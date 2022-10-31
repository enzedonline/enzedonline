from django import template
from django.utils.safestring import mark_safe

register = template.Library()

@register.simple_tag()
def get_google_thumbnails(img):
    return {
        'tn1x1': img.get_rendition('thumbnail-500x500|format-png'),
        'tn4x3': img.get_rendition('thumbnail-500x375|format-png'),
        'tn16x9': img.get_rendition('thumbnail-500x281|format-png'),
    }
    
