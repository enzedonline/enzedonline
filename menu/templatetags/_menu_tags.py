from django import template
from wagtail.images.models import Image
from wagtail.models import Locale, Page

from menu.models import Menu
from site_settings.models import SocialMedia


def sub_menu_items(menu, logged_in):
    # return any submenus for the menu instance
    sub_menu_items = []
    for item in menu.sub_menu_items.all():
        if item.show(logged_in):
            sub_menu_items.append({
                'order': item.menu_display_order,
                'submenu_id': item.submenu_id, 
                'is_submenu': True,
                'divider': item.show_divider_after_this_item,
                'display_option': item.display_option,
            })
    return sub_menu_items

def link_menu_items(menu, logged_in):
    #return any links for the menu instance
    link_menu_items = []
    for item in menu.link_menu_items.all():
        if item.show(logged_in): # authentication status of user matches item 'show_when' property
            if item.link_page: # link is to internal page (not url)
                trans_page = item.link_page.localized # get translated page if any
                if not item.title: # no title set in menu item, use page title
                    item.title = trans_page.title
                url = str(trans_page.url)
                if item.link_url: # anything in url field to be treated as suffix (eg /?cat=news)
                    url = url + str(item.link_url)
            else: # not a page link, test if internal or external url, translate if internal
                if item.link_url.startswith('/'): # presumes internal link starts with '/' and no lang code
                    url = '/' + Locale.get_active().language_code + item.link_url
                else: # external link, do nothing
                    url = item.link_url                
            link_menu_items.append({
                'order': item.menu_display_order,
                'title': item.title, 
                'url': url,
                'icon': item.icon,
                'is_submenu': False,
                'divider': item.show_divider_after_this_item,
            })
    return link_menu_items

def autofill_menu_items(menu, logged_in):
    autofill_menu_items = []
    for item in menu.autofill_menu_items.all():
        if item.show(logged_in): # authentication status of user matches item 'show_when' property
            trans_page = item.link_page.localized # get translated page if any
            if trans_page:
                if item.include_linked_page: # show linked page as well as any results
                    autofill_menu_items.append({
                        'order': item.menu_display_order,
                        'title': trans_page.title, 
                        'url': trans_page.url,
                        'is_submenu': False,
                        'divider': True,
                    })
                # return only public pages if user not logged in
                if logged_in:
                    list = trans_page.get_children().live().order_by(item.order_by)
                else:
                    list = trans_page.get_children().live().public().order_by(item.order_by)
                # filter by 'Show In Menu' if selected
                if item.only_show_in_menus:
                    list = list.filter(show_in_menus=True)
                # limit list to maximum set in menu item
                list = list[:item.max_items]
                # add results (if any) to menu items
                if list:
                    i = 0
                    for result in list:
                        autofill_menu_items.append({
                            'order': item.menu_display_order + i/(item.max_items + 1),
                            'title': result.title, 
                            'url': result.url,
                            'is_submenu': False,                            
                        })
                        i+=1
                    # if add divider selected, add to last item only
                    autofill_menu_items[-1]['divider'] = item.show_divider_after_this_item
    return autofill_menu_items

register = template.Library()

@register.simple_tag()
def get_menu_items(menu, request):
    # returns a list of dictionaries with title, url, page and icon of all items in the menu
    # use get_menu first to load the menu object then pass that instance to this function


    if not request: # 500 error has no request
        authenticated = False
    else:
        authenticated = request.user.is_authenticated

    if not isinstance(menu, Menu):
        if isinstance(menu, int):
            # menu id supplied instead of menu instance
            menu = get_menu(menu)
        if menu == None:
            # couldn't load menu, return nothing
            return None
    
    # gather all menu item types, sort by menu_display_order at the end
    # create a list of all items that should be shown in the menu depending on logged_in
    menu_items = [] + \
                 sub_menu_items(menu, authenticated) + \
                 link_menu_items(menu, authenticated) + \
                 autofill_menu_items(menu, authenticated)

    # if no menu items to show, return None
    if menu_items.__len__() == 0:
        return None

    # sort menu items by common 'order' field
    menu_items = sorted(menu_items, key=lambda k: k['order'])

    return menu_items

@register.simple_tag()
def get_menu(menu_title):
    # return the localized menu instance for a given id or title, or none if no such menu exists
    try:
        if isinstance(menu_title, int):
            return Menu.objects.all().filter(id=menu_title).first().localized 
        else:
            return Menu.objects.all().filter(title=menu_title).first().localized 
    except (AttributeError, Menu.DoesNotExist):
        return None
    
@register.simple_tag()
def language_switcher(page):
    # Build the language switcher, including the href alternate links for SEO
    default_lang = Locale.get_default()
    current_lang = Locale.get_active()

    switch_pages = []
    for locale in Locale.objects.all():
        try:
            if page.has_translation(locale=locale):
                trans_page = page.get_translation(locale=locale)
            else:
                trans_page = page
            # bug when run in debug mode on the server, page is none for some reason
            if trans_page:
                next_url = '/?next=' + trans_page.url
            else:
                next_url = '/?next=/'
        except AttributeError:
            next_url = ''
        if not locale == current_lang: # add the link to switch language and also alternate link
            switch_pages.append(
                {
                    'language': locale, 
                    'url': '/lang/' + locale.language_code + next_url,
                    'flag': get_lang_flag(locale.language_code),
                    'alternate': alternate_link
                }
            )
    return switch_pages

@register.simple_tag()
def get_lang_flag(language_code=None):
    # returns the flag icon for the menu 
    # upload flag image to wagtail, set title to flag-lang (eg flag-fr, flag-en)
    # if no language code supplied, assumes current language
    if not language_code:
        language_code = Locale.get_active().language_code
    return Image.objects.all().filter(title='flag-' + language_code).first()

@register.simple_tag()
def get_social_media_icons():
    try:
        social_media_icons = []
        icons = SocialMedia.objects.all().filter(locale_id=1)
        for icon in icons:
            item = {}
            locale_icon = icon.localized
            item['link'] = locale_icon.url
            item['image'] = locale_icon.photo.get_rendition('fill-50x50').url
            item['alt'] = locale_icon.site_name
            social_media_icons.append(item)
        return social_media_icons
    except:
        return None
