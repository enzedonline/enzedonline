from django.forms.utils import ErrorList
from django.utils.functional import cached_property
from django.utils.translation import gettext_lazy as _
from wagtail.blocks import BooleanBlock, CharBlock, RichTextBlock, StructBlock
from wagtail.blocks.field_block import IntegerBlock, URLBlock
from wagtail.blocks.struct_block import (StructBlockAdapter,
                                         StructBlockValidationError)
from wagtail.admin.telepath import register

from .choices import (AlignmentChoiceBlock, BreakpointChoiceBlock,
                      ButtonChoiceBlock, ButtonSizeChoiceBlock,
                      ColourThemeChoiceBlock, FlexCardLayoutChoiceBlock)


class ExternalLinkEmbedBlock(StructBlock):
    external_link = URLBlock(
        label=_("URL to External Article"),
        help_text=_("Use the 'Get Metadata' button to retrieve information from the external website."),
    )
    image = CharBlock(
        max_length=200, 
        null=True, 
        blank=True,
    )
    description = RichTextBlock(
        null=True, 
        blank=True,
    )
    image_min = IntegerBlock(
        label=_("Minimum image width (px)"),
        default=200,
        min_value=100
    )
    image_max = IntegerBlock(
        label=_("Maximum image width (px)"),
        required=False
    )
    format = FlexCardLayoutChoiceBlock(
        default='vertical',
        label=_("Card Format")
    )    
    breakpoint = BreakpointChoiceBlock(
        default = 'md',
        label=_("Breakpoint for responsive layouts")
    )
    background = ColourThemeChoiceBlock(
        default='bg-transparent',
        label=_("Card Background Colour")
    )
    border = BooleanBlock(
        default=True,
        required=False,
        label=_("Add Border"),
    )
    full_height = BooleanBlock(
        default=True,
        required=False,
        label=_("Full Height"),
    )
    button_text = CharBlock(
        label=_("Button Text"),
        default=_("Read Full Article")
    )
    button_appearance = ButtonChoiceBlock(
        max_length=15,
        default='btn-primary',
        label=_("Button Appearance")
    )
    button_placement = AlignmentChoiceBlock(
        default='end',
        label=_("Button Placement")
    )
    button_size = ButtonSizeChoiceBlock()

    class Meta:
        template='blocks/external_link_embed.html',
        icon = 'link-external'
        label = _("External Article Link")
        label_format = _("External Link") +": {external_link}"
        form_classname = "struct-block flex-block external-link-block"
    
    def clean(self, value):
        errors = {}
        image_min = value.get('image_min')
        image_max = value.get('image_max')
        if image_min and image_max and image_min > image_max:
            errors['image_min'] = ErrorList([_("Please make sure minimum is less than maximum.")])
            errors['image_max'] = ErrorList([_("Please make sure minimum is less than maximum.")])
        if errors:
            raise StructBlockValidationError(block_errors=errors)
        return super().clean(value)

class ExternalLinkEmbedBlockAdapter(StructBlockAdapter):
    js_constructor = "blocks.models.ExternalLinkEmbedBlock"

    @cached_property
    def media(self):
        from django import forms
        structblock_media = super().media
        return forms.Media(
            js=structblock_media._js + ["js/embed-external-link-block.js"],
            css={"all": ("css/embed-external-link-block.css",)},
        )

register(ExternalLinkEmbedBlockAdapter(), ExternalLinkEmbedBlock)