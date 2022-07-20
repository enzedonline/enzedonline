from django import template

register = template.Library()

@register.simple_tag()
def two_column_layout(value):
    layout={
        'left_order': '', 'right_order': '', 'hide_left': '', 'hide_right': '', 
        }
    left, right = value['column_layout'].split('-') 
    breakpoint = value['breakpoint']
    
    if breakpoint == '-':
        breakpoint = ''
        layout['horizontal_padding'] = 'px-' + str(value['horizontal_padding'])
        layout['breakpoint_pixels'] = '0px'
        layout['pre_breakpoint_bottom_pad'] = ''
    else:
        layout['horizontal_padding'] = 'px' + breakpoint + '-' + str(value['horizontal_padding'])
        
        if value['order'] == 'right-first':
            layout['left_order'] = ' order-3 order' + breakpoint + '-1'
            layout['right_order'] = ' order-2'
        
        if value['hide'] == 'hide-right':
            layout['hide_right'] = 'd-none d' + breakpoint + '-block'
        elif value['hide'] == 'hide-left':
            layout['hide_left'] = 'd-none d' + breakpoint + '-block'

        if breakpoint == '-sm':
            layout['breakpoint_pixels'] = '576px'
        elif breakpoint == '-md':
            layout['breakpoint_pixels'] = '768px'
        else:
            layout['breakpoint_pixels'] = '991px'

    layout['left'] = breakpoint + (('-' + left) if left and left < right else '')
    layout['right'] = breakpoint + (('-' + right) if right and right < left else '')

    layout['left_min'] = str(value['left_min']) + 'px' if value['left_min'] else ''
    layout['left_max'] = str(value['left_max']) + 'px' if value['left_max'] else ''
    layout['right_min'] = str(value['right_min']) + 'px' if value['right_min'] else ''
    layout['right_max'] = str(value['right_max']) + 'px' if value['right_max'] else ''

    return layout
    
@register.simple_tag()
# def three_column_layout(breakpoint, column_layout, horizontal_padding, hide):
def three_column_layout(value):
    layout={}
    layout['left'], layout['centre'], layout['right'] = value['column_layout'].split('-') 
    layout['hide_sides'] = ''
    breakpoint = value['breakpoint']

    if breakpoint == '-':
        breakpoint = ''
        layout['horizontal_padding'] = 'px-' + str(value['horizontal_padding'])
        layout['breakpoint_pixels'] = '0px'
        layout['pre_breakpoint_bottom_pad'] = ''
    else:
        layout['horizontal_padding'] = 'px' + breakpoint + '-' + str(value['horizontal_padding'])
        if breakpoint == '-sm':
            layout['breakpoint_pixels'] = '576px'
        elif breakpoint == '-md':
            layout['breakpoint_pixels'] = '768px'
        else:
            layout['breakpoint_pixels'] = '991px'

        if value['hide'] == 'hide-sides':
            layout['hide_sides'] = 'd-none d' + breakpoint + '-block'

    layout['left'] = breakpoint + (('-' + layout['left']) if layout['left'] else '')
    layout['centre'] = breakpoint 
    layout['right'] = breakpoint + (('-' + layout['right']) if layout['right'] else '')
    layout['outer_min'] = str(value['outer_min']) + 'px' if value['outer_min'] else ''
    layout['outer_max'] = str(value['outer_max']) + 'px' if value['outer_max'] else ''
    
    
    return layout
