from django.utils.translation import gettext_lazy as _
from wagtail.blocks import CharBlock, ListBlock, StructBlock

from .choices import ColourThemeChoiceBlock
from .rich_text import SimpleRichTextBlock, RichTextBlock


class CollapsibleCard(StructBlock):
    header = CharBlock(
        label=_("Card Banner Title")
    )
    text = SimpleRichTextBlock(
        label="OLD",
        required=False
    )
    rich_text = RichTextBlock(label=_("Text"))

class CollapsibleCardBlock(StructBlock):
    header_colour  = ColourThemeChoiceBlock(
        default='bg-dark',
        label=_("Header Colour")
    )    
    body_colour  = ColourThemeChoiceBlock(
        default='bg-light',
        label=_("Body Colour")
    )
    cards = ListBlock(CollapsibleCard)

    class Meta:
        template='blocks/collapsible_card_block.html'
        icon="collapse-down"
        label = _("Collapsible Text Block")
        label_format = label
        form_classname = "struct-block flex-block collapsible-card-block"

