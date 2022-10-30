from django import template
from django.utils.safestring import mark_safe

register = template.Library()

@register.simple_tag()
def get_google_thumbnails(img):
    return {
        'tn1x1': img.get_rendition('fill-500x500-c100'),
        'tn4x3': img.get_rendition('fill-500x375-c100'),
        'tn16x9': img.get_rendition('fill-500x281-c100'),
    }
    
