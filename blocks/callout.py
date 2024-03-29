from django.utils.translation import gettext_lazy as _
from wagtail.blocks import CharBlock, ChoiceBlock, StreamBlock, StructBlock

from .code import BlogCodeBlock
from .rich_text import SimpleRichTextBlock


class CalloutHeadingStructBlock(StructBlock):
    icon = ChoiceBlock(
        label=_("Icon"), 
        required=False,
        choices=[
            ('fa-solid fa-triangle-exclamation fa-xl', '⚠ Attention'),
            ('fa-regular fa-pen-to-square fa-xl', '⏍ Note'),
            ('fa-solid fa-circle-info fa-xl', '🛈 Info')
        ],
    )
    text = CharBlock(label=_("Heading Text"), required=False)

    class Meta:
        label = _("Optional Heading")
        form_classname = "struct-block flex-block callout-heading-block"

class CalloutStreamBlock(StreamBlock):
    text = SimpleRichTextBlock()
    code = BlogCodeBlock()

class CalloutBlock(StructBlock):
    heading = CalloutHeadingStructBlock(required=False, label=" ")
    content = CalloutStreamBlock(label=" ")

    class Meta:
        template = "blocks/callout_block.html"
        icon = "warning"
        label = _("Callout Block")
        label_format = _("Callout")