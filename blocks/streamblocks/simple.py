from wagtail.blocks import StreamBlock

from ..models import (CallToActionCard, ImageBlock, SimpleCard,
                      SimpleRichTextBlock, SpacerStaticBlock)


class SimpleStreamBlock(StreamBlock):
    richtext_block = SimpleRichTextBlock()
    image_block = ImageBlock()
    simple_card = SimpleCard()
    call_to_action_card = CallToActionCard()
    spacer_block = SpacerStaticBlock()
