from django.utils.translation import gettext_lazy as _
from wagtail.blocks import StaticBlock


class EmptyStaticBlock(StaticBlock):
    class Meta:
        admin_text = _("Empty block")
        template = 'blocks/empty_block.html'
        icon = 'block-empty'
        label = 'Empty Block'
        label_format = label

class SpacerStaticBlock(StaticBlock):
    class Meta:
        admin_text = _("Blank spacer block")
        template = 'blocks/spacer_block.html'
        icon = 'block-solid'
        label = 'Blank Space'
        label_format = label
