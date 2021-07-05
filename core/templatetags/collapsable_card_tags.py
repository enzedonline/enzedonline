from django import template

register = template.Library()

@register.simple_tag()
def button_colour(colour_theme):
    result = {}
    if colour_theme == 'bg-transparent':
        result['text'] = 'black'
        result['background'] = 'transparent'
    else:
        theme = colour_theme.split()
        result['text'] = theme[0].replace('text-','')
        result['background'] = theme[1].replace('bg-','')
    return result

