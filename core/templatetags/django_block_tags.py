from django import template
from django.template import Context, Template
from django.utils.safestring import mark_safe

register = template.Library()

@register.filter()
@mark_safe
def parse_django_template(code):
    return Template(code).render(Context())