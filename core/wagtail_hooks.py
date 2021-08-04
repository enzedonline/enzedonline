from django.urls import reverse
from django.utils.translation import gettext_lazy as _
from wagtail.admin.menu import MenuItem
from wagtail.admin.rich_text.converters.html_to_contentstate import \
    InlineStyleElementHandler
from wagtail.admin.rich_text.editors.draftail import \
    features as draftail_features
from wagtail.core import hooks

from .utils import purge_page_cache_fragments


@hooks.register('register_settings_menu_item')
def register_refresh_cache_menu_item():
    return MenuItem(_('Empty Cache'), reverse('refresh-page-cache'), classnames='icon icon-bin', order=1)

@hooks.register('after_delete_page')
def do_after_page_create(request, page):
    purge_page_cache_fragments(page.slug)

@hooks.register("register_rich_text_features")
def register_code_styling(features):
    """Add the <small> to the richtext editor and page."""

    # Step 1
    feature_name = "small"
    type_ = "SMALL"
    tag = "small"

    # Step 2
    control = {
        "type": type_,
        "label": "Small",
        "description": "Small"
    }

    # Step 3
    features.register_editor_plugin(
        "draftail", feature_name, draftail_features.InlineStyleFeature(control)
    )

    # Step 4
    db_conversion = {
        "from_database_format": {tag: InlineStyleElementHandler(type_)},
        "to_database_format": {"style_map": {type_: {"element": tag}}}
    }

    # Step 5
    features.register_converter_rule("contentstate", feature_name, db_conversion)

    # Step 6. This is optional
    # This will register this feature with all richtext editors by default
    features.default_features.append(feature_name)

@hooks.register("register_rich_text_features")
def register_code_styling(features):
    """Add the <code> to the richtext editor and page."""

    # Step 1
    feature_name = "code"
    type_ = "CODE"
    tag = "code"

    # Step 2
    control = {
        "type": type_,
        "label": "</>",
        "description": "Code"
    }

    # Step 3
    features.register_editor_plugin(
        "draftail", feature_name, draftail_features.InlineStyleFeature(control)
    )

    # Step 4
    db_conversion = {
        "from_database_format": {tag: InlineStyleElementHandler(type_)},
        "to_database_format": {"style_map": {type_: {"element": tag}}}
    }

    # Step 5
    features.register_converter_rule("contentstate", feature_name, db_conversion)

    # Step 6. This is optional
    # This will register this feature with all richtext editors by default
    features.default_features.append(feature_name)
