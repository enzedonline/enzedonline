from django import template
from site_settings.models import Facebook_Script_Src

register = template.Library()

@register.simple_tag()
def facebook_js_sdk(embed_code):
    post_class = embed_code.split()[1]
    try:
        if (post_class[:10] =='class="fb-'):
            return Facebook_Script_Src.objects.first().javascript_sdk
        else:
            return ''
    except:
        return ''