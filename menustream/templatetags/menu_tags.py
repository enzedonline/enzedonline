from django import template
from django.db.models import Q
from django.utils.safestring import mark_safe

from core.utils import strip_svg_markup
from menustream.models import Menu
from site_settings.models import SocialMediaLinks

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
    
    query = Q(live=True)
    # filter by 'Show in Menus' if selected
    if autofill_block['only_show_in_menus']:
        query &= Q(show_in_menus=True)
    # return only public pages if user not authenticated
    if authenticated:
        children = parent_page.get_children().filter(query).order_by(autofill_block['order_by'])
    else:
        children = parent_page.get_children().public().filter(query).order_by(autofill_block['order_by'])

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
def menu_icon(image, rendition_token='fill-25x25|format-png'):
    if image:
        if image.is_svg():
            svg_file = image.file.file
            if svg_file.closed: svg_file.open()
            svg = svg_file.read().decode('utf-8')
            svg_file.close()
            return strip_svg_markup(svg)
        else:
            r = image.get_rendition(rendition_token)
            return r.img_tag()
    return ''


@register.simple_tag(takes_context=True)
def get_social_media_icons(context):
    try:
        request = context['request']
        social_media_icons = []
        links = SocialMediaLinks.for_request(request).social_media_links.all()
        for link in links:
            item = {}
            item['link'] = link.url
            item['image'] = menu_icon(link.logo, 'fill-50x50|format-png')
            item['alt'] = link.site_name
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