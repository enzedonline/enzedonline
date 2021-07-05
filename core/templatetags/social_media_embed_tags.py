from django import template

from core import tags

register = template.Library()

@register.simple_tag()
def is_facebook(embed_code):
    try:
        return (embed_code.split()[1]=='class="fb-post"')
    except:
        return False