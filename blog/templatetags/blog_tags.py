from django import template
from wagtail.models import Page, Locale

register = template.Library()

@register.simple_tag()
def translate_categories(categories):
    if categories:
        cat_list = []
        for category in categories:
            trans = category.localized
            cat_list.append({'name': trans.name, 'slug': trans.slug})
        return cat_list
    else:
        return None
    
@register.simple_tag()
def get_tags(page):
    active_lang = Locale.get_active()
    default_lang = Locale.get_default()

    if active_lang == default_lang:
        return page.tags.all()
    else:
        def_lang_page = page.get_translation(locale=default_lang)
        return def_lang_page.tags.all()