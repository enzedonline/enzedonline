import wagtail.admin.rich_text.editors.draftail.features as draftail_features
from wagtail.admin.rich_text.converters.html_to_contentstate import (
    BlockElementHandler, InlineStyleElementHandler)
from wagtail.admin.rich_text.editors.draftail.features import \
    InlineStyleFeature
    
def register_inline_styling(features, feature_name, type_, tag, description, label=None, icon=None, style=None, style_map=None):
    control = {
        "type": type_,
        "description": description
    }
    if label:
        control['label'] = label
    elif icon:
        control['icon'] = icon
    else:
        control['label'] = description
    if style:
        control['style'] = style
    
    if not style_map:
        style_map = {"element": tag}
        
    features.register_editor_plugin(
        "draftail", feature_name, InlineStyleFeature(control)
    )
    db_conversion = {
        "from_database_format": {tag: InlineStyleElementHandler(type_)},
        "to_database_format": {"style_map": {type_: style_map}}
    }
    features.register_converter_rule("contentstate", feature_name, db_conversion)
    
def register_block_feature(features, feature_name, type_, description, css_class, element='div', label=None, icon=None, style=None):
    control = {
        'type': type_,
        'description': description,
        'element': element,
    }
    if label:
        control['label'] = label
    elif icon:
        control['icon'] = icon
    else:
        control['label'] = description
    if style:
        control['style'] = style

    features.register_editor_plugin(
        'draftail', feature_name, draftail_features.BlockFeature(control, css={'all': ['admin.css']})
    )

    features.register_converter_rule('contentstate', feature_name, {
        'from_database_format': {f'{element}[class={css_class}]': BlockElementHandler(type_)},
        'to_database_format': {'block_map': {type_: {'element': element, 'props': {'class': css_class}}}},
    })
     
    
#--------------------------------------------------------------------------------------------------    
# SVG icons
#--------------------------------------------------------------------------------------------------  
  
LEFT_ALIGN_ICON = [
    'M 584.19821,168.76226 H 73.024776 C 32.701407,168.76226 0,137.69252 0,99.38113 0,\
    61.069736 32.701407,30 73.024776,30 H 584.19821 c 40.39183,0 73.02477,31.069736 73.02477,\
    69.38113 0,38.31139 -32.63294,69.38113 -73.02477,69.38113 z m 0,\
    555.04902 H 73.024776 C 32.701407,723.81128 0,692.80659 0,654.43015 0,616.05372 32.701407,\
    585.04902 73.024776,585.04902 H 584.19821 c 40.39183,0 73.02477,31.0047 73.02477,69.38113 0,\
    38.37644 -32.63294,69.38113 -73.02477,69.38113 z M 0,376.90564 C 0,338.5292 32.701407,\
    307.52451 73.024776,307.52451 H 949.32209 c 40.39183,0 73.02481,31.00469 73.02481,69.38113 0,\
    38.37644 -32.63298,69.38113 -73.02481,69.38113 H 73.024776 C 32.701407,446.28677 0,415.28208 0,\
    376.90564 Z M 949.32209,1001.3358 H 73.024776 C 32.701407,1001.3358 0,970.3311 0,931.95467 0,\
    893.57823 32.701407,862.57354 73.024776,862.57354 H 949.32209 c 40.39183,0 73.02481,\
    31.00469 73.02481,69.38113 0,38.37643 -32.63298,69.38113 -73.02481,69.38113 z'
    ]
CENTRE_ALIGN_ICON = [
    'M 729.54876,161.46125 H 293.0195 c -40.24254,0 -72.75487,-31.67405 -72.75487,-70.73062 C 220.26463,\
    51.674059 252.77696,20 293.0195,20 h 436.52926 c 40.24254,0 72.75488,31.674059 72.75488,70.73063 0,\
    39.05657 -32.51234,70.73062 -72.75488,70.73062 z M 947.81339,444.38376 H 74.754876 C 34.580543,\
    444.38376 2,412.77601 2,373.65314 2,334.53026 34.580543,302.92251 74.754876,\
    302.92251 H 947.81339 c 40.24254,0 72.75491,31.60775 72.75491,70.73063 0,39.12287 -32.51237,\
    70.73062 -72.75491,70.73062 z M 2,939.49815 C 2,900.37528 34.580543,868.76753 74.754876,\
    868.76753 H 947.81339 c 40.24254,0 72.75491,31.60775 72.75491,70.73062 0,39.12288 -32.51237,\
    70.73065 -72.75491,70.73065 H 74.754876 C 34.580543,1010.2288 2,978.62103 2,939.49815 Z M 729.54876,\
    727.30627 H 293.0195 c -40.24254,0 -72.75487,-31.60775 -72.75487,-70.73062 0,-39.12288 32.51233,\
    -70.73063 72.75487,-70.73063 h 436.52926 c 40.24254,0 72.75488,31.60775 72.75488,70.73063 0,\
    39.12287 -32.51234,70.73062 -72.75488,70.73062 z'
    ]
RIGHT_ALIGN_ICON = [
    'M 947.56774,163.47496 H 437.33896 c -40.31719,0 -72.88983,-29.43806 -72.88983,\
    -65.73748 C 364.44913,61.438065 397.02177,32 437.33896,32 h 510.22878 c 40.31718,\
    0 72.88986,29.438065 72.88986,65.73748 0,36.29942 -32.57268,65.73748 -72.88986,\
    65.73748 z m 0,525.89984 H 437.33896 c -40.31719,0 -72.88983,-29.37643 -72.88983,\
    -65.73748 0,-36.36104 32.57264,-65.73748 72.88983,-65.73748 h 510.22878 c 40.31718,\
    0 72.88986,29.37644 72.88986,65.73748 0,36.36105 -32.57268,65.73748 -72.88986,65.73748 z M 0,\
    360.6874 C 0,324.32636 32.640975,294.94992 72.889826,294.94992 H 947.56774 c 40.31718,\
    0 72.88986,29.37644 72.88986,65.73748 0,36.36104 -32.57268,65.73748 -72.88986,\
    65.73748 H 72.889826 C 32.640975,426.42488 0,397.04844 0,360.6874 Z M 947.56774,\
    952.32472 H 72.889826 C 32.640975,952.32472 0,922.94829 0,886.58724 0,850.2262 32.640975,\
    820.84976 72.889826,820.84976 H 947.56774 c 40.31718,0 72.88986,29.37644 72.88986,65.73748 0,\
    36.36105 -32.57268,65.73748 -72.88986,65.73748 z'
    ]
MINIMISE_ICON = [
    'm 485.28502,777.56678 c 24.60641,-29.17486 22.79287,-74.46855 -4.0578,-101.20659 -27.92436,\
    -27.76641 -69.5739,-23.51874 -93.19111,4.41089 l -66.79383,81.14635 V 86.603264 c 0,-39.570499 -29.53182,\
    -71.606954 -65.94683,-71.606954 -36.41502,0 -65.94683,32.036455 -65.94683,71.606954 V 761.76093 L 122.57745,\
    682.64229 C 97.929825,653.71335 56.197847,651.47773 29.386339,678.30518 2.5336142,705.02087 0.7406848,\
    750.33691 25.328548,779.51177 L 204.82757,994.33263 c 24.97737,29.64437 72.253,29.64437 97.25097,\
    0 z m 429.47872,95.90816 H 810.17619 l 151.22433,-164.0499 c 18.86903,-20.46935 24.50337,-51.2181 14.29809,\
    -77.97848 C 965.49334,604.68617 941.34856,587.3154 912.90899,587.3154 H 649.12167 c -34.62209,0 -64.09207,\
    31.96938 -64.09207,71.53988 0,39.5705 29.53181,71.53989 65.94682,71.53989 h 104.58755 l -151.22432,\
    164.0499 c -18.86904,20.46935 -24.50337,51.21808 -14.2981,77.97847 10.20528,26.76039 34.35006,\
    44.13116 59.08012,44.13116 h 261.93256 c 40.18635,0 69.65634,-31.96938 69.65634,-71.53988 0,\
    -39.5705 -29.46999,-71.53988 -65.94683,-71.53988 z M 1006.6771,411.37199 841.83067,53.448999 c -22.33949,\
    -48.7589041 -95.6229,-48.7589041 -117.96239,0 L 559.06303,411.37199 c -16.29299,35.56874 -3.09126,\
    78.78329 29.4906,96.55649 32.7055,17.71059 72.21178,3.30201 88.47179,-32.19295 l 14.74324,\
    -32.17059 H 874.0086 l 14.74324,32.17059 c 12.72362,27.78877 49.3983,53.36429 88.47179,32.19295 32.54477,\
    -17.63906 45.73417,-61.01011 29.45347,-96.55649 z m -257.1926,-93.67254 33.38558,-73.10482 33.4268,\
    72.94833 H 749.4845 Z']
UNDERLINE_ICON = [
    'm 38.444913,116.09067 c 0,-38.152504 32.572641,-68.976279 72.889827,-68.976279 h 218.66948 c 40.31718,\
    0 72.88982,30.823775 72.88982,68.976279 0,38.15251 -32.57264,68.97628 -72.88982,\
    68.97628 H 293.5593 v 275.90512 c 0,114.24194 97.94571,206.92882 218.66948,206.92882 120.72378,\
    0 218.66948,-92.68688 218.66948,-206.92882 V 185.06695 h -36.44491 c -40.31719,0 -72.88983,\
    -30.82377 -72.88983,-68.97628 0,-38.152504 32.57264,-68.976279 72.88983,-68.976279 h 218.66948 c 40.31718,\
    0 72.88982,30.823775 72.88982,68.976279 0,38.15251 -32.57264,68.97628 -72.88982,\
    68.97628 h -36.44492 v 275.90512 c 0,190.54696 -163.09098,344.88138 -364.44913,344.88138 -201.35814,\
    0 -364.44913,-154.33442 -364.44913,-344.88138 V 185.06695 h -36.44491 c -40.317186,0 -72.889827,\
    -30.82377 -72.889827,-68.97628 z M 2,943.80601 C 2,905.6535 34.572641,874.82973 74.889826,\
    874.82973 H 949.56774 c 40.31718,0 72.88986,30.82377 72.88986,68.97628 0,38.1525 -32.57268,\
    68.97629 -72.88986,68.97629 H 74.889826 C 34.572641,1012.7823 2,981.95851 2,943.80601 Z'
]
FONT_AWESOME_ICON = [
    'M 1011.0111,38.377438 V 802.30364 c -142.37657,51.24671 -185.81845,72.75487 -269.67821,\
    72.75487 -141.76722,0 -195.43205,-72.75487 -336.92846,-72.75487 -48.94828,0 -86.83863,\
    8.61918 -121.2762,19.93029 -34.66323,10.76317 -66.483,-15.15575 -66.483,-47.89545 v -1.69632 c 0,\
    -21.08755 12.94004,-40.01519 32.54192,-47.42709 42.15555,-16.58334 89.77237,-32.04375 155.21728,\
    -32.04375 141.56412,0 195.22894,72.75488 336.92846,72.75488 57.54639,0 96.7005,-10.46761 161.28786,\
    -33.42177 V 186.84286 c -46.87209,16.5972 -95.3916,33.42177 -161.28786,33.42177 -0.009,0 0.009,0 0,\
    0 -141.74465,0 -195.45461,-72.75488 -336.92846,-72.75488 -128.85878,0 -181.44038,59.3407 -296.08182,\
    68.43506 v 750.0573 c 0,30.23874 -24.259748,54.56619 -54.161303,54.56619 C 24.259752,1020.5683 0,\
    996.24085 0,966.00211 V 56.566157 C 0,26.418355 24.259752,2 54.161307,2 84.062862,2 108.32261,\
    26.418355 108.32261,56.566157 V 108.83599 C 222.96405,97.809077 275.54565,38.377438 404.40443,\
    38.377438 c 141.65438,0 195.09354,72.754872 336.92846,72.754872 84.85272,0 131.56685,\
    -23.076933 269.67821,-72.754872 z'
]
