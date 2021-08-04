from django import template
from adv_cache_tag.tag import CacheTag
from datetime import datetime

register = template.Library()

@register.simple_tag()
def trans_url(link):
    return link.localized.url

@register.simple_tag()
def get_cache_key_settings(page):
    if not page:
        page = {}
        page['slug'] = '_DynamicPage'
        page['last_published_at'] = datetime.now()
    return page