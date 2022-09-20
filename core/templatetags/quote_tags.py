from django import template
from wagtail.models import Locale

register = template.Library()

@register.simple_tag()
def get_quote_marks():

    if Locale.get_active().language_code in ('fr', 'es'):
        open_path = "svg/open-guillemet.svg"
        close_path = "svg/close-guillemet.svg"
    else:
        open_path = "svg/open-quote.svg"
        close_path = "svg/close-quote.svg"

    return {
        'open' : open_path,
        'close' : close_path
    }

