from django import template

register = template.Library()

@register.simple_tag()
def padding(border, background):
    if background.find('bg-transparent') != -1 and not border:
        return '0'
    else:
        return '4'

@register.simple_tag()
def card_layout(value):
    if value['background'].find('bg-transparent') != -1 and not value['border']:
        padding = 'p-0'
    else:
        padding = f"p-4 pb-3{'' if value['format'] == 'vertical' else ' pt-0'}"
    border = f"rounded-3 border{'' if value['border'] else '-0'}"
    return f"{value['background']} {padding} h-100 {border}"

@register.simple_tag()
def button_layout(value):
    justification = f"text-{value['breakpoint']}-{value['link']['placement']}"
    if value['format'].find('responsive') != -1:
        justification = f"text-end {justification}"
    return f"mt-auto p-0 {justification}"

@register.simple_tag()
def embed_button_layout(value):
    justification = f"text-{value['breakpoint']}-{value['button_placement']}"
    if value['format'].find('responsive') != -1:
        justification = f"text-end {justification}"
    return f"mt-auto p-0 {justification}"

@register.simple_tag()
def row_layout(value, block_id):
    layout = {}
    
    minmax_style = (f"min-width:{str(value['image_min'])}" if value['image_min'] else '200') + "px !important;"
    minmax_style += f"max-width:{str(value['image_max'])}px !important;" if value['image_max'] else ''

    if value['format'].find('right') != -1:
        layout['row_class'] = 'row flex-row-reverse'
    else:
        layout['row_class'] = 'row'
        
    if value['format'].find('responsive') != -1:
        layout['image_column'] = f"col-{value['breakpoint']}-4"
        if value['format'].find('right') != -1:
            layout['text_column'] = "pe-2 text-break"
        else:
            layout['text_column'] = "ps-2 text-break"
        layout['heading_align'] = f"text-center text-{value['breakpoint']}-start"
        if value['breakpoint'] == 'md':
            breakpoint = '768px'
        else:
            breakpoint = '576px'
        layout['image_style'] = f"@media (min-width: {breakpoint}) {{.size-{block_id} {{{minmax_style}}}}}"
    else:
        layout['image_column'] = 'col-4'
        layout['breakpoint'] = '0px'
        layout['image_style'] = f".size-{block_id} {{{minmax_style}}}"
        layout['heading_align'] = f"text-start"

    if value['border']:
        layout['image_column'] += ' pt-4'

    return layout
