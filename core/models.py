from django.conf import settings
from django.db import models
from django.utils.translation import gettext_lazy as _
from wagtail.admin.edit_handlers import FieldPanel, MultiFieldPanel
from wagtail.core.models import Page
from wagtail.images.edit_handlers import ImageChooserPanel
from wagtail.search import index
from wagtailcaptcha.models import WagtailCaptchaEmailForm
from wagtailmetadata.models import WagtailImageMetadataMixin

def get_image_model_string():
    try:
        image_model = settings.WAGTAILIMAGES_IMAGE_MODEL
    except AttributeError:
        image_model = 'wagtailimages.Image'
    return image_model

class SEOPageMixin(index.Indexed, WagtailImageMetadataMixin, models.Model):
    search_image = models.ForeignKey(
        get_image_model_string(),
        null=True,
        blank=False,
        related_name='+',
        on_delete=models.SET_NULL,
        verbose_name=_('Search Image'),
        help_text=_("The image to use on previews of this page on external links and search results. \
                     This will also be the image used for blog posts on the index pages.")
    )

    summary = models.TextField(
        null=False,
        blank=False,
        help_text=_("A summary of the page to be used on index pages. \
                     If Meta Description is left blank, this text will be used on search results and link previews.")
    )

    content_panels = Page.content_panels + [
        FieldPanel('summary'),
    ]
    
    promote_panels = [
        MultiFieldPanel([
            FieldPanel('slug'),
            FieldPanel('seo_title'),
            FieldPanel('search_description'),
            ImageChooserPanel('search_image'),
        ], _('Common page configuration')),
    ]

    def get_meta_url(self):
        return self.full_url

    def get_meta_title(self):
        return self.seo_title or self.title

    def get_meta_description(self):
        return self.search_description or self.summary

    def get_meta_image(self):
        return self.search_image

    class Meta:
        abstract = True

class SEOPage(SEOPageMixin, Page):

    search_fields = Page.search_fields + [
        index.SearchField('summary'),
    ]

    class Meta:
        abstract = True

class SEOWagtailCaptchaEmailForm(SEOPageMixin, WagtailCaptchaEmailForm):
    pass

    class Meta:
        abstract = True

