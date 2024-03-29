from django.forms.utils import ErrorList
from django.utils.translation import gettext_lazy as _
from wagtail.blocks import (BooleanBlock, CharBlock, ListBlock, StructBlock,
                            TextBlock)
from wagtail.blocks.field_block import IntegerBlock
from wagtail.blocks.struct_block import StructBlockValidationError

from core.utils import isfloat

from .choices import DefaultChoiceBlock


class RouteOptionChoiceBlock(DefaultChoiceBlock):
     choices=[
        ('no-route', "None"),
        ('walking', "Walking"),
        ('cycling', "Cycling"),
        ('driving', "Driving"),
        ('driving-traffic', "Driving (with traffic conditions)")
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
    waypoints = ListBlock(
        MapWaypointBlock, 
        min_num=2, 
        max_num=25, 
        label=_("Add Waypoints (minimum 2, maximum 25)")
    )
    route_type = RouteOptionChoiceBlock(default='walking')
    show_route_info = BooleanBlock(
        label=_("Show Route Info"),
        default=True,
        required=False
    )
    height = IntegerBlock(
        default=70, 
        min_value=20,
        label=_("Height (% of viewport)"))
    padding_top = IntegerBlock(default=50, min_value=0)
    padding_right = IntegerBlock(default=50, min_value=0)
    padding_bottom = IntegerBlock(default=50, min_value=0)
    padding_left = IntegerBlock(default=50, min_value=0)

    class Meta:
        template='blocks/map_block.html'
        icon="map-marker"
        label = _("Interactive Map")
        label_format = label
        form_classname = "struct-block flex-block map-block"
