import pandas as pd
from django import template
from django.utils.safestring import mark_safe
from io import StringIO

register = template.Library()

@register.filter
def render_html_table(csv_data):
    df = pd.read_csv(StringIO(csv_data))
    html = df.to_html(classes='table table-striped text-center', justify='center',index=False)
    return mark_safe(html)
