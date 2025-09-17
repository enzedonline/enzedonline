import json
from django import template
from django.utils.safestring import mark_safe

from site_settings.models import SocialMediaLinks, Brand

register = template.Library()

@register.filter
def tojson(value):
    """Render Python list/dict/etc. as JSON, safe for inclusion in templates."""
    return mark_safe(json.dumps(value, ensure_ascii=False))

@register.simple_tag()
def get_google_thumbnails(img):
    return {
        'tn1x1': img.get_rendition('thumbnail-500x500|format-png'),
        'tn4x3': img.get_rendition('thumbnail-500x375|format-png'),
        'tn16x9': img.get_rendition('thumbnail-500x281|format-png'),
    }
    
@register.simple_tag(takes_context=True)
def get_social_media_sameas(context):
    request = context['request']
    links = SocialMediaLinks.for_request(request).social_media_links.all()
    same_as = []
    for link in links:
        same_as.append(f'"{link.url}"')
    return mark_safe(','.join(same_as))

@register.simple_tag(takes_context=True)
def get_organisation_logo(context):
    request = context['request']
    try:
        brand = Brand.for_request(request)
        logo = getattr(brand, 'logo', None)
        if logo and logo.is_svg():
            return logo.full_url
        elif logo:
            return logo.get_rendition('thumbnail-500x500|format-png').full_url
    except (AttributeError, Brand.DoesNotExist):
        pass
    return ''