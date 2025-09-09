from django import template
from django.templatetags.static import static
from django.utils.safestring import mark_safe
from django.template import Context, Template

register = template.Library()

@register.filter()
def import_feature_layer_js(featureLayers):
    js = set()
    for layer in featureLayers:
        name = layer['handler']
        source = layer['source']
        js.add(f"import {{ {name} }} from '{source}';")
    return mark_safe(''.join(sorted(js)))

@register.filter()
def parse_django_template(code):
    # If a call to {% static %} is present without {% load static %}, add load statement
    if '{% load' not in code and '{% static' in code:
        code = '{% load static %}\n' + code
    return Template(code).render(Context())