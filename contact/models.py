import logging
import os
from datetime import datetime
from email.policy import default

from django.conf import settings
from django.core.exceptions import ImproperlyConfigured
from django.db import models
from django.db.models.fields import CharField, EmailField
from django.template.defaultfilters import linebreaksbr
from django.template.loader import get_template
from django.utils.translation import gettext_lazy as _
from django_recaptcha import widgets
from django_recaptcha.fields import ReCaptchaField
from htmlmin import minify
from modelcluster.models import ParentalKey
from wagtail.admin.panels import (FieldPanel, FieldRowPanel, InlinePanel,
                                  MultiFieldPanel)
from wagtail.contrib.forms.models import AbstractFormField
from wagtail.fields import RichTextField
from wagtail.models import TranslatableMixin
from wagtailcaptcha.forms import WagtailCaptchaFormBuilder
from wagtailcaptcha.models import WagtailCaptchaEmailForm

from core.mail.message import GmailMessage
from core.models import SEOPage
from site_settings.models import SpamSettings


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
        self.recaptcha_widget = widget or getattr(
            settings, 'RECAPTCHA_WIDGET', False) or widgets.ReCaptchaV2Checkbox
        self.recaptcha_action = action
        self.required_score = required_score
        self.v2_attrs = v2_attrs
        self.api_params = api_params
        self.keys = keys

    @property
    def formfields(self):
        fields = super(WagtailCaptchaFormBuilder, self).formfields
        if widgets.__package__ == 'django_recaptcha':
            fields[self.CAPTCHA_FIELD_NAME] = ReCaptchaField(
                **self.field_attrs)
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

class ContactPage(WagtailCaptchaEmailForm, SEOPage):
    form_builder = ContactFormBuilder
    recaptcha_attrs = {
        'required_score': 0.7,
        'action': 'contact',
    }
    template = "contact/contact_page.html"
    landing_page_template = "contact/contact_page_landing.html"
    subpage_types = []
    max_count = 2

    def get_form_class(self):
        attrs = getattr(self, 'recaptcha_attrs', {})
        fb = self.form_builder(self.get_form_fields(), **attrs)
        return fb.get_form_class()

    introduction = RichTextField(
        editor='basic',
        verbose_name=_("Introduction")
    )
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
        verbose_name=_(
            "Acknowledgement Text to Display On Website After Submit")
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
        help_text=_(
            "Text to display above the form in case there was a problem")
    )
    send_error_text = RichTextField(
        editor='basic',
        verbose_name=_(
            "Error Message to Display On Website After Email Failure")
    )
    send_error = models.BooleanField(default=False, null=True, blank=True)
    to_address = models.CharField(
        max_length=255,
        verbose_name=_('To Address'),
        help_text=_(
            "Address to send form submissions to. Separate multiple addresses by comma.")
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
        FieldPanel('introduction'),
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

    def is_spam(self, form):
        check = SpamSettings.load()
        banned_domains = check.banned_domains.lower().splitlines()
        if any(email.split('@')[1] in banned_domains for email in form.cleaned_data['email_address'].lower().split(',')):
            return True
        banned_phrases = check.banned_phrases.lower().splitlines()
        if any(phrase in form.cleaned_data['message'].lower() for phrase in banned_phrases):
            return True
        return False

    def get_notification_email(self, form):
        submitted_date_str = datetime.now().strftime('%d-%m-%Y %H:%M:%S')
        content = []
        for field in form:
            value = field.value()
            if isinstance(value, list):
                value = ', '.join(value)
            content.append(
                f'<p><strong>{field.label}:</strong><br> {linebreaksbr(value)}</p>'
            )
        content.append(
            f'<hr><br>Submitted {submitted_date_str} via {self.full_url}'
        )
        content = ''.join(content)
        return GmailMessage(
            from_email=self.from_address,
            to=[x.strip() for x in self.to_address.split(',')],
            subject=self.subject + " - " + submitted_date_str,
            html_body=content
        )

    def get_receipt_email_html(self):
        locale_footer = self.receipt_email_footer.localized
        template = get_template('contact/receipt-email.html')
        html = template.render(
            {
                'body': {
                    'receipt_email_headline': self.receipt_email_headline,
                    'receipt_email_content': self.receipt_email_content,
                },
                'heading_image': self.receipt_email_banner,
                'footer': locale_footer,
                'base_url': settings.WAGTAILADMIN_BASE_URL
            }
        )
        html = minify(''.join(html).replace('\n', ''))
        #   Enable next 3 lines to test html output
        # output = os.path.join(settings.BASE_DIR, 'contact', 'templates',
        #                       'contact', 'test.html')
        # with open(output, 'w') as f:
        #     f.write(html)
        return html

    def get_receipt_email(self, form):
        return GmailMessage(
            from_email=self.from_address,
            reply_to=[x.strip() for x in self.reply_to.split(',')],
            to=[x.strip() for x in form.cleaned_data['email_address'].split(',')],
            subject=self.receipt_email_subject,
            html_body=self.get_receipt_email_html()
        )

    def send_mail(self, form):
        try:
            notification_email = self.get_notification_email(form)
            result = notification_email.send()
            self.send_error = (result != 1)
        except Exception as e:
            self.send_error = True
            logging.warning(
                f"{type(e).__name__} at line {e.__traceback__.tb_lineno} of {__file__}: {e}"
            )

        if not self.send_error:
            receipt_email = self.get_receipt_email(form)
            receipt_email.send(fail_silently=True, wait_for_completion=False)

    def process_form_submission(self, form):
        if not self.is_spam(form):
            return super().process_form_submission(form)
