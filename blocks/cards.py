from django import forms
from django.forms.utils import ErrorList
from django.utils.functional import cached_property
from django.utils.translation import gettext_lazy as _
from wagtail.blocks import BooleanBlock, ListBlock, StructBlock
from wagtail.blocks.field_block import IntegerBlock
from wagtail.blocks.struct_block import (StructBlockAdapter,
                                         StructBlockValidationError)
from wagtail.telepath import register

from .choices import (BreakpointChoiceBlock, ChoiceBlock,
                      ColourThemeChoiceBlock, FlexCardLayoutChoiceBlock)
from .image import SEOImageChooserBlock
from .link import Link
from .rich_text import RichTextBlock


class SimpleCard(StructBlock):
    background = ColourThemeChoiceBlock(
        default='bg-transparent',
        label=_("Card Background Colour")
    )    
    border = BooleanBlock(
        default=True,
        required=False,
        label=_("Border"),
    )
    rich_text = RichTextBlock(label=_("Text"))

    class Meta:
        template = 'blocks/simple_card_block.html'
        label = _("Text Card")
        label_format = label + ": {text}"
        icon = 'text-card'
        form_classname = "struct-block flex-block simple-card-block"

class SimpleCardBlockAdapter(StructBlockAdapter):        
    @cached_property
    def media(self):
        return forms.Media(
            css={"all": (
                "css/admin/simple-card-block.css",
            )},
        )

register(SimpleCardBlockAdapter(), SimpleCard)

class FlexCard(StructBlock):
    format = FlexCardLayoutChoiceBlock(
        max_length=15,
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
        label=_("Border"),
    )
    rich_text = RichTextBlock(label=_("Text"))
    image = SEOImageChooserBlock(
        label=_("Card Image (approx 1:1.4 ratio - ideally upload 2100x1470px)"),
    )
    image_min = IntegerBlock(
        label=_("Image width min (px)"),
        default=200,
        min_value=100
    )
    image_max = IntegerBlock(
        label=_("Image width max (px)"),
        required=False
    )
    class Meta:
        template = 'blocks/flex_card_block.html'
        label = _("Image & Text Card")
        label_format = label
        icon = 'image-text-card'
        form_classname = "struct-block flex-block flex-card-block"

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

class FlexCardBlockAdapter(StructBlockAdapter):        
    @cached_property
    def media(self):
        return forms.Media(
            css={"all": (
                "css/admin/flex-card-block.css",
            )},
        )

register(FlexCardBlockAdapter(), FlexCard)

class CallToActionCard(FlexCard):
    def __init__(self, required=True, link_required=True, **kwargs):
        local_blocks = (
            ("link", Link(
                label=_("Link Button"),
                required=(required and link_required)
            )),
        )   
        super().__init__(local_blocks, required=required, **kwargs)

    class Meta:
        template = 'blocks/flex_card_block.html'
        label = _("Call-To-Action Card")
        label_format = label
        icon = 'call-to-action'

class CallToActionCardBlockAdapter(StructBlockAdapter):        
    @cached_property
    def media(self):
        return forms.Media(
            css={"all": (
                "css/admin/flex-card-block.css",
            )},
        )

register(CallToActionCardBlockAdapter(), CallToActionCard)

class CardGridBlock(StructBlock):
    format = ChoiceBlock(
        choices=[
            ('grid', _('Standard Grid')),
            ('masonry', _('Masonry Grid')),
        ],
        default='grid'
    )
    min_col = IntegerBlock(
        label=_("Min Columns"), 
        min_value=1,
        max_value=3,
        default=1
        )
    max_col = IntegerBlock(
        label=_("Max Columns"), 
        min_value=1,
        max_value=8,
        default=5
        )

    def clean(self, value):
        errors = {}
        min_col = value.get('min_col')
        max_col = value.get('max_col')

        if min_col > max_col:
            errors['min_col'] = ErrorList([_("Please make sure minimum is less than maximum.")])
            errors['max_col'] = ErrorList([_("Please make sure minimum is less than maximum.")])
        if errors:
            raise StructBlockValidationError(block_errors=errors)

        return super().clean(value)     

class SimpleCardGridBlock(CardGridBlock):
    cards = ListBlock(SimpleCard, min_num=2)

    class Meta:
        template = "blocks/simple_card_grid_block.html"
        icon = 'text-card-grid'
        label = _("Text Card Grid")
        label_format = label
        form_classname = "struct-block flex-block card-grid-block"

class SimpleCardGridBlockAdapter(StructBlockAdapter):        
    @cached_property
    def media(self):
        return forms.Media(
            css={"all": (
                "css/admin/card-grid-block.css",
            )},
        )

register(SimpleCardGridBlockAdapter(), SimpleCardGridBlock)

class SimpleImageCardGridBlock(CardGridBlock):
    cards = ListBlock(CallToActionCard(link_required=False), min_num=2)

    class Meta:
        template = "blocks/simple_card_grid_block.html"
        icon = 'image-card-grid'
        label = _("Image & Text Card Grid")
        label_format = label
        form_classname = "struct-block flex-block card-grid-block"

class SimpleImageCardGridBlockAdapter(StructBlockAdapter):        
    @cached_property
    def media(self):
        return forms.Media(
            css={"all": (
                "css/admin/card-grid-block.css",
            )},
        )

register(SimpleImageCardGridBlockAdapter(), SimpleImageCardGridBlock)
