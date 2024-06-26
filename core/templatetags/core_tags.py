import re
from datetime import datetime
from urllib.parse import urlparse

from django import template
from django.conf import settings
from django.utils.safestring import mark_safe
from django.utils.text import normalize_newlines
from wagtail.admin.templatetags.wagtailadmin_tags import render_with_errors
from wagtail.documents.models import Document
from wagtail.models import Page

from site_settings.models import CompanyLogo, EmailSignature, TemplateText

register = template.Library()

@register.filter(name='is_in_group') 
def is_in_group(user, group_name):
    if user.id==None:
        return False
    else:
        return user.groups.get_queryset().filter(name=group_name).exists() 

@register.filter()
def strip_newlines(text):
    return re.sub(" +", " ", normalize_newlines(text).replace('\n', ' '))

@register.filter(name='remove')
def remove(value, arg):
    """
    Replace all occurrences of arg with an empty string.
    """
    return value.replace(arg, '')

@register.filter()
def replace_doublequotes(text):
    return text.replace('"', '\'')

@register.simple_tag()
def trans_url(link):
    return link.localized.url

@register.simple_tag()
def get_setting(key):
    return getattr(settings, key, '')

@register.simple_tag()
def trans_page_from_slug(slug, specific=False):
    try:
        if specific:
            return Page.objects.live().filter(slug=slug).first().specific.localized
        else:
            return Page.objects.live().filter(slug=slug).first().localized
    except:
        return Page.objects.none()

@register.filter()
def homepage_url(request):
    try:
        return request._wagtail_site.root_page.localized.url
    except:
        '/'

@register.filter()
def doc_title_to_url(title):
    try:
        document = Document.objects.get(title=title)
        return document.url
    except:
        pass
    
@register.simple_tag(takes_context=True)
def robots(context):
    page = get_context_var_or_none(context, 'self')
    if not (page and page.search_engine_index):
        return mark_safe('<meta name="robots" content="noindex">')
    return mark_safe('<meta name="robots" content="index, follow, archive, imageindex, noodp, noydir, snippet, translate, max-snippet:-1, max-image-preview:large, max-video-preview:-1">')

@register.simple_tag(takes_context=True)
def canonical(context):
    page = get_context_var_or_none(context, 'self')
    page_type = type(page).__name__
    if not page: # not a wagtail page, not indexed, return empty string
        return ''
    if page_type == 'HomePage': # drop /en from homepage canonical
        href = f'{page.get_url_parts()[1]}/'
    else:
        href = page.full_url
    # add pagination for blog posts if any 
    pagination = get_context_var_or_none(context, 'posts')
    if pagination and pagination.number > 1:
        href += f'?page={pagination.number}'
    return mark_safe(f'<link rel="canonical" href="{href}">')

@register.simple_tag(takes_context=True)
def get_cache_key_settings(context):
    page = get_context_var_or_none(context, 'self')
    cache = {'cache_head': context.get('cache_head', 'head')}
    if not page:
        cache['cache_name'] = '_DynamicPage'
        cache['cache_date'] = datetime.now()
    else:
        cache['cache_name'] = get_context_var_or_none(context, 'cache_name')
        cache['cache_date'] = get_context_var_or_none(context, 'cache_date')
    return cache

@register.simple_tag()
def paginator_filter(filter):
    if filter:
        return filter + '&'
    else:
        return '?'
    
@register.simple_tag(takes_context=True)
def search_paginator_filter(context):
    search_query = context.request.GET.get('query', None)
    search_order = context.request.GET.get('order', None)
    return f'?query={search_query}{("&order=" + search_order) if search_order else ""}&'

@register.simple_tag()
def get_template_set(set):
    try:
        template_set = TemplateText.objects.filter(template_set=set).first()
        if template_set:
            items = template_set.localized.templatetext_items.all()
            if items:
                text_dict = {}
                for i in items:
                    text_dict[i.template_tag] = i.text
                return text_dict
        return TemplateText.objects.none()
                
    except (AttributeError, TemplateText.DoesNotExist):
        return TemplateText.objects.none()    

@register.simple_tag()
def get_email_signature(signature):
    try:
        signature = EmailSignature.objects.filter(signature_name=signature).first()
        return signature.localized  if signature else EmailSignature.objects.none()
                
    except (AttributeError, EmailSignature.DoesNotExist):
        return EmailSignature.objects.none()    

@register.simple_tag(takes_context=True)
def var_exists(context, name):
    dicts = context.dicts  # array of dicts
    if dicts:
        for d in dicts:
            if name in d:
                return True
    return False

@register.simple_tag(takes_context=True)
def get_context_var_or_none(context, name):
    dicts = context.dicts  # array of dicts
    if dicts:
        for d in dicts:
            if name in d:
                return d[name]
    return None

# modified version of get_context_var_or_none to get search context if exists without throwing error if not
# {% if context_var %} throws an error in logs if var doesn't exist
@register.simple_tag(takes_context=True)
def get_search_or_none(context):
    dicts = context.dicts  # array of dicts
    if dicts:
        for d in dicts:
            if 'search_query' in d:
                return d['search_query']
    return ''

@register.simple_tag()
def get_rendition(image, image_options):
    return image.get_rendition(image_options)

@register.simple_tag()
def get_picture_rendition(image, width):
    if width < image['file'].width:
        return image['file'].get_rendition(f"width-{width}|format-webp")
    else:
        return image['file'].get_rendition("original|format-webp")

@register.simple_tag()
def get_logo(logo):
    try:
        logo = CompanyLogo.objects.filter(name=logo).first()
        return logo.localized.logo if logo else CompanyLogo.objects.none()
                
    except (AttributeError, CompanyLogo.DoesNotExist):
        return CompanyLogo.objects.none()    

@register.simple_tag(takes_context=True)
def get_referrer_or_none(context):
    try:
        referer = context['request'].META.get('HTTP_REFERER', False)
        return urlparse(referer).path
    except:
        return '/'

@register.filter()
def checkbox_checked(checkbox):
    return mark_safe(str(checkbox)[:-1] + " checked>")
