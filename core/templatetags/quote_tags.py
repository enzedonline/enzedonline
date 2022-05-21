from django import template
from django.utils.translation import get_language_from_request

register = template.Library()

@register.simple_tag(takes_context=True)
def quote_marks(context):
    language = get_language_from_request(context.get('request', None))
    quote_mark = {}
    if language in ('fr', 'es'):
        quote_mark['open'] = "\u00AB"
        quote_mark['close'] = "\u00BB"
        quote_mark['top_margin'] = "mt-n2"
        quote_mark['bottom_margin'] = ""
    else:
        quote_mark['open'] = "\u201C"
        quote_mark['close'] = "\u201D"
        quote_mark['top_margin'] = "mt-4"
        quote_mark['bottom_margin'] = "mb-n4"

    return quote_mark
