from django import template
from site_settings.models import MapBoxToken

register = template.Library()

@register.simple_tag()
def get_map_settings(block):
    try:
        token = getattr(MapBoxToken.objects.first(), 'key')
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
        latitude, longitude = [round(float(x.strip()),6) for x in waypoint.value['gps_coord'].split(',')]
        map_settings['waypoints'].append({
            'longitude' : longitude,
            'latitude' : latitude,
            'pin_label' : waypoint.value['pin_label'],
            'show_pin' : waypoint.value['show_pin']
        })

    return(map_settings)
    