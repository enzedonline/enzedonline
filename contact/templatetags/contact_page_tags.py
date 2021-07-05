from django import template

register = template.Library()

@register.simple_tag()
def field_class(field):
    if (str(field).find('type="checkbox"') != -1):
        return 'checkbox'
    else:
        return 'false'
