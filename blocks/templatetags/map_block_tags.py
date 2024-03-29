from django import template
from site_settings.models import Tokens
from django.utils.html import json_script

register = template.Library()

@register.simple_tag()
def get_map_settings(block):
    try:
        token = getattr(Tokens.objects.first(), 'mapbox')
    except:
        token = ''
        print('MapBox key not found in site settings')
    
    map_settings = {
        'uid': block.id,
        'token': token,
        'route_type' : block.value['route_type'], 
        'show_route_info' : block.value['show_route_info'], 
        'padding' : [
            block.value['padding_top'], 
            block.value['padding_right'], 
            block.value['padding_bottom'], 
            block.value['padding_left']
            ],
        'waypoints' : []
        }
    
    waypoints = block.value['waypoints']
    for waypoint in waypoints:
        latitude, longitude = [round(float(x.strip()),6) for x in waypoint['gps_coord'].split(',')]
        map_settings['waypoints'].append({
            'longitude' : longitude,
            'latitude' : latitude,
            'pin_label' : waypoint['pin_label'],
            'show_pin' : waypoint['show_pin']
        })

    return(map_settings)
    
@register.simple_tag()
def add_json_script(value, element_id):
    return json_script(value, element_id)