from django import template
from site_settings.models import MapBoxToken

register = template.Library()

@register.simple_tag()
def get_waypoints(waypoints):
    waypoint_list = []
    try:    
        for waypoint in waypoints:
            row = [round(float(x.strip()),6) for x in waypoint.value['gps_coord'].split(',')]
            row.append(waypoint.value['pin_label'])
            row.append(waypoint.value['show_pin'])
            waypoint_list.append(row)
        return(waypoint_list)
    except:
        return()

@register.simple_tag()
def get_padding(padding_top, padding_right, padding_bottom, padding_left):
    return([padding_top, padding_right, padding_bottom, padding_left])

@register.simple_tag()
def get_mapbox_token():
    token=MapBoxToken.objects.first()
    return(getattr(token, 'key'))