from django.utils.translation import gettext_lazy as _
from wagtail.blocks import (BooleanBlock, CharBlock, ListBlock,
                            PageChooserBlock, StructBlock, TextBlock)

from .choices import ImageFormatChoiceBlock
from .image import SEOImageChooserBlock


class CarouselImageBlock(StructBlock):
    image = SEOImageChooserBlock(label=_("Select Image & Enter Details"))
    title = CharBlock(label=_("Optional Image Title"), required=False)
    caption = TextBlock(label=_("Optional Image Caption"), required=False)
    link = PageChooserBlock(
        required=False,
        label=_("Optional Link to Internal Page")
    )

    class Meta:
        icon = 'image'
        label = _("Image for Carousel")


class ImageCarouselBlock(StructBlock):
    format = ImageFormatChoiceBlock(
        default='4-3',
        label=_("Select image aspect ratio"),
    )
    heading = CharBlock(
        label=_("Carousel Title"),
        required=False,
    )
    show_scroll_buttons = BooleanBlock(
        default=True,
        required=False,
        label=_("Show Scroll Buttons"),
        help_text=_("Disable for clickable vertical carousels.")
    )
    carousel_images = ListBlock(CarouselImageBlock, min_num=2, max_num=5)

    class Meta:
        template = 'blocks/image_carousel.html'
        icon = "image-carousel"
        label = _("Image Carousel")
        label_format = label
