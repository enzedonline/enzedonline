from django import template
from site_settings.models import SiteTokens

register = template.Library()

@register.simple_tag(takes_context=True)
def facebook_js_sdk(context, embed_code):
    # Check if the embed code is a Facebook post embed code
    try:
        post_class = embed_code.split()[1]
        if (post_class[:10] =='class="fb-'):
            request = context['request']
            site_tokens = SiteTokens.for_request(request)
            if site_tokens and site_tokens.javascript_sdk:
                return site_tokens.javascript_sdk
        else:
            return ''
    except:
        return ''