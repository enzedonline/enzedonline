from django import template
from django.utils.safestring import mark_safe

register = template.Library()

def breakpoint_to_pixels(breakpoint):
    if breakpoint == '-sm':
        return '576px'
    elif breakpoint == '-md':
        return '768px'
    elif breakpoint == '-lg':
        return '991px'
    else:
        return '0px'

@register.simple_tag()
def two_column_layout(value, block_id):
    left, right = value['column_layout'].split('-') 
    breakpoint = value['breakpoint']
    horizontal_padding = str(value['horizontal_padding'])

    if breakpoint == '-':
        breakpoint = ''
        lcol_horizontal_padding = f' pe-{horizontal_padding}'
        rcol_horizontal_padding = f' ps-{horizontal_padding}'
        divider = 'divider' if value['vertical_border'] else ''
    else:
        lcol_horizontal_padding = f' pe{breakpoint}-{horizontal_padding}'
        rcol_horizontal_padding = f' ps{breakpoint}-{horizontal_padding}'
        divider = 'divider' + breakpoint if value['vertical_border'] else ''
        
    if value['order'] == 'right-first':
        left_order = f' order-3 order{breakpoint}-1'
        right_order = ' order-2'
    else:
        left_order = right_order = ''

    hide_left = hide_right = ''
    if value['hide'] == 'hide-right':
        hide_right = f' d-none d{breakpoint}-block'
    elif value['hide'] == 'hide-left':
        hide_left = f' d-none d{breakpoint}-block'

    left_col = f"col{breakpoint}{('-' + left) if left and left < right else ''}"
    right_col = f"col{breakpoint}{('-' + right) if right and right < left else ''}"

    l_minmax_style = r_minmax_style = ''
    l_minmax_style = f"min-width:{str(value['left_min'])}px !important;" if value['left_min'] else ''
    l_minmax_style += f"max-width:{str(value['left_max'])}px !important;" if value['left_max'] else ''
    r_minmax_style = f"min-width:{str(value['right_min'])}px !important;" if value['right_min'] else ''
    r_minmax_style += f"max-width:{str(value['right_max'])}px !important;" if value['right_max'] else ''

    sizel = sizer = ''
    if l_minmax_style or r_minmax_style:
        style = f"@media (min-width: { breakpoint_to_pixels(breakpoint) }) {{"
        if l_minmax_style:
            style += f".sizel-{block_id} {{{l_minmax_style}}}"
            sizel = f" sizel-{block_id}"
        if r_minmax_style:
            style += f".sizer-{block_id} {{{r_minmax_style}}}"
            sizer = f" sizer-{block_id}"
        style += "}"

    return {
        'l_class': mark_safe(f'class="{left_col}{lcol_horizontal_padding}{left_order}{hide_left}{sizel} mx-auto"'),
        'r_class': mark_safe(f'class="{right_col}{rcol_horizontal_padding}{right_order}{hide_right}{sizer} mx-auto"'),
        'size': mark_safe(style) if l_minmax_style or r_minmax_style else '',
        'divider': divider
    }

@register.simple_tag()
# def three_column_layout(breakpoint, column_layout, horizontal_padding, hide):
def three_column_layout(value, block_id):
    left, centre, right = value['column_layout'].split('-') 
    breakpoint = value['breakpoint']
    horizontal_padding = str(value['horizontal_padding'])

    if breakpoint == '-':
        breakpoint = ''
        lcol_horizontal_padding = f' pe-{horizontal_padding}'
        mcol_horizontal_padding = f' px-{horizontal_padding}'
        rcol_horizontal_padding = f' ps-{horizontal_padding}'
        divider = 'three-col-divider' if value['vertical_border'] else ''
        hide_sides = ''
    else:
        lcol_horizontal_padding = f' pe{breakpoint}-{horizontal_padding}'
        mcol_horizontal_padding = f' px{breakpoint}-{horizontal_padding}'
        rcol_horizontal_padding = f' ps{breakpoint}-{horizontal_padding}'
        divider = f' three-col-divider{breakpoint}' if value['vertical_border'] else ''
        hide_sides = f' d-none d{breakpoint}-block' if value['hide'] == 'hide-sides' else ''

    left_col = f'col{breakpoint}{("-" + left) if left else ""}'
    centre_col = f'col{breakpoint}'
    right_col = f'col{breakpoint}{("-" + right) if left else ""}'

    minmax_style = size = ''
    minmax_style = f"min-width:{str(value['outer_min'])}px !important;" if value['outer_min'] else ''
    minmax_style += f"max-width:{str(value['outer_max'])}px !important;" if value['outer_max'] else ''
    
    if minmax_style:
        style = f"@media (min-width: { breakpoint_to_pixels(breakpoint) }) {{"
        style += f".size-{block_id} {{{minmax_style}}}"
        size = f" size-{block_id}"
        style += "}"
    
    return {
        'l_class': mark_safe(f'class="{left_col}{lcol_horizontal_padding}{hide_sides}{size} mx-auto"'),
        'm_class': mark_safe(f'class="{centre_col}{mcol_horizontal_padding}{divider} mx-auto"'),
        'r_class': mark_safe(f'class="{right_col}{rcol_horizontal_padding}{hide_sides}{size} mx-auto"'),
        'size': mark_safe(style) if minmax_style else ''
    }
