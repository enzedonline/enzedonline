from django import forms
from django.utils.functional import cached_property
from django.utils.translation import gettext_lazy as _
from wagtail.admin.telepath import register
from wagtail.blocks import CharBlock, ChoiceBlock, StreamBlock, StructBlock
from wagtail.blocks.struct_block import StructBlockAdapter

from .code import BlogCodeBlock
from .rich_text import RichTextBlock


class CalloutHeadingStructBlock(StructBlock):
    icon = ChoiceBlock(
        label=_("Icon"), 
        required=False,
        choices=[
            ('fa-solid fa-triangle-exclamation fa-xl', '⚠ Attention'),
            ('fa-regular fa-pen-to-square fa-xl', '⏍ Note'),
            ('fa-solid fa-circle-info fa-xl', '🛈 Info'),
            ('fa-regular fa-lightbulb', '💡 Lightbulb')
        ],
    )
    text = CharBlock(label=_("Heading Text"), required=False)

    class Meta:
        label = _("Optional Heading")
        form_classname = "struct-block flex-block callout-heading-block"

class CalloutStreamBlock(StreamBlock):
    rich_text = RichTextBlock()
    code = BlogCodeBlock()

class CalloutBlock(StructBlock):
    heading = CalloutHeadingStructBlock(required=False, label=" ")
    content = CalloutStreamBlock(label=" ")

    class Meta:
        template = "blocks/callout_block.html"
        icon = "warning"
        label = _("Callout Block")
        label_format = _("Callout")

class CalloutBlockAdapter(StructBlockAdapter):        
    @cached_property
    def media(self):
        return forms.Media(
            css={"all": (
                "css/admin/callout-block.css",
            )},
        )

register(CalloutBlockAdapter(), CalloutBlock)