from django import template

register = template.Library()

@register.simple_tag()
def button_appearance(style, outline):
    print(outline)
    if outline:
        style = style.replace("-", "-outline-")
    return style
