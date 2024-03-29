from django.utils.translation import gettext_lazy as _
from wagtail.blocks import BooleanBlock, RichTextBlock, StructBlock
from wagtail.blocks.field_block import IntegerBlock

from .choices import TextAlignmentChoiceBlock
from .heading import HeadingBlock
from .import_text import ImportTextBlock

class CSVTableBlock(StructBlock):
    title = HeadingBlock(required=False, label=" ")
    data = ImportTextBlock(label=_("Comma Separated Data"), file_type_filter=".csv")
    precision = IntegerBlock(
        default=2,
        label=_("Float Precision")
    )
    column_headers = BooleanBlock(
        label=_("Column Headers"),
        required=False, 
        default=True
    )
    row_headers = BooleanBlock(
        label=_("Row Headers"),
        required=False
    )
    compact = BooleanBlock(label=_("Compact"), required=False)
    caption = RichTextBlock(label=_("Caption"), editor='minimal', required=False)        
    caption_alignment = TextAlignmentChoiceBlock(
        label=_("Caption Alignment"),
        required=False, 
        default = 'end'
        )
    width = IntegerBlock(
        label=_("Table Width (%)"), 
        default=100, 
        )
    max_width = IntegerBlock(
        label=_("Maximum Width (px)"), 
        required=False, 
        )
    
    class Meta:
        template = 'blocks/csv_table_block.html'
        icon = 'table'
        label = 'CSV Table'
        label_format = label
        form_classname = 'struct-block flex-block csv-table-block'