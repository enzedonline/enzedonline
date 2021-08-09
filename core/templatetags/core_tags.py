from datetime import datetime

from django import template
from django.utils.html import mark_safe
from site_settings.models import TemplateText
from wagtail.admin.templatetags.wagtailadmin_tags import render_with_errors
from wagtail.core.models import Page

register = template.Library()

@register.simple_tag()
def trans_url(link):
    return link.localized.url

@register.simple_tag()
def trans_page_from_slug(slug, specific=False):
    try:
        if specific:
            return Page.objects.get(slug=slug).specific.localized
        else:
            return Page.objects.get(slug=slug).localized
    except Page.DoesNotExist:
        return Page.objects.none()

@register.simple_tag()
def get_cache_key_settings(page):
    if not page:
        page = {}
        page['slug'] = '_DynamicPage'
        page['last_published_at'] = datetime.now()
    return page

@register.simple_tag()
def paginator_filter(filter):
    if filter:
        return filter + '&'
    else:
        return '?'

@register.simple_tag()
def get_template_set(set):
    try:
        template_set = TemplateText.objects.all().filter(template_set=set).first().localized 
        if template_set:
            items = template_set.templatetext_items.all()
            if items:
                text_dict = {}
                for i in items:
                    text_dict[i.template_tag] = i.text
                return text_dict
        return TemplateText.objects.none()
                
    except (AttributeError, TemplateText.DoesNotExist):
        return TemplateText.objects.none()    

@register.simple_tag()
def regex_render_with_errors(bound_field):
    id = bound_field.auto_id
    rendered_field = render_with_errors(bound_field)
    if f'id="{id}"' in rendered_field:
        fn = id.replace('-','_')
        script = f' onkeydown="return keydownhandler_{fn}(event)">\
        <script>function keydownhandler_{fn}(event) \
            {{if (!(/{bound_field.field.pattern}/.test(event.key))){{\
                return false;}} }} \
        </script>'       
        return mark_safe(rendered_field.replace('>', script))
    return rendered_field

@register.simple_tag()
def panel(panel):
    print(panel.__dir__())