from django import template
from datetime import datetime
from wagtail.core.models import Page
register = template.Library()

@register.simple_tag()
def trans_url(link):
    return link.localized.url

@register.simple_tag()
def trans_page_from_slug(slug, specific=False):
    try:
        if specific:
            return Page.objects.get(slug=slug).specific.localized
        else:
            return Page.objects.get(slug=slug).localized
    except Page.DoesNotExist:
        return Page.objects.none()

@register.simple_tag()
def get_cache_key_settings(page):
    if not page:
        page = {}
        page['slug'] = '_DynamicPage'
        page['last_published_at'] = datetime.now()
    return page

@register.simple_tag()
def paginator_filter(filter):
    if filter:
        return filter + '&'
    else:
        return '?'