from django import template
from urllib.parse import urlparse
from django.conf import settings

register = template.Library()

@register.simple_tag()
def get_next_url(request):
    referer = request.META.get('HTTP_REFERER')
    if referer:
        base_url = getattr(settings, 'WAGTAILADMIN_BASE_URL')
        netloc = urlparse(referer).netloc.replace('/','')
        if netloc in base_url:
            return urlparse(referer).path
    return '/'