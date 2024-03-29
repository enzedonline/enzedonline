from django.utils.translation import gettext_lazy as _
from wagtail.blocks import RichTextBlock, StructBlock

from .choices import TextAlignmentChoiceBlock


class RichTextStructBlock(StructBlock):
    alignment = TextAlignmentChoiceBlock(
        default = 'justify',
        label=_("Text Alignment")
    )
    content = RichTextBlock()

    class Meta:
        template = 'blocks/simple_richtext_block.html'
        label = _("Rich Text Block")
        label_format = "RTB: {content}"
        icon = 'pilcrow'
        abstract = True

class SimpleRichTextBlock(RichTextStructBlock):
    pass

class MinimalRichTextBlock(RichTextStructBlock):
    content = RichTextBlock(editor='minimal')

class BasicRichTextBlock(RichTextStructBlock):
    content = RichTextBlock(editor='basic')