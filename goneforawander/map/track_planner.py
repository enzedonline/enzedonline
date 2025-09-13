from django.db import models
from django.templatetags.static import static
from django.utils.translation import gettext_lazy as _
from wagtail.admin.panels import FieldPanel, MultiFieldPanel
from wagtail.fields import StreamField

from blocks.streamblocks.base import BaseStreamBlock
from core.models import SEOPage

from .settings import MapboxAssistConfigs, MapboxSettings


class TrackPlannerPage(SEOPage):
    parent_page_types = ['goneforawander.MapIndexPage']
    subpage_types = ['TrackPlannerHelpPage']
    max_count = 2
    template = 'map/track_planner_page.html'
    config = models.ForeignKey(
        MapboxAssistConfigs,
        null=True,
        blank=False,
        on_delete=models.SET_NULL,
        related_name="+",
        verbose_name=_("Map Configuration")
    )
    body = StreamField(
        BaseStreamBlock(), verbose_name=_("Page body"), blank=True, use_json_field=True
    )

    content_panels = SEOPage.content_panels + [
        FieldPanel('config'),
        FieldPanel('body'),
    ]

    def get_context(self, request, *args, **kwargs):
        """Adds custom fields to the context"""

        context = super().get_context(request, *args, **kwargs)
        mapbox_assist_config = self.config
        if not mapbox_assist_config:
            mapbox_assist_config = MapboxAssistConfigs.objects.first()

        feature_layers = []
        for layer in mapbox_assist_config.feature_layers.all():
            feature_layers.append({
                "id": layer.uid,
                "tileId": layer.tile_id,
                "handler": layer.handler_function_name,
                "source": static(layer.handler_function_path) if layer.handler_function_path.startswith('/') else layer.handler_function_path
            })

        map_styles = []
        for style in mapbox_assist_config.mapbox_styles.all():
            try:
                img = style.tile_image.get_rendition('fill-50x50').img_tag()
            except:
                img = ''
            map_styles.append({
                "title": style.title,
                "source": style.source,
                "tileImageHTML": img,
            })

        parameters = {
            "mapOptions": {
                "container": 'map',
                "style": map_styles[0]['source']
            },
            "showUserLocationOnLoad": True
        }

        settings = {
            "mapStyles": map_styles,
            "fitBounds": {"relativePadding": {"top": 5, "bottom": 10, "left": 5, "right": 5}},
            "loadSpritesheet": {
                "path": static("icons/mapbox-assist.svg"),
                "id": 'mapbox-assist--icons'
            },
            "route": {"form": {"show": True}, "enableUrlSharing": True},
            "search": {"show": True},
            "helpControl": {"show": True},
            "locationServices": {"showUserLocationControl": True},
        }

        if mapbox_assist_config.country_code:
            settings["limitToCountry"] = mapbox_assist_config.country_code

        context |= {
            "mapbox": MapboxSettings.load(request_or_site=request),
            "parameters": parameters,
            "mapboxAssistSettings": settings,
            "featureLayers": feature_layers,
            "help": {
                "title": mapbox_assist_config.help_panel_title,
                "body": mapbox_assist_config.help_panel_body
            }
        }

        if mapbox_assist_config.extra_head:
            context["extra_head"] = mapbox_assist_config.extra_head
        if mapbox_assist_config.extra_js:
            context["extra_js"] = mapbox_assist_config.extra_js

        return context

class TrackPlannerHelpPage(SEOPage):
    parent_page_types = ['goneforawander.TrackPlannerPage']
    subpage_types = []
    max_count = 2
    template = 'map/track_planner_help_page.html'
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
        BaseStreamBlock(), verbose_name="Page body", blank=True, use_json_field=True
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
        FieldPanel('body'),
    ]

    class Meta:
        verbose_name = _("Track Planner Help Page")
        verbose_name_plural = _("Track Planner Help Pages")    