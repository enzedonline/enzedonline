from django.utils.translation import gettext_lazy as _
from django.db import models
# from django.core.cache import cache
# from django.core.cache.utils import make_template_fragment_key
from wagtail.core.fields import StreamField
from wagtail.admin.edit_handlers import FieldPanel, StreamFieldPanel, MultiFieldPanel
from wagtail.images.edit_handlers import ImageChooserPanel
from wagtail.search import index

from core.blocks import GridStreamBlock
from core.models import SEOPage

class ServicePage(SEOPage):

    parent_page_types = ["home.HomePage"]
    subpage_types = [
        "service.ServicePage", 
    ]
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

    body = StreamField(
        GridStreamBlock(), verbose_name="Page body", blank=True
    )

    content_panels = SEOPage.content_panels + [
        MultiFieldPanel(
            [
                ImageChooserPanel('banner_image'),
                FieldPanel('banner_headline'),
                FieldPanel('banner_small_text'),
            ], 
            heading=_("Choose banner image and text/button overlay options.")
        ),
        StreamFieldPanel("body"),
    ]

    search_fields = SEOPage.search_fields + [
        index.SearchField('body'),
    ]

    class Meta:
        verbose_name = "Service Page"

    # def flush_cache_fragments(self, fragment_keys):
    #     for fragment in fragment_keys:
    #         key = make_template_fragment_key(
    #             fragment,
    #             [self.id],
    #         )
    #         cache.delete(key)

    # def save(self, *args, **kwargs):
    #     self.flush_cache_fragments(["base", "head", "service_page", "main_menu", "banner_image", "footer"])
    #     return super().save(*args, **kwargs)

