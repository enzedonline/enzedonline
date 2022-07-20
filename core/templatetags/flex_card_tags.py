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
        padding = f"p-4{'' if value['format'] == 'vertical' else ' pt-0'}"
    border = f"border{'' if value['border'] else '-0'}"
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
def row_layout(value):
    layout = {}
    
    if value['format'].find('right') != -1:
        layout['row_class'] = 'row flex-row-reverse'
        text_padding = 'pe'
    else:
        layout['row_class'] = 'row'
        text_padding = 'ps'
        
    if value['format'].find('responsive') != -1:
        layout['image_column'] = f"col-{value['breakpoint']}-4 pt-4"
        layout['text_column'] = f"p-0 {text_padding}-{value['breakpoint']}-3 pt-{value['breakpoint']}-1 text-break"
        if value['breakpoint'] == 'md':
            layout['breakpoint'] = '768px'
        else:
            layout['breakpoint'] = '576px'
    else:
        layout['image_column'] = 'col-4 pt-4'
        layout['text_column'] = f"p-0 {text_padding}-3 pt-1 text-break"
        layout['breakpoint'] = '0px'
  
    image_min = 'min-width: ' + str(value['image_min'] if value['image_min'] else 200) + 'px;'
    image_max = (f"max-width: {str(value['image_max'])}px;") if value['image_max'] else ''
    layout['image_style'] = f'{image_min}{image_max}'
    
    return layout



