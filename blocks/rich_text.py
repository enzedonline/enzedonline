from django.utils.translation import gettext_lazy as _
from wagtail.blocks import RichTextBlock as WagtailRichTextBlock

class RichTextBlock(WagtailRichTextBlock):
    class Meta:
        template = "blocks/richtext_block.html"
        label = _("Rich Text Block")
        label_format = 'RTB: {content}'    
