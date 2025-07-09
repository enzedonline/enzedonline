from django import forms
from django.core.exceptions import ValidationError
from django.db import models
from django.forms.utils import ErrorList
from django.utils.functional import cached_property
from django.utils.safestring import mark_safe
from django.utils.translation import gettext_lazy as _
from modelcluster.fields import ParentalKey
from modelcluster.models import ClusterableModel
from wagtail.admin.panels import FieldPanel, InlinePanel
from wagtail.blocks import (BooleanBlock, CharBlock, ChoiceBlock, ListBlock,
                            StaticBlock, StructBlock, TextBlock)
from wagtail.blocks.field_block import IntegerBlock
from wagtail.blocks.struct_block import (StructBlockAdapter,
                                         StructBlockValidationError)
from wagtail.contrib.settings.models import (BaseGenericSetting,
                                             register_setting)
from wagtail.telepath import register
from wagtail.admin.forms.models import WagtailAdminModelForm
from core.utils import isfloat

STYLE_CHOICES = [
    ('satellite', _('Satellite')),
    ('terrain', _('Terrain / Topography')),
]

class MapStyleChoiceBlock(ChoiceBlock):
    choices=STYLE_CHOICES

class MapBlockSettingsForm(WagtailAdminModelForm):
    """
    Custom form for MapBlockSettings to validate inline MapboxStyle formset.
    """

    def clean(self):
        cleaned_data = super().clean()

        styles_formset = self.formsets['styles']
        valid_identifiers = {choice[0] for choice in STYLE_CHOICES}
        submitted_identifiers = set()
        errors = []
        invalid_styles = []

        for style_form in styles_formset.forms:
            if (style_form.data.get(f"{style_form.prefix}-DELETE")!='1'):  # Ignore deleted forms
                identifier = style_form.data.get(f"{style_form.prefix}-identifier")
                if identifier:
                    submitted_identifiers.add(identifier)
                    # Check for invalid identifiers
                    if identifier not in valid_identifiers:
                        invalid_styles.append(identifier)
        
        if invalid_styles:
            errors.append(f'{_("The following styles are not valid")}: {", ".join(invalid_styles)}')

        missing_styles = valid_identifiers - submitted_identifiers
        if missing_styles:
            style_map = {key: value for key, value in STYLE_CHOICES}
            missing_styles = [str(style_map[style]) for style in missing_styles]
            errors.append(
                f'{_("The following required styles are missing")}: {", ".join(missing_styles)}'
            )

        if errors:
            raise ValidationError(errors)
        return cleaned_data
    
@register_setting(icon="map-marker")
class MapBlockSettings(ClusterableModel, BaseGenericSetting):
    base_form_class = MapBlockSettingsForm
    mapbox_token = models.CharField(
        max_length=100,
        null=True,
        blank=False,
        verbose_name=_("Mapbox Access Token")
    )
    mapbox_gl_css_url = models.URLField(
        verbose_name=_("mapbox-gl-css URL")
    )
    mapbox_gl_js_url = models.URLField(
        verbose_name=_("mapbox-gl-js URL")
    )
    mapbox_directions_api_url = models.URLField(
        verbose_name=_("Mapbox Directions API URL")
    )

    panels = [
        FieldPanel("mapbox_token"),
        FieldPanel("mapbox_gl_css_url"),
        FieldPanel("mapbox_gl_js_url"),
        FieldPanel("mapbox_directions_api_url"),
        InlinePanel("styles", label="Available Styles", ),
    ]    

    class Meta:
        verbose_name = _("Map Block Configuration")


class MapboxStyle(models.Model):
    setting = ParentalKey(
        MapBlockSettings, 
        on_delete=models.CASCADE, 
        related_name="styles"
    )
    identifier = models.CharField(
        verbose_name=_("Style Identifier"),
        max_length=20,
        choices=MapStyleChoiceBlock.choices,
        unique=True
    )
    description = models.CharField(
        verbose_name=_("Style Description"),
        max_length=80
    )
    url = models.CharField(
        verbose_name=_("MapBox Style URL"),
        default="mapbox://styles/",
        max_length=80,
        help_text=_("URL to the style (mapbox://styles/{owner}/{style_id})")
    )
    tile_image = models.ForeignKey(
        "wagtailimages.Image",
        blank=False,
        null=True,
        on_delete=models.SET_NULL,
        related_name="+",
        verbose_name=_("Style Tile Image"),
        help_text=_("Displayed at 50x50")
    ) 

    def __str__(self):
        return self.description


class RouteOptionChoiceBlock(ChoiceBlock):
     choices=[
        ('', _("None")),
        ('walking', _("Walking")),
        ('cycling', _("Cycling")),
        ('driving', _("Driving")),
        ('driving-traffic', _("Driving (with traffic conditions)"))
     ]

class RouteSummaryChoiceBlock(ChoiceBlock):
    choices=[
        ('', _("Not displayed")),
        ('simple', _("Summary only")),
        ('detailed', _("Detailed")),
    ]
    
class MapWaypointBlock(StructBlock):
    gps_coord = CharBlock(
        label=_('GPS Coordinates (Latitude, Longtitude)'),
        help_text=_('Ensure latitude followed by longitude separated by a comma (e.g. 42.597486, 1.429252).')
    )
    pin_label = TextBlock(
        label=_('Map Pin Label (optional)'),
        required=False
    )
    show_pin = BooleanBlock(
        label=_('Show Pin on Map'),
        default=True,
        required=False
    )
    class Meta:
        icon = 'plus-inverse'
        label = _("Map Waypoint")
        form_classname = "struct-block flex-block map-waypoint-block"
        
    def clean(self, value):
        errors = {}
        gps = value.get('gps_coord')

        if gps.count(',') != 1:
            errors['gps_coord'] = ErrorList(
                [_("Please enter latitude followed by longitude, separated by a comma.")]
            )
            raise StructBlockValidationError(block_errors=errors)

        lat, lng = gps.split(',')
        
        if not(isfloat(lat) and isfloat(lng)):
            errors['gps_coord'] = ErrorList(
                [_("Please enter latitude and longitude in numeric format (e.g. 42.603552, 1.442655 not 42°36'12.8\"N 1°26'33.6\"E).")]
            )
            raise StructBlockValidationError(block_errors=errors)

        if (float(lat) < -90 or float(lat) > 90 or float(lng) < -180 or float(lng) > 360):
            errors['gps_coord'] = ErrorList(
                [_("Please enter latitude between -90 and 90 and longitude between -180 and 360.")]
            )
            raise StructBlockValidationError(block_errors=errors)

        return super().clean(value)
        
class MapBlock(StructBlock):
    padding_help_text = _(
        "Padding left/right should be given as a percentage of the map dimension."
    )
             
    waypoints = ListBlock(
        MapWaypointBlock, 
        min_num=2, 
        max_num=25, 
        label=_("Add Waypoints (minimum 2, maximum 25)")
    )
    style = MapStyleChoiceBlock(
        required=True,
        label=_("Map Type")
    )
    height = IntegerBlock(
        default=70, 
        min_value=20,
        label=_("Height (% of viewport)")
    )
    route_type = RouteOptionChoiceBlock(
        default='walking', 
        required=False
    )
    show_route_summary = RouteSummaryChoiceBlock(
        label=_("Show Route Summary"),
        required=False
    )
    pitch = IntegerBlock(
        default=0, 
        min_value=0, 
        max_value=90, 
        label=_("Pitch (degrees from vertical)")
    )
    bearing = IntegerBlock(
        default=0, 
        min_value=-180, 
        max_value=360, 
        label=_("Bearing (degrees from North)")
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
        context = super().get_context(value, parent_context)
        context['map_help_text'] = _(
            "Right-click, drag left/right to rotate. Right-click, drag up/down to tilt."
        )
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