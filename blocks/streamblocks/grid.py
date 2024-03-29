from wagtail.blocks import StreamBlock

from .columns import (FullWidthBaseBlock, ThreeColumnBaseBlock,
                      TwoColumnBaseBlock)


class GridStreamBlock(StreamBlock):
    page_wide_block=FullWidthBaseBlock()
    two_column_block = TwoColumnBaseBlock()
    three_column_block = ThreeColumnBaseBlock()
