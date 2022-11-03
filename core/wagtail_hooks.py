from django.http import HttpResponse
from django.urls import reverse
from django.utils.translation import gettext_lazy as _
from wagtail import hooks
from wagtail.admin.menu import MenuItem

from .draftail_extensions import (DRAFTAIL_ICONS,
                                  register_block_feature,
                                  register_inline_styling)
from .utils import purge_page_cache_fragments
from .thumbnails import ThumbnailOperation

@hooks.register('register_image_operations')
def register_image_operations():
    return [
        ('thumbnail', ThumbnailOperation)
    ]

@hooks.register('register_rich_text_features')
def register_align_left_feature(features):
    register_block_feature(
        features=features,
        feature_name='left-align',
        type_='left-align',
        description=_('Left align text'),
        css_class='text-start',
        element='p',
        icon=DRAFTAIL_ICONS.left_align
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
        icon=DRAFTAIL_ICONS.centre_align
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
        icon=DRAFTAIL_ICONS.right_align
    )

@hooks.register('register_rich_text_features')
def register_code_block_feature(features):
    register_block_feature(
        features=features,
        feature_name='code-block',
        type_='CODE-BLOCK',
        description='Code Block',
        css_class='code-block',
        element='div',
        icon=DRAFTAIL_ICONS.code_block
    )
    
@hooks.register("register_rich_text_features")
def register_fa_styling(features):
    """Add <fa> to the richtext editor and page."""
    register_inline_styling(
        features=features,
        feature_name='fa',
        description="Font Awesome Icon",
        type_="FA",
        tag="fa",
        format='style="display:none;"',
        editor_style={            
            'background-color': 'orange',            
            'color': '#666',
            'font-family': 'monospace',
            'font-size': '0.9rem',
            'font-weight': 'bolder',
            'padding': '0 0.4rem',
            'border-radius': '0.6rem'
        },
        icon=DRAFTAIL_ICONS.font_awesome
    )

@hooks.register("register_rich_text_features")
def register_smaller_styling(features):
    register_inline_styling(
        features=features,
        feature_name='smaller',
        type_='SMALLER',
        tag='span',
        format='style="font-size:smaller"',
        editor_style={'font-size':'smaller'},
        description='Decrease Font',
        icon=DRAFTAIL_ICONS.decrease_font
    )

@hooks.register("register_rich_text_features")
def register_larger_styling(features):
    register_inline_styling(
        features=features,
        feature_name='larger',
        type_='LARGER',
        tag='span',
        format='style="font-size:larger"',
        editor_style={'font-size':'larger'},
        description='Increase Font',
        icon=DRAFTAIL_ICONS.increase_font
    )

@hooks.register("register_rich_text_features")
def register_underline_styling(features):
    register_inline_styling(
        features=features,
        feature_name='underline',
        type_='UNDERLINE',
        tag='u',
        description='Underline',
        icon=DRAFTAIL_ICONS.underline
    )

@hooks.register('register_rich_text_features')
def register_highlighted_text_feature(features):
    register_inline_styling(
        features=features,
        feature_name='highlight',
        type_='HIGHLIGHT',
        format='style="background-color: yellow;padding-left: 0.15rem;padding-right: 0.15rem;"',
        editor_style={'background-color': 'yellow', 'padding-left': '0.15rem', 'padding-right': '0.15rem'},
        description='Highlighted Text',
        icon=DRAFTAIL_ICONS.highlighter,
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


    