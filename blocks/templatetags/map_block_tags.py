from django import template
from django.utils.html import json_script
from django.utils.translation import gettext_lazy as _

from blocks.map import MapBlockSettings

register = template.Library()


@register.simple_tag()
def get_map_settings(block):
    settings = MapBlockSettings.load()
    map_settings = {
        'uid': block.id,
        'token': settings.mapbox_token,
        'urls': {
            'mapboxGlCSS': settings.mapbox_gl_css_url,
            'mapboxGlJS': settings.mapbox_gl_js_url,
            'directionsAPI': settings.mapbox_directions_api_url
        },
        'pitch': block.value['pitch'],
        'bearing': block.value['bearing'],
        'padding': {
            'top': block.value['padding_top'],
            'right': block.value['padding_right'],
            'bottom': block.value['padding_bottom'],
            'left': block.value['padding_left']
        },
        'styles': {},
        'initialStyle': block.value['style'],
        'waypoints': [],
        'route' : {
            'type': block.value['route_type'],
            'showSummary': block.value['show_route_summary'],
            'summaryHeading': _("Route Summary")            
        }
    }
    for style in settings.styles.all():
        map_settings['styles'][style.identifier] = {
            'description': style.description,
            'url': style.url,
            'tileImage': style.tile_image.get_rendition('fill-50x50').url
        }
    for waypoint in block.value['waypoints']:
        latitude, longitude = [
            round(float(x.strip()), 6) for x in waypoint['gps_coord'].split(',')
        ]
        map_settings['waypoints'].append({
            'longitude': longitude,
            'latitude': latitude,
            'pinLabel': waypoint['pin_label'],
            'showPin': waypoint['show_pin']
        })

    return (map_settings)


@register.simple_tag()
def add_json_script(value, element_id):
    return json_script(value, element_id)
