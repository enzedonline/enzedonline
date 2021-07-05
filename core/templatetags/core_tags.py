from django import template

register = template.Library()

@register.simple_tag()
def trans_url(link):
    return link.localized.url