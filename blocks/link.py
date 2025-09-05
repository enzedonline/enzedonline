from django import forms
from django.forms.utils import ErrorList
from django.utils.functional import cached_property
from django.utils.translation import gettext_lazy as _
from wagtail.blocks import (CharBlock, PageChooserBlock, StructBlock,
                            StructValue)
from wagtail.blocks.struct_block import (StructBlockAdapter,
                                         StructBlockValidationError)
from wagtail.models import Locale
from wagtail.telepath import register

from .choices import (AlignmentChoiceBlock, ButtonChoiceBlock,
                      ButtonSizeChoiceBlock)


class Link_Value(StructValue):
    """ Additional logic for the Link class """

    def url(self) -> str:
        internal_page = self.get("internal_page")
        url_link = self.get("url_link")
        if internal_page:
            return internal_page.localized.url
        elif url_link:
            if url_link.startswith('/'): # presumes internal link starts with '/' and no lang code
                url = '/' + Locale.get_active().language_code + url_link
            else:
                url = url_link 
            return url
        else:
            return None

class Link(StructBlock):
    def __init__(self, required=True, **kwargs):
        self._required = required
        local_blocks = (
            ("internal_page", PageChooserBlock(
                label=_("Link to internal page"),
                required=False
            )),
            ("url_link", CharBlock(
                label=_("Link to external site or internal URL"),
                required=False
            )),
            ("button_text", CharBlock(
                label=_("Button Text"),
                required=required
            )),
            ("appearance", ButtonChoiceBlock(
                label=_("Appearance"),
                default='btn-primary',
            )),
            ("placement", AlignmentChoiceBlock(
                label=_("Button Align"),
                default='end',
            )),
            ("size", ButtonSizeChoiceBlock(
                label=_("Size"),
                default=' '
            )),
        )   
        super().__init__(local_blocks, required=required, **kwargs)

    class Meta:
        value_class = Link_Value
        icon = "link"
        template = "blocks/link_button.html"
        label = _("Link")
        label_format = label + ": {button_text}"
        form_classname = "struct-block flex-block link-block"

    def clean(self, value):
        errors = {}
        if self._required:
            internal_page = value.get('internal_page')
            url_link = value.get('url_link')
            if not(bool(internal_page) ^ bool(url_link)):
                errors['internal_page'] = ErrorList([_("Please select an internal page or an external link (but not both)")])
                errors['url_link'] = ErrorList([_("Please select an internal page or an external link (but not both)")])
            if errors:
                raise StructBlockValidationError(block_errors=errors)

        return super().clean(value)

class LinkBlockAdapter(StructBlockAdapter):        
    @cached_property
    def media(self):
        return forms.Media(
            css={"all": (
                "css/admin/link-block.css",
            )},
        )

register(LinkBlockAdapter(), Link)