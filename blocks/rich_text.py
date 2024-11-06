from django.utils.translation import gettext_lazy as _
from wagtail.blocks import RichTextBlock as WagtailRichTextBlock
from wagtail.blocks import StructBlock

from .choices import TextAlignmentChoiceBlock


class RichTextBlock(WagtailRichTextBlock):
    class Meta:
        template = "blocks/richtext_block.html"
        label = _("Rich Text Block")
        label_format = 'RTB: {content}'    

class RichTextStructBlock(StructBlock):
    alignment = TextAlignmentChoiceBlock(
        default = 'justify',
        label=_("Text Alignment")
    )
    content = RichTextBlock(label="OLD", required=False)

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