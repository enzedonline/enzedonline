from django.db import models
from django.utils.translation import gettext_lazy as _
from wagtail.admin.panels import FieldPanel, MultiFieldPanel
from wagtail.fields import StreamField
from wagtail.search import index

from blocks.models import DocumentBlock, HeadingBlock, TableOfContentsBlock
from blocks.streamblocks.columns import FullWidthBaseBlock, TwoColumnBaseBlock
from blocks.streamblocks.simple import SimpleStreamBlock
from core.models import SEOPage


class ServiceColumnStreamBlock(SimpleStreamBlock):
    document = DocumentBlock()

class ServiceStreamBlock(ServiceColumnStreamBlock):
    heading = HeadingBlock()
    toc = TableOfContentsBlock()

class FullWidthServiceBlock(FullWidthBaseBlock):
    column = ServiceStreamBlock(
        label=_("Single Column Contents"),
        blank=True,
        Null=True
    )

class TwoColumnServiceBlock(TwoColumnBaseBlock):
    left_column = ServiceColumnStreamBlock(
        label=_("Left Column Contents"),
        blank=True,
        Null=True
    )
    right_column = ServiceColumnStreamBlock(
        label=_("Right Column Contents"),
        blank=True,
        Null=True
    )

class ServicePage(SEOPage):

    parent_page_types = ["home.HomePage", "goneforawander.GFWHomePage"]
    subpage_types = []
    max_count = 8

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

    body = StreamField([
            ('single_column', FullWidthServiceBlock()),
            ('two_column', TwoColumnServiceBlock()),
        ], 
        verbose_name="Page body", blank=True, use_json_field=True
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
        FieldPanel("body"),
    ]

    search_fields = SEOPage.search_fields + [
        index.SearchField('body'),
    ]

    class Meta:
        verbose_name = "Service Page"

