from django import template

register = template.Library()

@register.simple_tag()
def button_colour(colour_theme):
    result = {}
    if colour_theme == 'bg-transparent':
        result['background'] = 'bs-transparent'
        result['border'] = '0'
    else:
        result['background'] = colour_theme.replace('bg-','bs-')
        result['border'] = colour_theme.replace('bg-','')
    return result

