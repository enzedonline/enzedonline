from django import forms
from django.db import models
from django.utils.translation import gettext_lazy as _
from modelcluster.fields import ParentalKey
from modelcluster.models import ClusterableModel
from wagtail.admin.edit_handlers import (FieldPanel, InlinePanel, MultiFieldPanel, FieldRowPanel)
from wagtail.contrib.settings.models import BaseSetting, register_setting
from wagtail.core.models import Orderable, TranslatableMixin
from wagtail.images.edit_handlers import ImageChooserPanel
from wagtail.snippets.models import register_snippet
from wagtail_localize.fields import TranslatableField
from core.edit_handlers import RegexPanel

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
        verbose_name=_("Signature Name"),
        help_text=_("Used to identify this signature")
    )
    signature_heading = models.CharField(
        max_length=50,
        null=False,
        blank=False,
        verbose_name=_("Heading"),
        help_text=_("Company/Organisation name or other heading.")
    )
    signature_sub_heading = models.TextField(
        null=True,
        blank=True,
        verbose_name=_("Sub Heading"),
        help_text=_("Optional sub heading such as address, motto, department, title etc.")
    )
    signature_heading_link = models.URLField(
        max_length=200,
        null=True,
        blank=True,
        verbose_name=_("Heading Link"),
        help_text=_("Optional hyperlink address for heading.")
    )
    address = models.TextField(
        null=True,
        blank=True,
        verbose_name=_("Address"),
        help_text=_("Optional"),
    )
    map_link = models.URLField(
        null=True,
        blank=True,
        verbose_name=_("Map Link"),
        help_text=_("Option link to online map (eg Google Maps)")
    )
    map_icon = models.ForeignKey(
        'wagtailimages.Image',
        blank=True,
        null=True,
        related_name='+',
        on_delete=models.SET_NULL,
        verbose_name=_("Map Icon"),
        help_text=_("Optional icon displayed alongside address @ 15x15px")
    )
    signature_image = models.ForeignKey(
        'wagtailimages.Image',
        blank=True,
        null=True,
        related_name='+',
        on_delete=models.SET_NULL,
        verbose_name=_("Signature Image"),
        help_text=_("Optional image to display in Email Signature @ 64x64px")
    )
    contact_email_label = models.CharField(
        max_length=80,
        default=_("Email:"),
        verbose_name=_("Contact Email Label"),
        help_text=_("Label for email address displayed in footer.")
    )
    contact_email_address = models.EmailField(
        max_length=80,
        verbose_name=_("Contact Email Address"),
        help_text=_("Email address displayed in footer.")
    )
    email_icon = models.ForeignKey(
        'wagtailimages.Image',
        blank=True,
        null=True,
        related_name='+',
        on_delete=models.SET_NULL,
        verbose_name=_("Email Icon"),
        help_text=_("Optional icon displayed alongside email address @ 15x15px")
    )
    contact_phone_label = models.CharField(
        max_length=80,
        default=_("Phone:"),
        verbose_name=_("Contact Phone Label"),
        help_text=_("Label for phone number displayed in footer.")
    )
    contact_phone_number = models.CharField(
        max_length=80,
        verbose_name=_("Contact Phone Number"),
        help_text=_("Phone number displayed in footer.")
    )
    phone_icon = models.ForeignKey(
        'wagtailimages.Image',
        blank=True,
        null=True,
        related_name='+',
        on_delete=models.SET_NULL,
        verbose_name=_("Phone Icon"),
        help_text=_("Optional icon displayed alongside phone number @ 15x15px")
    )

    panels = [
        FieldPanel('signature_name'),
        MultiFieldPanel([
            FieldPanel('signature_heading'),
            FieldPanel('signature_sub_heading'),
            FieldPanel('signature_heading_link'),
        ], heading=_("Heading Settings")),
        MultiFieldPanel([
            FieldPanel('address'),
            FieldPanel('map_link'),
            ImageChooserPanel('map_icon'),
        ], heading=_("Address Settings")),
        ImageChooserPanel('signature_image'),
        MultiFieldPanel([
            FieldRowPanel([
                FieldPanel("contact_email_label", classname='col-6'),
                FieldPanel("contact_email_address", classname='col-6'),
            ]),
            ImageChooserPanel("email_icon"),
        ], heading=_("Contact Email Settings")),
        MultiFieldPanel([
            FieldRowPanel([
                FieldPanel("contact_phone_label", classname='col-6'),
                FieldPanel("contact_phone_number", classname='col-6'),
            ]),
            ImageChooserPanel("phone_icon"),
        ], heading=_("Contact Phone Settings")),
    ]

    def __str__(self):
        """The string representation of this class"""
        return self.signature_name

    class Meta:
        verbose_name = _('Email Signature')
        verbose_name_plural = _('Email Signatures')
        unique_together = ('translation_key', 'locale')

@register_snippet
class TemplateText(TranslatableMixin, ClusterableModel):
    template_set = models.CharField(
        unique=True,
        max_length=50,
        verbose_name="Set Name",
        help_text=_("The set needs to be loaded in template tags then text references as {{set.tag}}")
    )    

    translatable_fields = []
    
    panels = [
        FieldPanel("template_set"),
        MultiFieldPanel(
            [
                InlinePanel("templatetext_items"),
            ],
            heading=_("Text Items"),
        ),
    ]

    # base_form_class = TemplateTextForm

    def __str__(self):
        return self.template_set
    
    class Meta:
        verbose_name = _('Template Text')
        unique_together = ('translation_key', 'locale')

class TemplateTextSetItem(TranslatableMixin, Orderable):
    set = ParentalKey(
        "TemplateText",
        related_name="templatetext_items",
        help_text=_("Template Set to which this item belongs."),
        verbose_name="Set Name",
    )
    template_tag = models.SlugField(
        max_length=50,
        help_text=_("Enter a tag without spaces, consisting of letters, numbers, underscores or hyphens."),
        verbose_name="Template Tag",
    )    
    text = models.TextField(
        null=True,
        blank=True,
        help_text=_("The text to be inserted in the template.")
    )

    translatable_fields = [
        TranslatableField('text'),
    ]

    panels = [
        RegexPanel('template_tag', '^[-\w]+$'),
        FieldPanel('text'),
    ]

    def __str__(self):
        return self.template_tag

    class Meta:
        unique_together = ('set', 'template_tag'), ('translation_key', 'locale')

@register_snippet
class CompanyLogo(TranslatableMixin, models.Model):
    name = models.CharField(max_length=250)
    logo = models.ForeignKey(
        "wagtailimages.Image", on_delete=models.CASCADE, related_name="+"
    )

    panels = [
        FieldPanel("name", classname="full"),
        ImageChooserPanel("logo"),
    ]

    def __str__(self):
        return self.name
