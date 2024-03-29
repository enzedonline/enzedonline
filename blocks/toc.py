from django.utils.translation import gettext_lazy as _
from wagtail.blocks import CharBlock, IntegerBlock, StructBlock


class TableOfContentsBlock(StructBlock):
    toc_title = CharBlock(
        default=_("On this page"),
        max_length=60, 
        null=True, 
        blank=True,
        required=False,
        label=_("Title (optional)"),
        help_text=_("Optional title to display at the top of the table."),
    )
    
    levels = IntegerBlock(
        default = 3,
        min_value=1,
        max_value=5,
        label=_("Number of levels to include"),
        help_text=_("H1 tags are ignored. 1 level includes H2 only, 5 levels will include H2 to H6."),
    )

    class Meta:
        template = 'blocks/table_of_contents.html'
        icon = 'list-ol'
        label = 'Table of Contents'
        label_format = label
        
