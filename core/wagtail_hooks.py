from django.conf import settings
from django.http import HttpResponse
from django.templatetags.static import static
from django.urls import reverse
from django.utils.safestring import mark_safe
from django.utils.translation import gettext_lazy as _
from wagtail import hooks
from wagtail.admin.menu import MenuItem

from .documents.views.chooser import viewset as document_chooser_viewset
from .draftail_extensions import (register_block_feature,
                                  register_inline_styling)
from .thumbnails import ThumbnailOperation
from .utils import get_custom_icons, purge_page_cache_fragments


@mark_safe
@hooks.register('insert_global_admin_css')
def global_admin_css():
    css = ""
    for css_file in ['css/admin.css']:
        css += f'<link rel="stylesheet" href="{static(css_file)}">'
    return css

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
        description='Left align text',
        css_class='text-start',
        element='p',
        icon='left-align'
    )
    
@hooks.register('register_rich_text_features')
def register_align_centre_feature(features):
    register_block_feature(
        features=features,
        feature_name='centre-align',
        type_='centre-align',
        description='Centre align text',
        css_class='text-center',
        element='p',
        icon='centre-align'
    )
    
@hooks.register('register_rich_text_features')
def register_align_right_feature(features):
    register_block_feature(
        features=features,
        feature_name='right-align',
        type_='right-align',
        description='Right align text',
        css_class='text-end',
        element='p',
        icon='right-align'
    )

@hooks.register('register_rich_text_features')
def register_code_block_feature(features):
    register_block_feature(
        features=features,
        feature_name='code-block',
        type_='CODE-BLOCK',
        element='li',
        wrapper='ul class="code-block-wrapper"',
        description='Code Block',
        css_class='code-block',
        icon='code-block'
    )

@hooks.register('register_rich_text_features')
def register_checklist_feature(features):
    register_block_feature(
        features=features,
        feature_name='checklist',
        type_='checklist',
        description='Check List',
        css_class='check-list',
        element='li',
        wrapper="ul class='check-list-wrapper' role='list'",
        icon="tasks"
    )

@hooks.register("register_rich_text_features")
def register_fa_styling(features):
    """Add font-awesome icons to the richtext editor and page."""
    register_inline_styling(
        features=features,
        feature_name='fa',
        description="Font Awesome Icon",
        type_="FA",
        format='class="fa-icon"',
        editor_style={            
            'background-color': 'orange',            
            'color': '#666',
            'font-family': 'monospace',
            'font-size': '0.9rem',
            'font-weight': 'bolder',
            'padding': '0 0.4rem',
            'border-radius': '0.6rem'
        },
        icon='font-awesome'
    )

@hooks.register("register_rich_text_features")
def register_smaller_styling(features):
    register_inline_styling(
        features=features,
        feature_name='smaller',
        type_='SMALLER',
        tag='span',
        format='style="font-size:smaller;"',
        editor_style={'font-size':'smaller'},
        description='Decrease Font',
        icon='decrease-font'
    )

@hooks.register("register_rich_text_features")
def register_larger_styling(features):
    register_inline_styling(
        features=features,
        feature_name='larger',
        type_='LARGER',
        tag='span',
        format='style="font-size:larger;"',
        editor_style={'font-size':'larger'},
        description='Increase Font',
        icon='increase-font'
    )

@hooks.register("register_rich_text_features")
def register_underline_styling(features):
    register_inline_styling(
        features=features,
        feature_name='underline',
        type_='UNDERLINE',
        tag='u',
        description='Underline',
        icon='underline'
    )

@hooks.register('register_rich_text_features')
def register_highlighted_text_feature(features):
    register_inline_styling(
        features=features,
        feature_name='highlight',
        type_='HIGHLIGHT',
        format='style="background-color: yellow;padding-left: 0.15rem;padding-right: 0.15rem;"',
        editor_style={'background-color': 'yellow', 'padding-left': '0.15rem', 'padding-right': '0.15rem', 'color': 'var(--bs-dark)'},
        description='Highlighted Text',
        icon='highlighter'
    )

@hooks.register('register_rich_text_features')
def register_code_text_feature(features):
    register_inline_styling(
        features=features,
        feature_name='inline-code',
        type_='CODE',
        tag='code',
        format='class="inline-code"',
        editor_style={'font-size': '.9em', 'font-family': 'var(--font-family-monospace)', 'color': 'darkslateblue', 'background-color': 'oldlace', 'padding': '0.02em 0.3em', 'border-radius': '0.3rem'},
        description='Inline Code',
        icon='code',
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
    return MenuItem(_('Empty Cache'), reverse('refresh-page-cache'), icon_name='bin', order=1)

@hooks.register('after_delete_page')
def do_after_delete_page(request, page):
    purge_page_cache_fragments(page.slug)

@hooks.register("register_icons")
def register_icons(icons):
    return icons + get_custom_icons()
    
@hooks.register("register_admin_viewset")
def register_document_chooser_viewset():
    return document_chooser_viewset