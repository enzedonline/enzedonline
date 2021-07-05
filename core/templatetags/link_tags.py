from django import template
from wagtail_localize.synctree import Locale

register = template.Library()

@register.simple_tag()
def get_localized_link(page):
    if page.internal_page: # link is to internal page (not url)
        trans_page = page.internal_page.localized # get translated page if any
        url = str(trans_page.url)
    else: # not a page link, test if internal or external url, translate if internal
        if page.external_link.startswith('/'): # presumes internal link starts with '/' and no lang code
            url = '/' + Locale.get_active().language_code + page.external_link
        else: # external link, do nothing
            url = page.external_link
    return url   
