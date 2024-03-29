from django.utils.translation import gettext_lazy as _
from wagtail.blocks import BooleanBlock, CharBlock, StructBlock
from wagtail.blocks.field_block import IntegerBlock
from wagtail.images.blocks import ImageChooserBlock

from .choices import ColourThemeChoiceBlock


class SEOImageChooserBlock(StructBlock):
    def __init__(self, required=True, **kwargs):
        local_blocks = (
            ("file", ImageChooserBlock(
                label=_("Image"),
                required=required
            )),
            ("seo_title", CharBlock(
                label=_("SEO Title"),
                required=required
            )),
        )   
        super().__init__(local_blocks, **kwargs)

    class Meta:
        form_classname = "struct-block flex-block seo-image-chooser-block"
   
class ImageBlock(StructBlock):
    """
    Custom `StructBlock` for utilizing images with associated caption and
    attribution data
    """
    image = SEOImageChooserBlock(required=True, label=_("Select Image & Enter Details"))
    caption = CharBlock(required=False, label=_("Image Caption (optional)"))
    attribution = CharBlock(required=False, label=_("Image Attribution (optional)"))
    background = ColourThemeChoiceBlock(
        default='bg-transparent',
        label=_("Card Background Colour")
    )
    max_width = IntegerBlock(required=False, label=_("Maximum image width (px)"))
    animated_gif = BooleanBlock(required=False, label=_("Is Animated GIF"))
    class Meta:
        icon = 'image'
        template = "blocks/image_block.html"
        label = _("Image Block")
        label_format = _("Image") + ": {image}"
        form_classname = "struct-block flex-block image-block"

