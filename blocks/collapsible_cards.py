from django import forms
from django.utils.functional import cached_property
from django.utils.translation import gettext_lazy as _
from wagtail.blocks import CharBlock, ListBlock, StructBlock
from wagtail.blocks.struct_block import StructBlockAdapter
from wagtail.admin.telepath import register

from .choices import ColourThemeChoiceBlock
from .rich_text import RichTextBlock


class CollapsibleCard(StructBlock):
    header = CharBlock(
        label=_("Card Banner Title")
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

class CollapsibleCardBlockAdapter(StructBlockAdapter):        
    @cached_property
    def media(self):
        return forms.Media(
            css={"all": (
                "css/admin/collapsible-card-block.css",
            )},
        )

register(CollapsibleCardBlockAdapter(), CollapsibleCardBlock)