import json

from django import template
from django.utils.safestring import mark_safe
from wagtail.rich_text import RichText

from site_settings.models import Brand, SocialMediaLinks

register = template.Library()

@register.filter
def tojson(value):
    """Render Python list/dict/etc. as JSON, safe for inclusion in templates."""
    return mark_safe(json.dumps(value, ensure_ascii=False))

@register.filter
def richtext_to_json(value):
    """Convert a RichTextField to plain text JSON string safely for JSON-LD."""
    if not value:
        return mark_safe('""')  # empty string

    # Get raw text without HTML
    text = RichText(value).source
    from bs4 import BeautifulSoup
    text = BeautifulSoup(text, "html.parser").get_text(separator=" ", strip=True)

    # Dump as JSON string without escaping Unicode
    return mark_safe(json.dumps(text, ensure_ascii=False))

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