from django.db import models
from django import forms
from django.utils.translation import gettext_lazy as _
from wagtail.admin.edit_handlers import FieldPanel, RichTextFieldPanel
from wagtail.contrib.settings.models import BaseSetting, register_setting
from wagtail.core.models import TranslatableMixin
from wagtail.images.edit_handlers import ImageChooserPanel
from wagtail.snippets.models import register_snippet
from wagtail.core.fields import RichTextField

class PasswordField(forms.CharField):
    widget = forms.PasswordInput

class PasswordModelField(models.CharField):

    def formfield(self, **kwargs):
        defaults = {'form_class': PasswordField}
        defaults.update(kwargs)
        return super(PasswordModelField, self).formfield(**defaults)

@register_setting(icon='mail')
class EmailSettings(BaseSetting):
    default_from_email = models.CharField(
        max_length=80,
        null=True,
        blank=False,
        verbose_name=_("Sending Email Address")
    )
    host = models.CharField(
        max_length=80,
        null=True,
        blank=False,
        verbose_name=_("Mail Server")
    )
    port = models.IntegerField(
        null=True,
        blank=False,
        verbose_name=_("Port")
    )
    username = models.CharField(
        max_length=50,
        null=True,
        blank=False,
        verbose_name=_("Username")
    )
    password = PasswordModelField(
        max_length=30,
        null=True,
        blank=False,
        verbose_name=_("Password"),
    )
    use_tls = models.BooleanField(
        default=False,
        verbose_name=_("Use TLS"),
        help_text=_("Use only TLS or SSL")
    )
    use_ssl = models.BooleanField(
        default=True,
        verbose_name=_("Use SSL"),
        help_text=_("Use only TLS or SSL")
    )

@register_setting(icon='fa-facebook')
class Facebook_Script_Src(BaseSetting):
    javascript_sdk = models.CharField(
        max_length=300,
        null=True,
        blank=False,
        verbose_name=_("Facebook Javascript SDK"),
        help_text=_("Copy in the code from Section 2 of the Javascript SDK tab in the 'Advanced Settings' embed page.")
    )
    class Meta:
        verbose_name = 'Facebook Javascript SDK'

@register_snippet
class SocialMedia(TranslatableMixin, models.Model):

    site_name = models.CharField(
        max_length=30,
        null=False,
        blank=False,
        help_text=_("Site Name")
    )
    url = models.URLField(
        max_length=100,
        null=False,
        blank=False,
        help_text=_("Profile URL")
    )
    photo = models.ForeignKey(
        "wagtailimages.Image",
        blank=False,
        null=True,
        on_delete=models.SET_NULL,
        related_name="+",
        help_text=_("Social Media Icon (displayed at 25x25)")
    )
 
    panels = [
        FieldPanel('site_name'),
        FieldPanel('url'),
        ImageChooserPanel('photo'),
    ]

    def __str__(self):
        """The string representation of this class"""
        return self.site_name

    class Meta:
        verbose_name = 'Social Media Link'
        verbose_name_plural = 'Social Media Links'
        unique_together = ('translation_key', 'locale')

@register_snippet
class EmailSignature(TranslatableMixin, models.Model):
    signature_name = models.CharField(
        max_length=30,
        null=False,
        blank=False,
        verbose_name=_("Email Signature Title"),
        help_text=_("Used to identify this signature")
    )
    signature_content = RichTextField(
        features= [
            'h1', 'h2', 'h3', 'h4', 'h5', 'h6',
            'bold',
            'italic',
            'ol',
            'ul',
            'link',
            'hr',
        ],
        verbose_name=_("Email Signature Content"),
        help_text=_("Text for the Email Signature")
    )
    signature_image = models.ForeignKey(
        'wagtailimages.Image',
        blank=True,
        null=True,
        related_name='+',
        on_delete=models.SET_NULL,
        verbose_name=_("Image for Left Column"),
        help_text=_("Image to display in left column of Email Signature")
    )

    panels = [
        FieldPanel('signature_name'),
        RichTextFieldPanel('signature_content'),
        ImageChooserPanel('signature_image'),
    ]

    def __str__(self):
        """The string representation of this class"""
        return self.signature_name

    class Meta:
        verbose_name = _('Email Signature')
        verbose_name_plural = _('Email Signatures')
        unique_together = ('translation_key', 'locale')
