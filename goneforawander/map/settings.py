from django.db import models
from django.utils.translation import gettext_lazy as _
from modelcluster.fields import ParentalKey
from modelcluster.models import ClusterableModel
from wagtail.admin.panels import FieldPanel, InlinePanel, MultiFieldPanel
from wagtail.contrib.settings.models import (BaseGenericSetting,
                                             register_setting)
from wagtail.fields import RichTextField
from wagtail.models import Orderable
from wagtail.snippets.models import register_snippet


@register_setting(icon='map')
class MapboxSettings(BaseGenericSetting):
    token = models.CharField(max_length=100, unique=True)
    api_version = models.CharField(max_length=100, unique=True)

@register_snippet
class MapboxAssistConfigs(ClusterableModel):
    title = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(max_length=100, unique=True)
    country_code = models.CharField(max_length=2, blank=True, null=True)
    extra_head = models.TextField(blank=True)
    help_panel_title = models.CharField(max_length=100, blank=True, null=True)
    help_panel_body = RichTextField(blank=True, null=True)

    panels = [
        FieldPanel("title"),
        FieldPanel("slug"),
        MultiFieldPanel(
            [
                InlinePanel(
                    "mapbox_styles",
                ),
            ],
            heading=_("Mapbox Styles"),
        ),
        MultiFieldPanel(
            [
                InlinePanel(
                    "feature_layers",
                ),
            ],
            heading=_("Feature Layers"),
        ),
        FieldPanel("extra_head"),
        FieldPanel("help_panel_title"),
        FieldPanel("help_panel_body"),
    ]

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = _("Mapbox Assist Configurations")
        verbose_name_plural = _("Mapbox Assist Configurations")


class MapboxStyle(Orderable):
    set = ParentalKey(
        "MapboxAssistConfigs",
        related_name="mapbox_styles",
        help_text=_("Define Mapbox styles. First item will load as default."),
        verbose_name="Mapbox Style",
    )
    title = models.CharField(max_length=100)
    source = models.CharField(max_length=255)
    tile_image = models.ForeignKey(
        "wagtailimages.Image",
        null=True,
        blank=False,
        related_name="+",
        on_delete=models.SET_NULL,
        verbose_name=_("Tile Image"),
    )

    panels = [
        FieldPanel("title"),
        FieldPanel("source"),
        FieldPanel("tile_image"),
    ]

    def __str__(self):
        return self.title

class MapboxAssistFeatureLayer(Orderable):
    set = ParentalKey(
        "MapboxAssistConfigs",
        related_name="feature_layers",
        help_text=_("Mapbox Assist settings to which this item belongs."),
        verbose_name="Feature Layer",
    )
    uid = models.CharField(max_length=100)
    tile_id = models.CharField(max_length=100)
    handler_function_name = models.CharField(max_length=100)
    handler_function_path = models.CharField(max_length=100)

    panels = [
        "uid",
        "tile_id",
        "handler_function_name",
        "handler_function_path",
    ]

    def __str__(self):
        return self.handler_function_name
