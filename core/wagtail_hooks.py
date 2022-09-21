from django.http import HttpResponse
from django.urls import reverse
from django.utils.translation import gettext_lazy as _
from wagtail import hooks
from wagtail.admin.menu import MenuItem
from wagtail.admin.rich_text.converters.html_to_contentstate import \
    InlineStyleElementHandler
from wagtail.admin.rich_text.editors.draftail.features import \
    InlineStyleFeature

from .draftail_extensions import (CENTRE_ALIGN_ICON, LEFT_ALIGN_ICON,
                                  MINIMISE_ICON, RIGHT_ALIGN_ICON, SMALL_FONT_ICON,
                                  UNDERLINE_ICON, FONT_AWESOME_ICON,
                                  register_block_feature,
                                  register_inline_styling)
from .utils import purge_page_cache_fragments


@hooks.register('register_rich_text_features')
def register_align_left_feature(features):
    register_block_feature(
        features=features,
        feature_name='left-align',
        type_='left-align',
        description=_('Left align text'),
        css_class='text-start',
        element='p',
        icon=LEFT_ALIGN_ICON
    )
    
@hooks.register('register_rich_text_features')
def register_align_centre_feature(features):
    register_block_feature(
        features=features,
        feature_name='centre-align',
        type_='centre-align',
        description=_('Centre align text'),
        css_class='text-center',
        element='p',
        icon=CENTRE_ALIGN_ICON
    )
    
@hooks.register('register_rich_text_features')
def register_align_right_feature(features):
    register_block_feature(
        features=features,
        feature_name='right-align',
        type_='right-align',
        description=_('Right align text'),
        css_class='text-end',
        element='p',
        icon=RIGHT_ALIGN_ICON
    )
    
@hooks.register("register_rich_text_features")
def register_fa_styling(features):
    """Add <fa> to the richtext editor and page."""

    feature_name = "fa"
    type_ = "FA"
    tag = "fa"

    control = {
        "type": type_,
        "icon": FONT_AWESOME_ICON,
        "description": "Font Awesome",
        'style': {            
            'background-color': 'orange',            
            'color': '#666',
            'font-family': 'monospace',
            'font-size': '0.9rem',
            'font-weight': 'bolder',
            'padding-left': '2px',
            'padding-right': '4px'
        }    
    }

    features.register_editor_plugin(
        "draftail", feature_name, InlineStyleFeature(control)
    )

    db_conversion = {
        "from_database_format": {tag: InlineStyleElementHandler(type_)},
        "to_database_format": {"style_map": {type_: {"element": tag + ' style="display:none;"'}}}
    }

    features.register_converter_rule("contentstate", feature_name, db_conversion)
    features.default_features.append(feature_name)

@hooks.register("register_rich_text_features")
def register_small_styling(features):
    register_inline_styling(
        features=features,
        feature_name='small',
        type_='SMALL',
        tag='small',
        description='Small',
        icon=SMALL_FONT_ICON
    )

@hooks.register("register_rich_text_features")
def register_underline_styling(features):
    register_inline_styling(
        features=features,
        feature_name='underline',
        type_='UNDERLINE',
        tag='u',
        description='Underline',
        icon=UNDERLINE_ICON
    )

@hooks.register('before_serve_document')
def serve_pdf(document, request):
    if document.file_extension != 'pdf':
        return  # Empty return results in the existing response
    response = HttpResponse(document.file.read(), content_type='application/pdf')
    response['Content-Disposition'] = 'filename="' + document.file.name.split('/')[-1] + '"'
    if request.GET.get('download', False) in [True, 'True', 'true']:
        response['Content-Disposition'] = 'attachment; ' + response['Content-Disposition']
    return response

@hooks.register('register_settings_menu_item')
def register_refresh_cache_menu_item():
    return MenuItem(_('Empty Cache'), reverse('refresh-page-cache'), classnames='icon icon-bin', order=1)

@hooks.register('after_delete_page')
def do_after_delete_page(request, page):
    purge_page_cache_fragments(page.slug)

