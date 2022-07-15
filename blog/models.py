import six
from allauth.account.forms import LoginForm
from core.blocks import GridStreamBlock
from core.models import SEOPage
from core.utils import paginator_range
from django import forms
from django.conf import settings
from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator
from django.db import models
from django.template import loader
from django.urls import reverse
from django.utils.translation import gettext_lazy as _
from django_comments_xtd import signed
from django_comments_xtd.models import XtdComment
from django_comments_xtd.utils import send_mail
from django_extensions.db.fields import AutoSlugField
from modelcluster.contrib.taggit import ClusterTaggableManager
from modelcluster.fields import ParentalManyToManyField
from modelcluster.models import ParentalKey
from taggit.models import Tag, TaggedItemBase
from userauth.models import CustomUser
from wagtail.admin.panels import FieldPanel, InlinePanel, MultiFieldPanel
from wagtail.fields import StreamField
from wagtail.models import TranslatableMixin
from wagtail.search import index
from wagtail.snippets.models import register_snippet
from core.utils import purge_blog_list_cache_fragments

@register_snippet
class TechBlogCategory(TranslatableMixin, models.Model):
    name = models.CharField(max_length=200, verbose_name=_("Category Name"))
    slug = AutoSlugField(
        populate_from=['name'],
        verbose_name='slug',
        allow_unicode=True,
        max_length=200,
    )

    panels = [
        FieldPanel('name'),
    ]

    class Meta:
        verbose_name = _("Tech Blog Category")
        verbose_name_plural = _("Tech Blog Categories")
        ordering = ['name']
        unique_together = ('translation_key', 'locale')
    
    def __str__(self):
        return self.name

@register_snippet
class PersonalBlogCategory(TranslatableMixin, models.Model):
    name = models.CharField(max_length=200, verbose_name=_("Category Name"))
    slug = AutoSlugField(
        populate_from=['name'],
        verbose_name='slug',
        allow_unicode=True,
        max_length=200,
    )

    panels = [
        FieldPanel('name'),
    ]

    class Meta:
        verbose_name = _("Personal Blog Category")
        verbose_name_plural = _("Personal Blog Categories")
        ordering = ['name']
        unique_together = ('translation_key', 'locale')
    
    def __str__(self):
        return self.name

class TechBlogPageTag(TaggedItemBase):
    content_object = ParentalKey(
        'TechBlogDetailPage',
        related_name='tagged_items',
        on_delete=models.CASCADE,
    )

class PersonalBlogPageTag(TaggedItemBase):
    content_object = ParentalKey(
        'PersonalBlogDetailPage',
        related_name='tagged_items',
        on_delete=models.CASCADE,
    )

class BlogDetailPage(SEOPage):
    subpage_types = []
    parent_page_types = []

    body = StreamField(
        GridStreamBlock(), verbose_name=_("Page body"), blank=True, use_json_field=True
    )

    content_panels = SEOPage.content_panels + [
        FieldPanel('body'),
        InlinePanel('customcomments', label=_("Comments")),    
    ]

    search_fields = SEOPage.search_fields + [
        index.SearchField('body'),
    ]

    class Meta:
        verbose_name = _("Blog Page")
        # abstract = True

    def get_absolute_url(self):
        return self.get_url()

    def get_context(self, request, *args, **kwargs):
        context = super().get_context(request, *args, **kwargs)
        siblings = self.__class__.objects.sibling_of(self).live()
        category_filter = request.GET.get('category', None)
        tag_filter = request.GET.get('tag', None)
        
        # if category_filter:
        #     siblings = siblings.filter(categories__slug__in=category_filter.split(','))
        #     context['filter'] = '?category=' + category_filter
        #     context['showing'] = 'Showing blogs in ' + category_filter + ' category.'
        # elif tag_filter:
        #     siblings = siblings.filter(tags__slug__in=tag_filter.split(','))
        #     context['filter'] = '?tag=' + tag_filter
        #     context['showing'] = 'Showing blogs tagged with ' + tag_filter + '.'
        # else:
        #     context['filter'] = ''
        #     context['showing'] = None

        filter = {'qstring': ''}

        if category_filter:
            siblings = siblings.filter(categories__slug__in=category_filter.split(','))
            filter['qstring'] = '?category=' + category_filter
        elif tag_filter:
            siblings = siblings.filter(tags__slug__in=tag_filter.split(','))
            filter['qstring'] = '?tag=' + tag_filter

        context['filter'] = filter

        context['next_post'] = siblings.filter(path__gt=self.path).first()
        context['previous_post'] = siblings.filter(path__lt=self.path).last()

        return context

    def save(self, *args, **kwargs):
        purge_blog_list_cache_fragments()
        super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        purge_blog_list_cache_fragments()
        super().delete(*args, **kwargs)

    def serve(self, request, *args, **kwargs):
        response = super().serve(request, 'blog/blog_page.html')
        response.context_data['login_form'] = LoginForm()
        return response

    def blog_type(self):
        return self.__class__.__name__

class TechBlogDetailPage(BlogDetailPage):
    template = 'blog/blog_page.html'
    parent_page_types = ['blog.TechBlogListingPage']

    categories = ParentalManyToManyField(
        'blog.TechBlogCategory',
        verbose_name=_("Blog Categories")
    )
    tags = ClusterTaggableManager(through=TechBlogPageTag, blank=True)

    content_panels = BlogDetailPage.content_panels + [
        MultiFieldPanel(
            [
                FieldPanel(
                    'categories',
                    widget = forms.CheckboxSelectMultiple,
                ),
            ],
            heading = "Blog Categories",
        ),
        FieldPanel('tags'),
    ]

    class Meta:
        verbose_name = _("Tech Blog Page")

class PersonalBlogDetailPage(BlogDetailPage):
    template = 'blog/blog_page.html'
    parent_page_types = ['blog.PersonalBlogListingPage']

    categories = ParentalManyToManyField(
        'blog.PersonalBlogCategory',
        verbose_name=_("Blog Categories")
    )
    tags = ClusterTaggableManager(through=PersonalBlogPageTag, blank=True)

    content_panels = BlogDetailPage.content_panels + [
        MultiFieldPanel(
            [
                FieldPanel(
                    'categories',
                    widget = forms.CheckboxSelectMultiple,
                ),
            ],
            heading = _("Blog Categories"),
        ),
        FieldPanel('tags'),
    ]

    class Meta:
        verbose_name = _("Personal Blog Page")

class CustomComment(XtdComment):
    page = ParentalKey(BlogDetailPage, on_delete=models.CASCADE, related_name='customcomments')

    def save(self, *args, **kwargs):
        if self.user:
            self.user_name = self.user.display_name
        self.page = BlogDetailPage.objects.get(pk=self.object_pk)
        self.notify_author()
        super(CustomComment, self).save(*args, **kwargs)

    def notify_author(self):
        try:
            author = CustomUser.objects.get(id=self.page.owner_id)
        except CustomUser.DoesNotExist:
            return
        if not self.user_email == author.email:
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
                    html_message = html_message_template.render(message_context)
                else:
                    html_message = None
                send_mail(subject, text_message, settings.COMMENTS_XTD_FROM_EMAIL,
                        [email, ], html=html_message)

class BlogListingPage(SEOPage):
    parent_page_types = ['home.HomePage']

    banner_image = models.ForeignKey(
        'wagtailimages.Image',
        blank=False,
        null=True,
        related_name='+',
        on_delete=models.SET_NULL,
        verbose_name=_("Banner Image")
    )
    banner_headline = models.CharField(
        max_length=30,
        blank=True,
        null=True,
        verbose_name=_("Banner Headline")
    )
    banner_small_text = models.CharField(
        max_length=60,
        blank=True,
        null=True,
        verbose_name=_("Banner Small Text")
    )

    top_section = StreamField(
        GridStreamBlock(), 
        verbose_name=_("Content to go above the index"), 
        blank=True, 
        use_json_field=True
    )
    bottom_section = StreamField(
        GridStreamBlock(), 
        verbose_name=_("Content to go below the index"), 
        blank=True, 
        use_json_field=True
    )

    content_panels = SEOPage.content_panels + [
        MultiFieldPanel(
            [
                FieldPanel('banner_image'),
                FieldPanel('banner_headline'),
                FieldPanel('banner_small_text'),
            ], 
            heading=_("Choose banner image and text/button overlay options.")
        ),
        FieldPanel('top_section'),
        FieldPanel('bottom_section'),
    ]

    class Meta:
        abstract = True

    @property
    def get_child_pages(self):
        return self.get_children().public().live()

    def get_context(self, request, *args, **kwargs):
        """Adds custom fields to the context"""

        index_type = self.__class__
        context = super().get_context(request, *args, **kwargs)
        
        if index_type == TechBlogListingPage:
            all_posts = TechBlogDetailPage.objects.child_of(self).live().public().reverse()
            categories = TechBlogCategory.objects.all()
            tags = Tag.objects.all().filter(id__in=TechBlogPageTag.objects.all().values_list('tag_id', flat=True))
        else:
            all_posts = PersonalBlogDetailPage.objects.child_of(self).live().public().reverse()
            categories = PersonalBlogCategory.objects.all()
            tags = Tag.objects.all().filter(id__in=PersonalBlogPageTag.objects.all().values_list('tag_id', flat=True))

        category_filter = request.GET.get('category', None)
        tag_filter = request.GET.get('tag', None)

        filter = {'type': '', 'name': '', 'qstring': '', 'verbose': ''}

        if category_filter:
            all_posts = all_posts.filter(categories__slug__in=category_filter.split(','))
            filter['type'] = 'category'
            filter['name'] = category_filter
            filter['qstring'] = '?category=' + category_filter
            filter['verbose'] = categories.filter(slug=category_filter).first().name
        elif tag_filter:
            all_posts = all_posts.filter(tags__slug__in=tag_filter.split(','))
            filter['type'] = 'tag'
            filter['name'] = tag_filter
            filter['qstring'] = '?tag=' + tag_filter
            filter['verbose'] = tags.filter(slug=tag_filter).first().name 

        context['filter'] = filter
        
        paginator = Paginator(all_posts, 12)

        requested_page = request.GET.get('page')

        try:
            posts = paginator.page(requested_page)
        except PageNotAnInteger:
            posts = paginator.page(1)
        except EmptyPage:
            posts = paginator.page(paginator.num_pages)
        
        context['posts'] = posts
        context['categories'] = categories
        context['tags'] = tags
        context['category_filter'] = category_filter
        context['tag_filter'] = tag_filter
        context['page_range'] = paginator_range(
            requested_page=posts.number,
            last_page_num=paginator.num_pages,
            wing_size=4
        )
        # Next two are needed as Django templates don't support accessing range properties
        context['page_range_first'] = context['page_range'][0]
        context['page_range_last'] = context['page_range'][-1]

        return context

class TechBlogListingPage(BlogListingPage):
    template = 'blog/blog_index_page.html'
    subpage_types = ['blog.TechBlogDetailPage',]
    max_count = 1

class PersonalBlogListingPage(BlogListingPage):
    template = 'blog/blog_index_page.html'
    subpage_types = ['blog.PersonalBlogDetailPage',]
    max_count = 1


