from django import template
from django.templatetags.static import static
from django.utils.safestring import mark_safe
from django.template import Context, Template

from goneforawander.map.settings import MapboxSettings

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

@register.simple_tag()
def mapbox_importmap():
    settings = MapboxSettings.load()
    return mark_safe(
        f'<script type="importmap">{{"imports": {{"mapbox-gl": "https://esm.sh/mapbox-gl@v{settings.api_version}"}}}}</script>'
    )