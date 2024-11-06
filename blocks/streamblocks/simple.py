from wagtail.blocks import StreamBlock

from ..models import (CallToActionCard, ImageBlock, SimpleCard, RichTextBlock,
                      SimpleRichTextBlock, SpacerStaticBlock)


class SimpleStreamBlock(StreamBlock):
    rich_text_block = RichTextBlock()
    richtext_block = SimpleRichTextBlock()
    image_block = ImageBlock()
    simple_card = SimpleCard()
    call_to_action_card = CallToActionCard()
    spacer_block = SpacerStaticBlock()
