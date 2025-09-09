from django.db import models
from django.utils.translation import gettext_lazy as _
from wagtail.admin.panels import FieldPanel, MultiFieldPanel
from wagtail.fields import StreamField
from wagtail.search import index

from blocks.streamblocks.simple import SimpleStreamBlock
from core.models import SEOPage


class GFWHomePage(SEOPage):
    template = 'goneforawander/home/home_page.html'
    subpage_types = [
        "service.ServicePage", 
        "contact.ContactPage", 
        "goneforawander.MapIndexPage"
    ]
    max_count = 1

    banner_image = models.ForeignKey(
        'wagtailimages.Image',
        blank=False,
        null=True,
        related_name='+',
        on_delete=models.SET_NULL,
    )
    banner_headline = models.CharField(
        max_length=30,
        blank=True,
        null=True,
    )
    banner_small_text = models.CharField(
        max_length=60,
        blank=True,
        null=True,
    )
    banner_image_caption = models.CharField(
        max_length=60,
        blank=True,
        null=True,
    )

    body = StreamField(
        SimpleStreamBlock(), verbose_name="Page body", blank=True, use_json_field=True
    )

    content_panels = SEOPage.content_panels + [
        MultiFieldPanel(
            [
                FieldPanel('banner_image'),
                FieldPanel('banner_headline'),
                FieldPanel('banner_small_text'),
                FieldPanel('banner_image_caption'),
            ], 
            heading=_("Choose banner image and text/button overlay options.")
        ),
        FieldPanel("body"),
    ]

    search_fields = SEOPage.search_fields + [
        index.SearchField('body'),
    ]

    class Meta:
        verbose_name = "Home Page"

