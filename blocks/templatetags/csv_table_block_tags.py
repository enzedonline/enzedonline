import pandas as pd
from django import template
from django.utils.safestring import mark_safe
from io import StringIO

register = template.Library()

@register.filter()
def render_html_table(table_block):
    df = pd.read_csv(
        StringIO(table_block["data"]),
        header=("infer" if table_block["column_headers"] else None),
    )
    # Note: NaN is considered float by pandas, any int column with NaN's will be interpreted as float
    # Set NaN's to unused integer value, re-infer dtypes and set back to NaN again
    df.select_dtypes(include="float64").fillna(-999999, inplace=True)
    df = df.convert_dtypes()
    df.replace(-999999, None, inplace=True)
    # Hide row numbers (index)
    dfs = df.style.hide()
    # Set missing values representation as empty string
    dfs = dfs.format(na_rep="")
    # Set decimal places for float. Redeclare na values for floats as format is not cumulative, it is replaced.
    dfs = dfs.format(
        subset=list(df.select_dtypes(include="Float64")),
        precision=table_block["precision"],
        na_rep="",
    )
    # Align everything not an object (object=string) to the right
    dfs = dfs.set_properties(
        subset=list(df.select_dtypes(exclude=["string", "object"])),
        **{"text-align": "right", "padding-right": "0.7rem"},
    )
    if table_block["column_headers"]:
        # Set non-object column headers to right aligned
        for column in list(df.select_dtypes(exclude=["string", "object"])):
            dfs = dfs.set_table_styles(
                {
                    column: [
                        {
                            "selector": "th",
                            "props": [("text-align", "right"), ("padding-right", "0.7rem")],
                        }
                    ]
                },
                overwrite=False,
            )
    else:
        # hide column index row
        dfs = dfs.hide(axis=1)
    # If row headers, set formatting on 1st column (don't set to index, error thrown if not unique values)
    if table_block["row_headers"]:
        dfs = dfs.set_properties(
            subset=df.columns[[0]],
            **{
                "font-weight": "bold",
                "border-right-width": "0.1rem",
                "border-right-color": "var(--bs-dark)",
            },
        )
    # Add table classes and styles
    classes = f'\
        class="table table-striped table-hover mb-0\
        {" table-sm" if table_block["compact"] else ""}"'
    dfs = dfs.set_table_attributes(classes)

    return mark_safe(dfs.to_html())
