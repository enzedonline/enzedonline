from django import template

register = template.Library()

@register.simple_tag()
def two_column_layout(breakpoint, column_layout, horizontal_padding, order, hide):
    layout={}
    layout['left'], layout['right'] = column_layout.split('-') 
    layout['left_order'] = ''
    layout['right_order'] = ''
    layout['hide_left'] = ''
    layout['hide_right'] = ''
    
    if breakpoint == '-':
        breakpoint = ''
        layout['horizontal_padding'] = 'px-' + str(horizontal_padding)
        layout['breakpoint_pixels'] = '0px'
        layout['pre_breakpoint_bottom_pad'] = ''
    else:
        layout['horizontal_padding'] = 'px' + breakpoint + '-' + str(horizontal_padding)
        
        if order == 'right-first':
            layout['left_order'] = ' order-3 order' + breakpoint + '-1'
            layout['right_order'] = ' order-2'
        
        if hide == 'hide-right':
            layout['hide_right'] = 'd-none d' + breakpoint + '-block'
        elif hide == 'hide-left':
            layout['hide_left'] = 'd-none d' + breakpoint + '-block'

        if breakpoint == '-sm':
            layout['breakpoint_pixels'] = '575px'
        elif breakpoint == '-md':
            layout['breakpoint_pixels'] = '767px'
        else:
            layout['breakpoint_pixels'] = '991px'

    layout['left'] = breakpoint + (('-' + layout['left']) if layout['left'] else '')
    layout['right'] = breakpoint + (('-' + layout['right']) if layout['right'] else '')

    return layout
    
@register.simple_tag()
def three_column_layout(breakpoint, column_layout, horizontal_padding, hide):
    layout={}
    layout['left'], layout['centre'], layout['right'] = column_layout.split('-') 
    layout['hide_sides'] = ''
 
    if breakpoint == '-':
        breakpoint = ''
        layout['horizontal_padding'] = 'px-' + str(horizontal_padding)
        layout['breakpoint_pixels'] = '0px'
        layout['pre_breakpoint_bottom_pad'] = ''
    else:
        layout['horizontal_padding'] = 'px' + breakpoint + '-' + str(horizontal_padding)
        if breakpoint == '-sm':
            layout['breakpoint_pixels'] = '575px'
        elif breakpoint == '-md':
            layout['breakpoint_pixels'] = '767px'
        else:
            layout['breakpoint_pixels'] = '991px'

        if hide == 'hide-sides':
            layout['hide_sides'] = 'd-none d' + breakpoint + '-block'

    layout['left'] = breakpoint + (('-' + layout['left']) if layout['left'] else '')
    layout['centre'] = breakpoint + (('-' + layout['centre']) if layout['centre'] else '')
    layout['right'] = breakpoint + (('-' + layout['right']) if layout['right'] else '')
    return layout
