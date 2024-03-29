from django.forms.utils import ErrorList
from django.utils.translation import gettext_lazy as _
from wagtail.blocks import BooleanBlock, IntegerBlock, StructBlock
from wagtail.blocks.struct_block import StructBlockValidationError

from ..choices import DefaultChoiceBlock
from .base import BaseStreamBlock


#-----------------------------------------------------
# GridStream options
#-----------------------------------------------------
    
class TwoColumnCollapseOrderChoiceBlock(DefaultChoiceBlock):
    default='left-first'
    choices=[
        ('left-first', _("Left first")),
        ('right-first', _("Right first")),
    ]
    label=_("Column order on mobile")
    
class TwoColumnHideChoiceBlock(DefaultChoiceBlock):
    default='hide-none'
    choices=[
        ('hide-none', _("Display both columns")),
        ('hide-left', _("Hide left column")),
        ('hide-right', _("Hide right column")),
    ]
    label=_("Mobile display behaviour")

class TwoColumnLayoutChoiceBlock(DefaultChoiceBlock):
    choices = [
        ('auto-', _("Left atuo width")),
        ('-auto', _("Right auto width")),
        ('1-11', _("Left 1, Right 11")),
        ('2-10', _("Left 2, Right 10")),
        ('3-9', _("Left 3, Right 9")),
        ('4-8', _("Left 4, Right 8")),
        ('5-7', _("Left 5, Right 7")),
        ('6-6', _("Left 6, Right 6")),
        ('7-5', _("Left 7, Right 5")),
        ('8-4', _("Left 8, Right 4")),
        ('9-3', _("Left 9, Right 3")),
        ('10-2', _("Left 10, Right 2")),
        ('11-1', _("Left 11, Right 1")),
    ]
    default = '6-6',
    label = _("Select column size ratio")

class ThreeColumnHideChoiceBlock(DefaultChoiceBlock):
    default='hide-none'
    choices=[
        ('hide-none', _("Display all columns")),
        ('hide-sides', _("Show only centre")),
    ]
    label=_("Mobile display behaviour")
    
class ThreeColumnLayoutChoiceBlock(DefaultChoiceBlock):
    choices = [
        ('-auto-', _("Centre Auto")),
        ('4-4-4', _("Equal Width Columns")),
        ('3-6-3', _("Left 3, Centre 6, Right 3")),
        ('2-8-2', _("Left 2, Centre 8, Right 2")),
        ('1-10-1', _("Left 1, Centre 10, Right 1")),
    ]

class BreakPointChoiceBlock(DefaultChoiceBlock):
    choices = [
        ('-', _("No breakpoint")),
        ('-lg', _("Large (<992px)")),
        ('-md', _("Medium (<768px)")),
        ('-sm', _("Mobile (<576px)"))
    ]
    label = _("Select Breakpoint")


#-----------------------------------------------------
# Column Layout Blocks
#-----------------------------------------------------
 
class FullWidthBaseBlock(StructBlock):
    column = BaseStreamBlock(
        label=_("Single Column Contents"),
        blank=True,
        Null=True
    )

    class Meta:
        template = 'blocks/full_width_block.html'
        icon = 'block-empty'
        label = "Page Wide Block"
        label_format = label

class TwoColumnBaseBlock(StructBlock):
    column_layout = TwoColumnLayoutChoiceBlock()
    breakpoint = BreakPointChoiceBlock(
        default = '-sm',
    )
    left_min = IntegerBlock(
        required=False,
        min_value=0,
        label=_("Left Col Min px"),
    )
    left_max = IntegerBlock(
        required=False,
        min_value=0,
        label=_("Left Col Max px"),
    )
    right_min = IntegerBlock(
        required=False,
        min_value=0,
        label=_("Right Col Min px"),
    )
    right_max = IntegerBlock(
        required=False,
        min_value=0,
        label=_("Right Col Max px"),
    )
    horizontal_padding = IntegerBlock(
        default = 4,
        max_value=5
    )
    vertical_border = BooleanBlock(
        default=False,
        required=False,
        label=_("Vertical Border"),
    )
    order = TwoColumnCollapseOrderChoiceBlock()    
    hide = TwoColumnHideChoiceBlock()    

    left_column = BaseStreamBlock(
        label=_("Left Column Contents"),
        blank=True,
        Null=True
    )
    right_column = BaseStreamBlock(
        label=_("Right Column Contents"),
        blank=True,
        Null=True
    )

    class Meta:
        template = 'blocks/two_column_block.html'
        icon = 'columns-two'
        label = "Two Column Block"
        label_format = label
        form_classname = "struct-block flex-block two-column-block"

    def clean(self, value):
        errors = {}
        left_min = value.get('left_min')
        left_max = value.get('left_max')
        right_min = value.get('right_min')
        right_max = value.get('right_max')

        if left_min and left_max and left_min > left_max:
            errors['left_min'] = ErrorList([_("Please make sure minimum is less than maximum.")])
            errors['left_max'] = ErrorList([_("Please make sure minimum is less than maximum.")])
        if right_min and right_max and right_min > right_max:
            errors['right_min'] = ErrorList([_("Please make sure minimum is less than maximum.")])
            errors['right_max'] = ErrorList([_("Please make sure minimum is less than maximum.")])
        if errors:
            raise StructBlockValidationError(block_errors=errors)

        return super().clean(value)     
       
class ThreeColumnBaseBlock(StructBlock):
    column_layout = ThreeColumnLayoutChoiceBlock(
        default = '4-4-4',
        label = _("Select column size ratio")
    )
    breakpoint = BreakPointChoiceBlock(
        default = '-md',
        label = _("Select responsive layout behaviour")
    )
    outer_min = IntegerBlock(
        required=False,
        min_value=0,
        label=_("Outer Col Min px"),
    )
    outer_max = IntegerBlock(
        required=False,
        min_value=0,
        label=_("Outer Col Max px"),
    )
    horizontal_padding = IntegerBlock(
        default = 4,
        max_value=5,
        label=_("Col gap")
    )
    vertical_border = BooleanBlock(
        default=False,
        required=False,
        label=_("Col Border"),
    )
    hide = ThreeColumnHideChoiceBlock()    

    left_column = BaseStreamBlock(
        label=_("Left Column Contents"),
        blank=True,
        Null=True
    )
    centre_column = BaseStreamBlock(
        label=_("Centre Column Contents"),
        blank=True,
        Null=True
    )
    right_column = BaseStreamBlock(
        label=_("Right Column Contents"),
        blank=True,
        Null=True
    )

    class Meta:
        template = 'blocks/three_column_block.html'
        icon = 'columns-three'
        label = _("Three Column Block")
        label_format = label
        form_classname = "struct-block flex-block three-column-block"

    def clean(self, value):
        errors = {}
        outer_min = value.get('outer_min')
        outer_max = value.get('outer_max')

        if outer_min and outer_max and outer_min > outer_max:
            errors['outer_min'] = ErrorList([_("Please make sure minimum is less than maximum.")])
            errors['outer_max'] = ErrorList([_("Please make sure minimum is less than maximum.")])
        if errors:
            raise StructBlockValidationError(block_errors=errors)

        return super().clean(value)     