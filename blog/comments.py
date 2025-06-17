import six
from django.conf import settings
from django.db import models
from django.template import loader
from django.urls import reverse
from django.utils.translation import gettext_lazy as _
from django_comments_xtd import signed
from django_comments_xtd.models import XtdComment
from django_comments_xtd.utils import send_mail
from modelcluster.models import ParentalKey
from userauth.models import CustomUser

from .detail_page import BlogDetailPage
        
class BlogAuthorCommentNotified(models.Model):
    comment_id = models.IntegerField()

    @classmethod
    def already_notified(cls, id):
        try:
            BlogAuthorCommentNotified.objects.get(comment_id=id)
            return True
        except BlogAuthorCommentNotified.DoesNotExist:
            return False            
        
class CustomComment(XtdComment):
    page = ParentalKey(BlogDetailPage, on_delete=models.CASCADE, related_name='customcomments')

    def save(self, *args, **kwargs):
        if self.user:
            self.user_name = self.user.display_name
        self.page = BlogDetailPage.objects.get(pk=self.object_pk)
        self.notify_author()
        super().save(*args, **kwargs)

    def notify_author(self):
        try:
            author = CustomUser.objects.get(id=self.page.owner_id) # type: ignore
        except CustomUser.DoesNotExist:
            return
        if not self.user_email == author.email and not BlogAuthorCommentNotified.already_notified(self.object_pk):
            followers = {}
            followers[author.email] = (
                self.user_name,
                signed.dumps(
                    self.comment, 
                    compress=True,
                    extra_key=settings.COMMENTS_XTD_SALT
                )
            )

            subject = _("New comment on your blog post")
            text_message_template = loader.get_template(
                'django_comments_xtd/email_followup_comment.txt')
            if settings.COMMENTS_XTD_SEND_HTML_EMAIL:
                html_message_template = loader.get_template(
                    'django_comments_xtd/email_followup_comment.html')

            for email, (name, key) in six.iteritems(followers):
                mute_url = reverse('comments-xtd-mute', args=[key.decode('utf-8')])
                message_context = {
                    'user_name': name,
                    'comment': self,
                    'mute_url': mute_url,
                    'site': self.site,
                    'author': True
                }
                text_message = text_message_template.render(message_context)
                if settings.COMMENTS_XTD_SEND_HTML_EMAIL:
                    try:
                        html_message = html_message_template.render(message_context) # type: ignore
                    except:
                        html_message = None
                else:
                    html_message = None
                send_mail(subject, text_message, settings.COMMENTS_XTD_FROM_EMAIL,
                        [email, ], html=html_message)
            BlogAuthorCommentNotified(comment_id=self.object_pk).save()
