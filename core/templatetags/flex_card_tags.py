from django import template

register = template.Library()

@register.simple_tag()
def padding(border, background):
    if background == 'bg-transparent' and not border:
        return '0'
    else:
        return '3'
