import os
from datetime import datetime

from bs4 import BeautifulSoup
from core.blocks import HtmlBlock, SimpleRichTextBlock, SpacerStaticBlock
from core.models import SEOPage, SEOWagtailCaptchaEmailForm
from django.conf import settings
from django.core import mail
from django.core.mail import EmailMultiAlternatives
from django.db import models
from django.db.models.fields import CharField, EmailField
from django.template.defaultfilters import linebreaksbr
from django.template.loader import get_template
from django.utils.translation import gettext_lazy as _
from modelcluster.models import ParentalKey
from site_settings.models import EmailSettings
from wagtail.admin.panels import (FieldPanel, FieldRowPanel,
                                         InlinePanel, MultiFieldPanel)
from wagtail.contrib.forms.models import AbstractFormField
from wagtail.blocks import StreamBlock
from wagtail.fields import RichTextField, StreamField
from wagtail.models import TranslatableMixin

FORM_FIELD_CHOICES = (
    ('singleline', _('Single line text')),
    ('multiline', _('Multi-line text')),
    ('email', _('Email')),
    ('url', _('URL')),
    ('checkbox', _('Checkbox')),
)

class CustomAbstractFormField(AbstractFormField):
    field_type = models.CharField(
        verbose_name="Field Type",
        max_length=16,
        choices=FORM_FIELD_CHOICES,
    )

    class Meta:
        abstract = True
        ordering = ["sort_order"]

class FormField(TranslatableMixin, CustomAbstractFormField):
    page = ParentalKey(
        'ContactPage',
        on_delete = models.CASCADE,
        related_name = 'form_fields',
    )

    class Meta:
        ordering = ["sort_order"]
        unique_together = ('translation_key', 'locale')

class IntroStreamBlock(StreamBlock):
    text = SimpleRichTextBlock()
    html = HtmlBlock()
    spacer = SpacerStaticBlock()

class ContactPage(SEOWagtailCaptchaEmailForm):
    template = "contact/contact_page.html"
    landing_page_template = "contact/contact_page_landing.html"
    subpage_types = []
    max_count = 1

    intro_text = StreamField(IntroStreamBlock(), use_json_field=True)
    intro_image = models.ForeignKey(
        'wagtailimages.Image',
        blank=True,
        null=True,
        related_name='+',
        on_delete=models.SET_NULL,
        verbose_name=_("Introduction Image (optional)"),
        help_text=_("Image to display in left column on widescreen only")
    )
    privacy_notice = RichTextField(editor='basic',
        verbose_name=_("Privacy Notice in Left Column")
    )
    thank_you_text = RichTextField(editor='basic',
        verbose_name=_("Acknowledgement Text to Display On Website After Submit")
    )
    submit_button_text = CharField(
        default="Submit",
        max_length=20,
        verbose_name=_("Submit Button Text")
    )
    form_error_warning = CharField(
        default="There was a problem submitting the form. Please check below and try again.",
        max_length=150,
        verbose_name=_("Form Error Warning"),
        help_text=_("Text to display above the form in case there was a problem")
    )
    to_address = models.CharField(
        max_length=255,
        verbose_name=_('To Address'),
        help_text=_("Address to send form submissions to. Separate multiple addresses by comma.")
    )
    from_address = models.CharField(
        max_length=255,
        verbose_name=_('From Address'), 
        help_text=_("Address to send emails from. Account in email settings must have rights to use this address.")
    )
    subject = models.CharField(
        max_length=255, 
        verbose_name=_('subject'), 
        help_text=_("Subject Line for Notification Email. Will be suffixed by Date/Time.")
    )
    reply_to = EmailField(
        verbose_name=_("Reply-to Email Address"),
        help_text=_("Where to send replies made to the receipt email")
    )
    receipt_email_subject = CharField(
        max_length=150,
        verbose_name=_("Receipt Email Subject"),
        help_text=_("Subject for email sent to client")
    )
    receipt_email_banner = models.ForeignKey(
        'wagtailimages.Image',
        related_name='+',
        blank=False,
        null=True,
        on_delete=models.SET_NULL,
        verbose_name=_("Banner Image"),
        help_text=_("Image to display at top of email (letterbox format)")
    )
    receipt_email_banner_link = models.URLField(
        max_length=200,
        verbose_name=_("Receipt Email Subject"),
        help_text=_("Subject for email sent to client")
    )
    receipt_email_headline = CharField(
        max_length=150,
        verbose_name=_("Receipt Email Headline"),
        help_text=_("Large text header on receipt.")
    )
    receipt_email_content = RichTextField(
        editor='basic',
        verbose_name=_("Receipt Email Content"),
        help_text=_("Content for email sent to client")
    )
    receipt_email_footer = models.ForeignKey(
        'site_settings.EmailSignature',
        null=True,
        blank=False,
        on_delete=models.SET_NULL,
        related_name='+'
    )
    
    content_panels = SEOPage.content_panels + [
        FieldPanel('intro_text'),
        FieldPanel('intro_image'),
        FieldPanel("privacy_notice"),
        InlinePanel("form_fields", label = "Form Fields"),
        FieldPanel("submit_button_text"),
        FieldPanel("form_error_warning"),
        FieldPanel("thank_you_text"),
        MultiFieldPanel([
            FieldRowPanel([
                FieldPanel("from_address", classname='col-6'),
                FieldPanel("to_address", classname='col-6'),
            ]),
            FieldPanel("subject"),
        ], heading=_("Notification Email Settings")),
        MultiFieldPanel([
            FieldPanel("reply_to"),
            FieldPanel("receipt_email_banner"),
            FieldPanel("receipt_email_banner_link"),
            FieldPanel("receipt_email_subject"),
            FieldPanel("receipt_email_headline"),
            FieldPanel("receipt_email_content"),
            FieldPanel('receipt_email_footer'),
        ], heading=_("Client Receipt Email Settings")),
    ]

    def get_mail_backend(self):
        email_settings=EmailSettings.objects.first()
        host = getattr(email_settings, 'host')
        port = getattr(email_settings, 'port')
        username = getattr(email_settings, 'username')
        password = getattr(email_settings, 'password')
        use_tls = getattr(email_settings, 'use_tls')

        if use_tls:
            tls_setting = True
            ssl_setting = False
        else:
            ssl_setting = True
            tls_setting = False

        connection = mail.get_connection(
            host=host,
            port=port,
            username=username,
            password=password,
            use_tls=tls_setting,
            use_ssl=ssl_setting
        )
        return connection

    def get_notification_email(self, form):
        email={}
        email['addresses'] = [x.strip() for x in self.to_address.split(',')]
        email['content'] = []
        for field in form:
            if str(field).find('type="email"') != -1:
                email['contact_email_address'] = field.value()
            value = field.value()
            if isinstance(value, list):
                value = ', '.join(value)
            email['content'].append('<p><strong>{}:</strong><br> {}</p>'.format(field.label, linebreaksbr(value)))
        submitted_date_str = datetime.now().strftime('%d-%m-%Y %H:%M:%S')
        email['content'].append('<hr><br>Submitted {} via {}'.format(submitted_date_str, self.full_url))
        email['content'] = ''.join(email['content'])
        email['subject'] = self.subject + " - " + submitted_date_str
        return email

    def get_receipt_email_html(self):
        locale_footer = self.receipt_email_footer.localized
        template = get_template(os.path.join(settings.PROJECT_DIR, 'templates', 'contact','receipt_email', 'base.html'))
        html = template.render({'body': self, 'footer': locale_footer, 'base_url': settings.WAGTAILADMIN_BASE_URL})
    #   Enable next 3 lines to test html output
    #     output = os.path.join(settings.PROJECT_DIR, 'templates', 'contact','receipt_email', 'test.html')
    #     with open(output, 'w') as f:
    #         f.write(html)
        return html

    def get_receipt_email(self, contact_email_address):
        email={}
        email['addresses'] = [x.strip() for x in contact_email_address.split(',')]
        email['subject'] = self.receipt_email_subject
        email['content'] = self.get_receipt_email_html()
        return email

    def html_email(self, email):
        html_content = email['content']
        text_content = BeautifulSoup(html_content, features="html5lib").get_text().replace('\n', chr(10) + chr(10))
        html_email = EmailMultiAlternatives(
            subject=email['subject'], 
            body=text_content, 
            from_email=self.from_address, 
            to=email['addresses'],
        )
        html_email.attach_alternative(html_content, "text/html")
        return html_email

    def send_mail(self, form):
        notification_email = self.get_notification_email(form)
        receipt_email = self.html_email(self.get_receipt_email(notification_email['contact_email_address']))
        receipt_email.reply_to = [x.strip() for x in self.reply_to.split(',')]
        notification_email = self.html_email(notification_email)
        connection = self.get_mail_backend()      
        connection.send_messages([notification_email, receipt_email])
        connection.close()        

