from django import template
register = template.Library()

def get_column_number(min, max):
    increment = (max - min)/5
    columns = [min]
    columns.append(min + round(increment))
    columns.append(min + round(2*increment))
    columns.append(min + round(3*increment))
    columns.append(min + round(4*increment))
    columns.append(min + round(5*increment))
    return columns
    

@register.simple_tag()
def get_column_layout(col_min, col_max):
    columns = get_column_number(col_min, col_max)
    return f'row-cols-{columns[0]} \
             row-cols-sm-{columns[1]} \
             row-cols-md-{columns[2]} \
             row-cols-lg-{columns[3]} \
             row-cols-xl-{columns[4]} \
             row-cols-xxl-{columns[5]}'
     
@register.simple_tag()
def get_masonry_layout(col_min, col_max):
    # col_minmax = min and max number of columns to display
    columns = get_column_number(col_min, col_max)
    return dict(enumerate(columns))

