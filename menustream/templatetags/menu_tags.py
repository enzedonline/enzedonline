from django import template
from django.utils.safestring import mark_safe

from core.utils import strip_svg_markup
from menustream.models import Menu

register = template.Library()

@register.simple_tag()
def load_menu(menu_slug):
    try:
        return Menu.objects.filter(slug=menu_slug).first().localized
    except:
        return Menu.objects.filter(slug=menu_slug).first()
   
@register.simple_tag(takes_context=True)
def show_on_menu(context, item):
    display_when = item.get('display_when', getattr(item, 'display_when', True)) # If not specified, only show if user is authenticated.
    if not context.get('request', None):
        authenticated = False
    else:        
        authenticated = str(context['request'].user.is_authenticated)
    return (display_when == 'ALWAYS' or authenticated == display_when)

@register.simple_tag(takes_context=True)
def link_active(context, link):
    return ' active' if (getattr(link, 'url', None) == getattr(context.get('request', None), 'path', None)) else ''

@register.simple_tag(takes_context=True)
def get_autofill_pages(context):
    autofill_block = context['self']
    links=[]

    try:
        authenticated = context['request'].user.is_authenticated
    except: # 500 error has no request
        authenticated = False

    parent_page = autofill_block['parent_page']
    if not parent_page:
        return []
    else:
        parent_page = parent_page.localized

    # include parent page if selected and if matches restriction (just assume exists=private here)
    if autofill_block['include_parent_page']:
        if parent_page.url == getattr(context.get('request', None), 'path', None):
            parent_page.active = 'active'
        if parent_page.get_view_restrictions().exists():
            if authenticated:
                links.append(parent_page)
        else:
            links.append(parent_page)
    
    # return only public pages if user not authenticated
    if authenticated:
        children = parent_page.get_children().live().order_by(autofill_block['order_by'])
    else:
        children = parent_page.get_children().live().public().order_by(autofill_block['order_by'])

    # filter by 'Show in Menus' if selected
    if autofill_block['only_show_in_menus']:
        children = children.filter(show_in_menus=True)

    for child in children[:autofill_block['max_items']]:
        if child.url == getattr(context.get('request', None), 'path', None):
            child.active = 'active'
        links.append(child)

    return links

@register.simple_tag(takes_context=True)
def render_user_info(context, msg):
    user = getattr(context.get('request', None), 'user', None)
    if not user:
        msg = ''
    elif "@username" in msg:
        msg = msg.replace("@username", user.username)
    elif "@display_name" in msg:
        msg = msg.replace("@display_name", user.display_name or user.get_full_name())
    return msg

@register.simple_tag()
@mark_safe
def menu_icon(image, redition_token='fill-25x25|format-png'):
    if image:
        if image.is_svg():
            svg_file = image.file.file
            if svg_file.closed: svg_file.open()
            svg = svg_file.read().decode('utf-8')
            svg_file.close()
            return strip_svg_markup(svg)
        else:
            r = image.get_rendition(redition_token)
            return r.img_tag()
    return ''


@register.simple_tag()
def get_social_media_icons():
    from site_settings.models import SocialMedia
    try:
        social_media_icons = []
        icons = SocialMedia.objects.filter(locale_id=1)
        for icon in icons:
            item = {}
            locale_icon = icon.localized
            item['link'] = locale_icon.url
            item['image'] = menu_icon(locale_icon.photo, 'fill-50x50|format-png')
            item['alt'] = locale_icon.site_name
            social_media_icons.append(item)
        return social_media_icons
    except:
        return None

@register.simple_tag(takes_context=True)
def get_cache_fragment(context, slug):
    user = getattr(context.get('request', None), 'user', None)
    if user and hasattr(user, 'username'):
        return slug +'-' + user.username
    else:
        return slug +'-'