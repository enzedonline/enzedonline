from django.utils.translation import gettext_lazy as _
from wagtail.blocks import CharBlock, StructBlock
from wagtail.embeds.blocks import EmbedBlock

from .choices import ColourThemeChoiceBlock


class InlineVideoBlock(StructBlock):
    video = EmbedBlock(
        label=_("Video URL"),
        help_text = _("eg 'https://www.youtube.com/watch?v=kqN1HUMr22I'")
    )
    caption = CharBlock(required=False, label=_("Caption"))
    background = ColourThemeChoiceBlock(
        default='text-black bg-transparent',
        label=_("Card Background Colour")
    )

    class Meta:
        icon = 'video'
        template = 'blocks/inline_video_block.html'
        label = _("External Video")    
        label_format = label