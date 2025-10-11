from wagtail.blocks import StreamBlock

from ..models import *


class BaseStreamBlock(StreamBlock):
    rich_text_block = RichTextBlock()
    code_block = BlogCodeBlock()
    callout_block = CalloutBlock()
    heading_block = HeadingBlock()
    image_block = ImageBlock()
    table_of_contents = TableOfContentsBlock()
    link_button = Link()
    flex_card = FlexCard()
    call_to_action_card = CallToActionCard()
    simple_card = SimpleCard()
    simple_card_grid = SimpleCardGridBlock()
    simple_image_card_grid = SimpleImageCardGridBlock()
    collapsible_card_block = CollapsibleCardBlock()
    social_media_embed = SocialMediaEmbedBlock()
    external_link_embed = ExternalLinkEmbedBlock()
    inline_video_block = InlineVideoBlock()
    image_wall = ImageWallBlock()
    map_block = MapBlock()
    csv_table = CSVTableBlock()
    document_block = DocumentBlock()
    django_template_fragment = DjangoTemplateFragmentBlock()
    spacer_block = SpacerStaticBlock()
    empty_block = EmptyStaticBlock()