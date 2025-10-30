from django import forms
from django.templatetags.static import static
from django.utils.functional import cached_property
from django.utils.safestring import mark_safe
from django.utils.translation import gettext_lazy as _
from wagtail.admin.telepath import register
from wagtail.blocks import (BooleanBlock, ChoiceBlock, StaticBlock,
                            StructBlock, URLBlock)
from wagtail.blocks.field_block import IntegerBlock
from wagtail.blocks.struct_block import StructBlockAdapter
from wagtail.snippets.blocks import SnippetChooserBlock

from goneforawander.map.settings import MapboxAssistConfigs, MapboxSettings


class RouteSummaryChoiceBlock(ChoiceBlock):
    choices=[
        ('', _("Not displayed")),
        ('simple', _("Summary only")),
        ('detailed', _("Detailed")),
    ]

class MapWaypointBlock(StructBlock):
    pass

class MapBlock(StructBlock):
    map_url = URLBlock(
        label=_("Map URL"),
    )
    config = SnippetChooserBlock(
        target_model=MapboxAssistConfigs
    )
    height = IntegerBlock(
        default=70, 
        min_value=20,
        label=_("Height (% of viewport)")
    )
    show_route_summary = RouteSummaryChoiceBlock(
        label=_("Show Route Summary"),
        required=False
    )
    show_map_link = BooleanBlock(
        label=_("Show Map Link"),
        required=False,
    )
    padding_top = IntegerBlock(
        default=5, 
        min_value=0, 
        label=_("Top Padding")
    )
    padding_bottom = IntegerBlock(
        default=5, 
        min_value=0, 
        label=_("Bottom Padding")
    )
    padding_left = IntegerBlock(
        default=5, 
        min_value=0, 
        label=_("Left Padding")
    )
    padding_right = IntegerBlock(
        default=5, 
        min_value=0, 
        label=_("Right Padding")
    )
    padding_help_text = _(
        "Padding left/right should be given as a percentage of the map dimension."
    )
    padding_help = StaticBlock(
        admin_text=mark_safe(f"<span class='help'>{padding_help_text}</span>")
    )

    def get_context(self, value, parent_context=None):
        """Adds custom fields to the context"""

        context = super().get_context(value, parent_context)
        mapbox_assist_config = value['config']

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
                "style": map_styles[0]['source']
            },
            "encodedURL": value['map_url'],
            "route": {
                "showSummary": value['show_route_summary'],
            }
        }

        settings = {
            "mapStyles": map_styles,
            "fitBounds": {
                "relativePadding": {
                    "top": value['padding_top'], 
                    "bottom": value['padding_bottom'],
                    "left": value['padding_left'],
                    "right": value['padding_right']
                }
            },
            "loadSpritesheet": {
                "path": static("icons/mapbox-assist.svg"),
                "id": 'mapbox-assist--icons'
            },
            "shareControl": {"show": False},
        }

        context |= {
            "mapbox": MapboxSettings.load(),
            "parameters": parameters,
            "mapboxAssistSettings": settings,
            "featureLayers": feature_layers
        }

        if mapbox_assist_config.extra_head:
            context["extra_head"] = mapbox_assist_config.extra_head
        if mapbox_assist_config.extra_js:
            context["extra_js"] = mapbox_assist_config.extra_js

        return context

    class Meta:
        template='blocks/map/map_block.html'
        icon="map-marker"
        label = _("Interactive Map")
        label_format = label
        form_classname = "struct-block map-block"

class MapBlockAdapter(StructBlockAdapter):
    @cached_property
    def media(self):
        super().media
        return forms.Media(
            css={"all": ("css/admin/map-block.css",)},
        )
    
register(MapBlockAdapter(), MapBlock)    