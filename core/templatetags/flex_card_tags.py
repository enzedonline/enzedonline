from django import template

register = template.Library()

@register.simple_tag()
def padding(border, background):
    if background.find('bg-transparent') != -1 and not border:
        return '0'
    else:
        return '4'
