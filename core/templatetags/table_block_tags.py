import pandas as pd
from django import template
from django.utils.safestring import mark_safe
from io import StringIO

register = template.Library()

@register.filter
def render_html_table(table_block):
    df = pd.read_csv(StringIO(table_block['data']))
    # Hide row numbers (index)
    dfs = df.style.hide()
    # Align everything not an object (object=string) to the right
    dfs = dfs.set_properties(subset=list(df.select_dtypes(exclude='O')), **{'text-align': 'right', 'padding-right': '1rem'})
    # If row headers, set formatting on 1st column (don't set to index, error thrown if not unique values)
    if table_block['row_headers']:
        dfs = dfs.set_properties(subset=df.columns[0], **{'font-weight': 'bold', 'border-right-width': '0.1rem', 'border-right-color': 'var(--bs-dark)'})
    # Set column headers left aligned
    dfs = dfs.set_table_styles([ dict(selector='th', props=[('text-align', 'left')] ) ])
    # Add table classes and styles
    classes = f'class="table table-striped table-hover mx-auto w-{table_block["width"]}' + \
                (" table-sm" if table_block['compact'] else '') + '"'
    max_width = table_block['max_width']
    styles = f' style="max-width:{max_width}px;"' if max_width else ''
    dfs = dfs.set_table_attributes(f'{classes}{styles}')
    # Add table caption if any
    dfs = dfs.set_caption(table_block['caption'].source) if table_block['caption'] else dfs

    return mark_safe(dfs.to_html())
