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
def get_masonry_options(col_min, col_max):
    # col_min/max = min and max number of columns to display
    minpx = 300 # px to start counting from - it just works
    maxpx = 1400 # widest breakpoint, equivalenet to bootstrap xxl
    steps = col_max - col_min # calculate number of changes

    count = steps # loop counter
    breakpoints = {}

    for col in range(col_max, col_min-1, -1):
        # loop from max to min, needed for creating the media css instructions in js
        px = round(minpx + count * (maxpx-minpx)/steps)
        breakpoints[f'min-width: {px}px'] = col
        count = count - 1
        
    return {'breakpointCols': breakpoints, 'numCols': col_min}

@register.simple_tag()
def get_masonry_id(id):
    # because Django can't create on-the-fly variables in function calls
    return {
        'grid': f'grid-{id}',
        'options': f'grid-{id}-options'
    }