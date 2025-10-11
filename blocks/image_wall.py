from django.utils.translation import gettext_lazy as _
from wagtail.blocks import ListBlock, StructBlock
from wagtail.images.blocks import ImageChooserBlock

class ImageWallItemBlock(StructBlock):
    image = ImageChooserBlock(label=_("Select Image"))

    class Meta:
        icon = 'image'
        label = _("Image")

class ImageWallBlock(StructBlock):
    images = ListBlock(ImageWallItemBlock)

    class Meta:
        template = 'blocks/image_wall_block.html'
        icon = "image-carousel"
        label = _("Image Wall")
        label_format = label
