from PIL import Image
from wagtail.images.image_operations import FilterOperation
from willow.plugins.pillow import PillowImage
from willow.registry import registry

def thumbnail(image, width, height):
    img = Image.frombytes('RGB', image.get_size(), image.to_buffer_rgb().data, 'raw')
    original_aspect = img.width/img.height
    thumbnail_aspect = width/height
    
    if original_aspect == thumbnail_aspect:
        # return resized image
        return PillowImage(img.resize((width, height)))
    else:
        # create transparent background size of requested thumbnail
        thumb = Image.new('RGB', (width, height), (255, 255, 255)) 
        thumb.putalpha(0)

        if thumbnail_aspect < original_aspect:
        # thumb aspect ratio is more narrow than original
            # scale as proportion of width
            resized_original = img.resize((width, round(img.height * width/img.width)))
            # paste into background with top/bottom spacing
            thumb.paste(resized_original, (0,(height-resized_original.height)//2))
        else:
        # thumb aspect ratio is wider than original
            # scale as proportion of height
            resized_original = img.resize((round(img.width * height/img.height), height))
            # paste into background with left/right spacing
            thumb.paste(resized_original, ((width-resized_original.width)//2, 0))

        return PillowImage(thumb)

registry.register_operation(PillowImage, 'thumbnail', thumbnail)

class ThumbnailOperation(FilterOperation):
    def construct(self, size):
        width_str, height_str = size.split("x")
        self.width = int(width_str)
        self.height = int(height_str)

    def run(self, willow, image, env):
        return willow.thumbnail(self.width, self.height)