import os
from datetime import datetime

from bs4 import BeautifulSoup
from django.conf import settings
from django.core import mail
from django.core.exceptions import ImproperlyConfigured
from django.core.mail import EmailMultiAlternatives
from django.db import models
from django.db.models.fields import CharField, EmailField
from django.template.defaultfilters import linebreaksbr
from django.template.loader import get_template
from django.utils.translation import gettext_lazy as _
try:
    from django_recaptcha.fields import ReCaptchaField
    from django_recaptcha import widgets
except ImportError:
    from captcha.fields import ReCaptchaField
    from captcha import widgets
from modelcluster.models import ParentalKey
from wagtail.admin.panels import (FieldPanel, FieldRowPanel, InlinePanel,
                                  MultiFieldPanel)
from wagtail.blocks import StreamBlock
from wagtail.contrib.forms.models import AbstractFormField
from wagtail.fields import RichTextField, StreamField
from wagtail.models import Locale, TranslatableMixin
from wagtailcaptcha.forms import WagtailCaptchaFormBuilder
from wagtailcaptcha.models import WagtailCaptchaEmailForm

from core.blocks import BasicRichTextBlock
from core.models import SEOPage
from site_settings.models import EmailSettings


class ContactFormBuilder(WagtailCaptchaFormBuilder):
    def __init__(
            self, 
            fields, 
            widget=None, 
            required_score=None, 
            action='form', 
            v2_attrs={}, 
            api_params={}, 
            keys={}, 
            **kwargs
            ):
        super().__init__(fields, **kwargs)
        self.recaptcha_widget = widget or getattr(settings, 'RECAPTCHA_WIDGET', False) or widgets.ReCaptchaV2Checkbox
        self.recaptcha_action = action
        self.required_score = required_score
        self.v2_attrs = v2_attrs
        self.api_params = api_params
        self.keys = keys

    @property
    def formfields(self):
        fields = super(WagtailCaptchaFormBuilder, self).formfields
        if widgets.__package__ == 'django_recaptcha':
            fields[self.CAPTCHA_FIELD_NAME] = ReCaptchaField(**self.field_attrs)
        else:
            fields[self.CAPTCHA_FIELD_NAME] = ReCaptchaField(label='')
        return fields

    @property
    def field_attrs(self):
        kwargs = {'widget': self.get_recaptcha_widget()}
        if self.keys:
            try:
                kwargs['public_key'] = self.keys.get('public_key')
                kwargs['private_key'] = self.keys.get('private_key')
            except:
                raise ImproperlyConfigured(
                    _("`keys` attribute must be a dictionary with `public_key` and `private_key` values."))
        return kwargs

    def get_recaptcha_widget(self):
        import inspect
        if isinstance(self.recaptcha_widget, str):
            self.recaptcha_widget = getattr(
                widgets, self.recaptcha_widget, None)
        if inspect.getmodule(self.recaptcha_widget) != widgets:
            from django.core.exceptions import ImproperlyConfigured
            raise ImproperlyConfigured(
                _("Unsupported widget type. Please select widget from `django_recaptcha.widgets`."))

        recaptcha_kwargs = {}
        if self.recaptcha_widget == widgets.ReCaptchaV3:
            recaptcha_kwargs['action'] = self.recaptcha_action
            if self.required_score:
                recaptcha_kwargs['attrs'] = {
                    'required_score': self.required_score}
        else:
            if self.v2_attrs:
                recaptcha_kwargs['attrs'] = self.v2_attrs
        if self.api_params:
            recaptcha_kwargs['api_params'] = self.api_params

        return self.recaptcha_widget(**recaptcha_kwargs)


class CustomAbstractFormField(AbstractFormField):
    FORM_FIELD_CHOICES = (
        ('singleline', _('Single line text')),
        ('multiline', _('Multi-line text')),
        ('email', _('Email')),
        ('url', _('URL')),
        ('checkbox', _('Checkbox')),
    )

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
        on_delete=models.CASCADE,
        related_name='form_fields',
    )

    class Meta:
        ordering = ["sort_order"]
        unique_together = ('translation_key', 'locale')


class IntroStreamBlock(StreamBlock):
    text = BasicRichTextBlock()


class ContactPage(WagtailCaptchaEmailForm, SEOPage):
    form_builder = ContactFormBuilder
    recaptcha_attrs = {
        'required_score': 0.8,
        'action': 'contact',
    }
    template = "contact/contact_page.html"
    landing_page_template = "contact/contact_page_landing.html"
    subpage_types = []
    max_count = 1

    def get_form_class(self):
        attrs = getattr(self, 'recaptcha_attrs', {})
        fb = self.form_builder(self.get_form_fields(), **attrs)
        return fb.get_form_class()

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
    privacy_notice = RichTextField(
        editor='basic',
        verbose_name=_("Privacy Notice in Left Column")
    )
    thank_you_text = RichTextField(
        editor='basic',
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
    send_error_text = RichTextField(
        editor='basic',
        verbose_name=_("Error Message to Display On Website After Email Failure")
    )
    send_error = models.BooleanField(default=False, null=True, blank=True)
    to_address = models.CharField(
        max_length=255,
        verbose_name=_('To Address'),
        help_text=_("Address to send form submissions to. Separate multiple addresses by comma.")
    )
    from_address = models.CharField(
        max_length=255,
        verbose_name=_('From Address'),
        help_text=_(
                "Address to send emails from. Account in email settings must have rights to use this address."
            )
    )
    subject = models.CharField(
        max_length=255,
        verbose_name=_('subject'),
        help_text=_(
                "Subject Line for Notification Email. Will be suffixed by Date/Time."
            )
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
        InlinePanel("form_fields", label="Form Fields"),
        FieldPanel("submit_button_text"),
        FieldPanel("form_error_warning"),
        FieldPanel("send_error_text"),
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

    @property
    def mail_settings(self):
        email_settings = EmailSettings.objects.first()
        use_ssl = getattr(email_settings, 'use_ssl')
        return {
            'host': getattr(email_settings, 'host'),
            'port': getattr(email_settings, 'port'),
            'username': getattr(email_settings, 'username'),
            'password': getattr(email_settings, 'password'),
            'ssl_setting': use_ssl,
            'tls_setting': not use_ssl
        }

    def is_spam(self, form):
        from site_settings.models import SpamSettings
        check = SpamSettings.objects.first()
        banned_domains = check.banned_domains.lower().splitlines()
        if any(email.split('@')[1] in banned_domains for email in form.cleaned_data['email_address'].lower().split(',')):
            return True
        banned_phrases = check.banned_phrases.lower().splitlines()
        if any(phrase in form.cleaned_data['message'].lower() for phrase in banned_phrases):
            return True
        return False

    def get_notification_email(self, form):
        email = {}
        email['addresses'] = [x.strip() for x in self.to_address.split(',')]
        email['content'] = []
        for field in form:
            if str(field).find('type="email"') != -1:
                email['contact_email_address'] = field.value()
            value = field.value()
            if isinstance(value, list):
                value = ', '.join(value)
            email['content'].append(
                '<p><strong>{}:</strong><br> {}</p>'.format(field.label, linebreaksbr(value))
            )
        submitted_date_str = datetime.now().strftime('%d-%m-%Y %H:%M:%S')
        email['content'].append(
            '<hr><br>Submitted {} via {}'.format(
                submitted_date_str, self.full_url
            )
        )
        email['content'] = ''.join(email['content'])
        email['subject'] = self.subject + " - " + submitted_date_str
        return email

    def get_receipt_email_html(self):
        locale_footer = self.receipt_email_footer.localized
        template = get_template(os.path.join(
            settings.PROJECT_DIR, 'templates', 'contact', 'receipt_email', 'base.html'
            )
        )
        html = template.render(
            {
                'body': self, 
                'footer': locale_footer, 
                'base_url': settings.WAGTAILADMIN_BASE_URL
            }
        )
    #   Enable next 3 lines to test html output
    #     output = os.path.join(settings.PROJECT_DIR, 'templates', 'contact','receipt_email', 'test.html')
    #     with open(output, 'w') as f:
    #         f.write(html)
        return html

    def get_receipt_email(self, contact_email_address):
        email = {}
        email['addresses'] = [
            x.strip() for x in contact_email_address.split(',')
        ]
        email['subject'] = self.receipt_email_subject
        email['content'] = self.get_receipt_email_html()
        return email

    def html_email(self, email):
        html_content = email['content']
        text_content = BeautifulSoup(
                html_content, features="html5lib"
            ).get_text().replace('\n', chr(10) + chr(10))
        html_email = EmailMultiAlternatives(
            subject=email['subject'],
            body=text_content,
            from_email=self.from_address,
            to=email['addresses'],
        )
        html_email.attach_alternative(html_content, "text/html")
        return html_email

    def send_mail(self, form):
        try:
            notification_email = self.get_notification_email(form)
            receipt_email = self.html_email(
                self.get_receipt_email(
                    notification_email['contact_email_address']
                )
            )
            receipt_email.reply_to = [
                x.strip() for x in self.reply_to.split(',')
            ]
            notification_email = self.html_email(notification_email)
            connection = mail.get_connection(**self.mail_settings)
            connection.send_messages([notification_email, receipt_email])
            connection.close()
        except:
            self.send_error = True

    def process_form_submission(self, form):
        if not self.is_spam(form):
            return super().process_form_submission(form)
