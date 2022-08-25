from email.policy import default
import unidecode
from django.forms.utils import ErrorList
from django.utils.text import slugify
from django.utils.translation import gettext_lazy as _
from wagtail.blocks import (BooleanBlock, CharBlock, ChoiceBlock,
                            PageChooserBlock, RawHTMLBlock, RichTextBlock,
                            StaticBlock, StreamBlock, StructBlock, StructValue,
                            TextBlock)
from wagtail.blocks.field_block import IntegerBlock, URLBlock
from wagtail.blocks.struct_block import StructBlockValidationError
from wagtail.documents.blocks import DocumentChooserBlock
from wagtail.embeds.blocks import EmbedBlock
from wagtail.images.blocks import ImageChooserBlock
from wagtail_localize.synctree import Locale

import core.metadata
from core.utils import isfloat


class AlignmentChoiceBlock(ChoiceBlock):
    choices=[
        ('start', _('Left')), 
        ('center', _('Centre')), 
        ('end', _('Right'))
    ]

class TextAlignmentChoiceBlock(ChoiceBlock):
    choices=[
        ('justify', _('Justified')), 
        ('start', _('Left')), 
        ('center', _('Centre')), 
        ('end', _('Right'))
    ]

class ColourThemeChoiceBlock(ChoiceBlock):
    choices=[
        ('bg-transparent', _("Transparent")),
        ('bg-primary', _("Primary")),
        ('bg-secondary', _("Secondary")),
        ('bg-success', _("Success")),
        ('bg-info', _("Info")),
        ('bg-warning', _("Warning")),
        ('bg-danger', _("Danger")),
        ('bg-light', _("Light")),
        ('bg-dark', _("Dark")),
        ('bg-black', _("Black")),
    ]

class ButtonChoiceBlock(ChoiceBlock):
    choices=[
        ('btn-primary', _("Standard Button")),
        ('btn-secondary', _("Secondary Button")),
        ('btn-link', _("Text Only")),
        ('btn-success', _("Success Button")),
        ('btn-danger', _("Danger Button")),
        ('btn-warning', _("Warning Button")),
        ('btn-info', _("Info Button")),
        ('btn-light', _("Light Button")),
        ('btn-dark', _("Dark Button")),
    ]

class HeadingSizeChoiceBlock(ChoiceBlock):
    choices=[
        ('h2', 'H2'), 
        ('h3', 'H3'), 
        ('h4', 'H4'), 
        ('h5', 'H5'), 
        ('h6', 'H6'), 
    ]

class ImageFormatChoiceBlock(ChoiceBlock):
    choices=[
        ('4-1', _("4:1 Horizontal Letterbox Banner")),
        ('3-1', _("3:1 Horizontal Panorama Banner")),
        ('4-3', _("4:3 Horizontal Standard Format")),
        ('1-1', _("1:1 Square Format")),
        ('3-4', _("3:4 Portrait Standard Format")),
        ('1-3', _("1:3 Vertical Panorama Banner")),
    ]

class RouteOptionChoiceBlock(ChoiceBlock):
     choices=[
        ('no-route', "None"),
        ('walking', "Walking"),
        ('cycling', "Cycling"),
        ('driving', "Driving"),
        ('driving-traffic', "Driving (with traffic conditions)")
     ]

class FlexCardLayoutChoiceBlock(ChoiceBlock):
    choices=[
        ('image-left-responsive', _("Responsive Horizontal (Image left of text on widescreen only)")),
        ('image-right-responsive', _("Responsive Horizontal (Image right of text on widescreen only)")),
        ('image-left-fixed', _("Fixed Horizontal (Image left of text on all screen sizes)")),
        ('image-right-fixed', _("Fixed Horizontal (Image right of text on all screen sizes)")),
        ('vertical', _("Vertical (Image above text on on all screen sizes)")),
    ]

class BreakpointChoiceBlock(ChoiceBlock):
    choices=[
        ('sm', _("Small screen only")),
        ('md', _("Small and medium screens")),
    ]

class CodeChoiceBlock(ChoiceBlock):
    choices=[
        ('python', 'Python'),
        ('css', 'CSS'),
        ('html', 'HTML'),
        ('sql', 'SQL'),
        ('javascript', 'Javascript'),
        ('json', 'JSON'),
        ('xml', 'XML'),
        ('git', 'Git'),
        ('graphql', 'GraphQL'),
        ('powershell', 'PowerShell'),
        ('r', 'R'),
        ('vb', 'VB6'),
        ('vba', 'VBA'),
        ('vbnet', 'VB.NET'),
        ('bash', 'Bash/Shell'),
    ]
 
class SEOImageChooserBlock(StructBlock):
    file = ImageChooserBlock(
        required=True, 
        label=_("Image")
    )
    seo_title = CharBlock(
        required=True,
        label=_("SEO Title"),
        help_text=_("A text description of the image for screen readers and search engines")
    )
   
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
    max_width = IntegerBlock(required=False, label=_("Optional maximum width the image can grow to (in pixels)"))
    class Meta:
        icon = 'image'
        template = "blocks/image_block.html"
        label = _("Image Block")

class BlockQuote(StructBlock):
    """
    Custom `StructBlock` that allows the user to attribute a quote to the author
    """
    text = TextBlock(label=_("Quote"))
    attribute_name = CharBlock(
        blank=True, required=False, label=_("Optional Attribution"))
    background = ColourThemeChoiceBlock(
        default='bg-transparent',
        label=_("Card Background Colour")
    )

    class Meta:
        icon = "fa-quote-left"
        template = "blocks/blockquote.html"
        label = _("Quote Block")

class Link_Value(StructValue):
    """ Additional logic for the Link class """

    def url(self) -> str:
        internal_page = self.get("internal_page")
        url_link = self.get("url_link")
        if internal_page:
            return internal_page.localized.url
        elif url_link:
            if url_link.startswith('/'): # presumes internal link starts with '/' and no lang code
                url = '/' + Locale.get_active().language_code + url_link
            else:
                url = url_link 
            return url
        else:
            return None

class Link(StructBlock):
    button_text = CharBlock(
        max_length=50,
        null=False,
        blank=False,
        label=_("Button Text")
    )
    internal_page = PageChooserBlock(
        required=False,
        label=_("Link to internal page")
    )
    url_link = CharBlock(
        required=False,
        label=_("Link to external site or internal URL")
    )
    appearance = ButtonChoiceBlock(
        max_length=15,
        default='btn-primary',
        label=_("Button Appearance")
    )
    placement = AlignmentChoiceBlock(
        default='end',
        label=_("Button Placement")
    )
    size = ChoiceBlock(
        max_length=10,
        default=' ',
        choices=[
            ('btn-sm', _("Small")),
            (' ', _("Standard")),
            ('btn-lg', _("Large")),
        ],
        label=_("Button Size")
    )
    class Meta:
        value_class = Link_Value
        icon = "fa-link"
        template = "blocks/link_button.html"

    def clean(self, value):
        errors = {}
        internal_page = value.get('internal_page')
        url_link = value.get('url_link')

        if not(bool(internal_page) ^ bool(url_link)):
            errors['internal_page'] = ErrorList([_("Please select an internal page or an external link (but not both)")])
            errors['url_link'] = ErrorList([_("Please select an internal page or an external link (but not both)")])

        if errors:
            raise StructBlockValidationError(block_errors=errors)

        return super().clean(value)

class RichTextStructBlock(StructBlock):
    alignment = TextAlignmentChoiceBlock(
        default = 'justify',
        label=_("Text Alignment")
    )
    content = RichTextBlock()

    class Meta:
        template = 'blocks/simple_richtext_block.html'
        label = _("Rich Text Block")
        icon = 'pilcrow'
        abstract = True

class SimpleRichTextBlock(RichTextStructBlock):
    pass

class MinimalRichTextBlock(RichTextStructBlock):
    content = RichTextBlock(editor='minimal')

class BasicRichTextBlock(RichTextStructBlock):
    content = RichTextBlock(editor='basic')

class HeadingBlock(StructBlock):
    title = CharBlock(required=True)
    heading_size = HeadingSizeChoiceBlock(default='h2')
    alignment = TextAlignmentChoiceBlock(default='start')
    bookmark = CharBlock(
        required=False,
        label=_("Optional Bookmark"),
        help_text=_("Bookmark must be a compatible slug format without spaces or special characters")
    )
    
    class Meta:
        template = 'blocks/heading_block.html'
        label = _("Heading Block")
        icon = 'title'

    def clean(self, value):
        errors = {}
        bookmark = value.get('bookmark')
        slug = slugify(unidecode.unidecode(bookmark))
        
        if bookmark != slug:
            errors['bookmark'] = ErrorList([_(f"\
                '{bookmark}' is not a valid slug for the bookmark. \
                '{slug}' is the suggested value for this.")])
            raise StructBlockValidationError(block_errors=errors)

        return super().clean(value)

class FlexCard(StructBlock):
    
    format = FlexCardLayoutChoiceBlock(
        max_length=15,
        default='vertical',
        label=_("Card Format")
    )    
    breakpoint = BreakpointChoiceBlock(
        default = 'md',
        label=_("Breakpoint for responsive layouts")
    )
    background = ColourThemeChoiceBlock(
        default='bg-transparent',
        label=_("Card Background Colour")
    )
    border = BooleanBlock(
        default=True,
        required=False,
        label=_("Border"),
        help_text=_("Draw a border around the card?")
    )
    text = SimpleRichTextBlock(
        label=_("Card Body Text"),
        help_text=_("Body text for this card."),
    )
    image = SEOImageChooserBlock(
        label=_("Select Image & Enter Details"),
        help_text=_("Card Image (approx 1:1.4 ratio - ideally upload 2100x1470px)."),
    )
    image_min = IntegerBlock(
        label=_("Minimum width the image can shrink to (pixels)"),
        default=200,
        min_value=100
    )
    image_max = IntegerBlock(
        label=_("Optional maximum width the image can grow to (pixels)"),
        required=False
    )
    class Meta:
        template = 'blocks/flex_card_block.html'
        label = _("Image & Text Card")
        icon = 'fa-address-card'

    def clean(self, value):
        errors = {}
        image_min = value.get('image_min')
        image_max = value.get('image_max')

        if image_min and image_max and image_min > image_max:
            errors['image_min'] = ErrorList([_("Please make sure minimum is less than maximum.")])
            errors['image_max'] = ErrorList([_("Please make sure minimum is less than maximum.")])
        if errors:
            raise StructBlockValidationError(block_errors=errors)

        return super().clean(value)     

class CallToActionCard(FlexCard):
    link = Link(
        label=_("Link Button"),
        help_text = _("Enter a link or select a page and choose button options."),
        required=False,
    )
    class Meta:
        template = 'blocks/flex_card_block.html'
        label = _("Call-To-Action Card (Image/Text/Button)")
        icon = 'fa-address-card'

class SimpleCard(StructBlock):
    background = ColourThemeChoiceBlock(
        default='bg-transparent',
        label=_("Card Background Colour")
    )    
    border = BooleanBlock(
        default=True,
        required=False,
        label=_("Border"),
        help_text=_("Draw a border around the card?")
    )
    full_height = BooleanBlock(
        default=True,
        required=False,
        label=_("Full Height"),
        help_text=_("Card uses all available height")
    )
    text = SimpleRichTextBlock(
        label=_("Card Body Text"),
        help_text=_("Body text for this card."),
    )

    class Meta:
        template = 'blocks/simple_card_block.html'
        label = _("Simple Card (Text Only)")
        icon = 'fa-align-justify'

class SimpleCardStreamBlock(StreamBlock):
    simple_card = SimpleCard()

class SimpleCardGridBlock(StructBlock):
    columns = ChoiceBlock(
        max_length=40,
        default='row-cols-1 row-cols-sm-2 row-cols-lg-3 row-cols-xl-4',
        choices=[
            ('row-cols-1 row-cols-sm-2 row-cols-lg-3 row-cols-xl-4', _("Mobile:1 Max:4")),
            ('row-cols-1 row-cols-md-2', _("Mobile:1 Max:2")),
            ('row-cols-2 row-cols-lg-3 row-cols-xl-4', _("Mobile:2 Max:4")),
        ],
        label=_("Maximum Cards per Row")
    )
    cards = SimpleCardStreamBlock()

    class Meta:
        template = "blocks/simple_card_grid_block.html"
        icon = 'fa-th'
        label = _("Flexible Grid of Simple Cards")

class SimpleImageCard(StructBlock):
    
    background = ColourThemeChoiceBlock(
        default='bg-transparent',
        label=_("Card Background Colour")
    )
    border = BooleanBlock(
        default=True,
        required=False,
        label=_("Border"),
        help_text=_("Draw a border around the card?")
    )
    text = SimpleRichTextBlock(
        label=_("Card Body Text"),
        help_text=_("Body text for this card."),
    )
    image = SEOImageChooserBlock(
        label=_("Select Image & Enter Details"),
        help_text=_("Card Image (display size limited to 300-400px range)."),
    )

    class Meta:
        template = 'blocks/simple_image_card_block.html'
        label = _("Simple Image & Text Card")
        icon = 'far fa-image'

class SimpleImageCardStreamBlock(StreamBlock):
    simple_image_card = SimpleImageCard()

class SimpleImageCardGridBlock(StructBlock):
    alignment = ChoiceBlock(
        choices = [
            ('align-items-top', _('Top')), 
            ('align-items-center', _('Middle')), 
        ],
        label=_("Vertical Alignment"),
        help_text=_("Choose if row items should be vertically aligned to their tops or middles."),
        default='align-items-top'
    )

    cards = SimpleImageCardStreamBlock()

    class Meta:
        template = "blocks/simple_image_card_grid_block.html"
        icon = 'fab fa-stack-overflow'
        label = _("Flexible Grid of Simple Image Cards")

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
        icon = 'media'
        template = 'blocks/inline_video_block.html'
        label = _("Embed external video")    

class SocialMediaEmbedBlock(StructBlock):
    embed_code = RawHTMLBlock(
        label=_("Paste Embed code block from Provider"),
        help_text=_("Paste in only embed code. For Facebook, only Step 2 on the JavaScript SDK tab")
    )
    class Meta:
        template='blocks/social_media_embed.html'
        icon = 'fa-share-alt-square'
        label = _("Embed Social Media Post")

class HtmlBlock(StructBlock):
    code = RawHTMLBlock(
        label=_("Enter HTML Code")
    )
    class Meta:
        template='blocks/html_code_block.html'
        icon = 'fa-file-code'
        label = _("Embed HTML Code")

class ExternalLinkEmbedBlock(StructBlock):
    external_link = URLBlock(
        label=_("URL to External Article"),
        help_text=_("For articles in external websites without embed share option"),
    )
    image = CharBlock(
        max_length=200, 
        null=True, 
        blank=True,
        help_text=_("Leave blank to autofill from website. Delete text to refresh from website.")
    )
    title = CharBlock(
        max_length=200, 
        null=True, 
        blank=True,
        help_text=_("Leave blank to autofill from website. Delete text to refresh from website.")
    )
    description = TextBlock(
        null=True, 
        blank=True,
        help_text=_("Leave blank to autofill from website. Delete text to refresh from website.")
    )
    image_min = IntegerBlock(
        label=_("Minimum width the image can shrink to (pixels)"),
        default=200,
        min_value=100
    )
    image_max = IntegerBlock(
        label=_("Optional maximum width the image can grow to (pixels)"),
        required=False
    )
    format = FlexCardLayoutChoiceBlock(
        default='vertical',
        label=_("Card Format")
    )    
    breakpoint = BreakpointChoiceBlock(
        default = 'md',
        label=_("Breakpoint for responsive layouts")
    )
    background = ColourThemeChoiceBlock(
        default='bg-transparent',
        label=_("Card Background Colour")
    )
    border = BooleanBlock(
        default=True,
        required=False,
        label=_("Border"),
        help_text=_("Draw a border around the card?")
    )
    full_height = BooleanBlock(
        default=True,
        required=False,
        label=_("Full Height"),
        help_text=_("Card uses all available height")
    )
    button_text = CharBlock(
        label=_("Text for link to article"),
        default=_("Read Full Article")
    )
    button_appearance = ButtonChoiceBlock(
        max_length=15,
        default='btn-primary',
        label=_("Button Appearance")
    )
    button_placement = AlignmentChoiceBlock(
        default='end',
        label=_("Button Placement")
    )
    button_size = ChoiceBlock(
        max_length=10,
        default=' ',
        choices=[
            ('btn-sm', _("Small")),
            (' ', _("Standard")),
            ('btn-lg', _("Large")),
        ],
        label=_("Button Size")
    )

    class Meta:
        template='blocks/external_link_embed.html',
        icon = 'fa-share-alt'
        label = _("Embed External Article")
    
    def clean(self, value):
        errors = {}

        if not(value['image'] and value['title'] and value['description']):
            try:
                metadata = core.metadata.get_metadata(value.get('external_link'))
            except:
                metadata =  None
                errors['external_link'] = ErrorList([_("No information for the URL was found, please check the URL and ensure the full URL is included and try again.")])
            
            try:
                if metadata:
                    if metadata['image'] and not value['image']:
                        value['image'] = metadata['image']
                    if metadata['title'] and not value['title']:
                        value['title'] = metadata['title']
                    if metadata['description'] and not value['description']:
                        value['description'] = metadata['description']
            except KeyError:
                errors['external_link'] = ErrorList([_("No information for the URL was found, please check the URL and ensure the full URL is included and try again.")])

            image_min = value.get('image_min')
            image_max = value.get('image_max')

            if image_min and image_max and image_min > image_max:
                errors['image_min'] = ErrorList([_("Please make sure minimum is less than maximum.")])
                errors['image_max'] = ErrorList([_("Please make sure minimum is less than maximum.")])

            if errors:
                raise StructBlockValidationError(block_errors=errors)

        return super().clean(value)

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

class CarouselImageStreamBlock(StreamBlock):
    carousel_image = CarouselImageBlock()

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
    carousel_images = CarouselImageStreamBlock(min_num=2, max_num=5)

    class Meta:
        template='blocks/image_carousel.html'
        icon="fa-clone"
        label = _("Image Carousel")

class CollapsableCard(StructBlock):
    header = CharBlock(
        label=_("Card Banner Title")
    )
    text = SimpleRichTextBlock(
        label=_("Card Body Text"),
        help_text=_("Body text for this card."),
    )

class CollapsableCardStreamBlock(StreamBlock):
    collapsable_card = CollapsableCard()

class CollapsableCardBlock(StructBlock):
    header_colour  = ColourThemeChoiceBlock(
        default='bg-dark',
        label=_("Card Header Background Colour")
    )    
    body_colour  = ColourThemeChoiceBlock(
        default='bg-light',
        label=_("Card Body Background Colour")
    )
    cards = CollapsableCardStreamBlock(min_num=2)

    class Meta:
        template='blocks/collapsable_card_block.html'
        icon="fa-stack-overflow"
        label = _("Collapsable Text Block")

class MapWaypointBlock(StructBlock):
    gps_coord = TextBlock(
        label=_('GPS Coordinates (Latitude, Longtitude)'),
        help_text=_('Ensure latitude followed by longitude separated by a comma (e.g. 42.597486, 1.429252).')
        )
    pin_label = TextBlock(
        label=_('Map Pin Label (optional)'),
        help_text=_('Text for map pin pop-up (if used).'),
        required=False
    )
    show_pin = BooleanBlock(
        label=_('Show Pin on Map'),
        default=True,
        required=False
    )
    class Meta:
        icon = 'plus-inverse'
        label = _("Map Waypoint")
        
    def clean(self, value):
        errors = {}
        gps = value.get('gps_coord')

        if gps.count(',') != 1:
            errors['gps_coord'] = ErrorList([_("Please enter latitude followed by longitude, separated by a comma.")])
            raise StructBlockValidationError(block_errors=errors)

        lat, lng = gps.split(',')
        
        if not(isfloat(lat) and isfloat(lng)):
            errors['gps_coord'] = ErrorList([_("Please enter latitude and longitude in numeric format (e.g. 42.603552, 1.442655 not 42°36'12.8\"N 1°26'33.6\"E).")])
            raise StructBlockValidationError(block_errors=errors)

        if (float(lat) < -90 or float(lat) > 90 or float(lng) < -180 or float(lng) > 360):
            errors['gps_coord'] = ErrorList([_("Please enter latitude between -90 and 90 and longitude between -180 and 360.")])
            raise StructBlockValidationError(block_errors=errors)

        return super().clean(value)        
        
class MapWayPointStreamBlock(StreamBlock):
    waypoint = MapWaypointBlock()
            
class MapBlock(StructBlock):
    waypoints = MapWayPointStreamBlock(min_num=2, max_num=25, 
                                       label=_("Add Waypoints (minimum 2, maximum 25)"))
    route_type = RouteOptionChoiceBlock(default='walking')
    show_route_info = BooleanBlock(
        label=_("Show Route Distance and Duration on Map"),
        default=True,
        required=False
    )
    height = IntegerBlock(default=70, min_value=20,
                    help_text=_("Height of map (% of viewport)."))
    padding_top = IntegerBlock(default=50, min_value=0)
    padding_right = IntegerBlock(default=50, min_value=0)
    padding_bottom = IntegerBlock(default=50, min_value=0)
    padding_left = IntegerBlock(default=50, min_value=0,
                    help_text=_("Pixels from edge of map to closest waypoint."))

    class Meta:
        template='blocks/map_block.html'
        icon="site"
        label = _("Interactive Map")
        
class BlogCodeBlock(StructBlock):
    language = CodeChoiceBlock(default='python')
    code = TextBlock()

    translatable_fields = []

    class Meta:
        template = "blocks/code_block.html"
        icon = "fa-code"
        label = _("Code Block")

class DocumentBlock(StructBlock):
    document = DocumentChooserBlock(
        label=_("Document")
    )
    link_label = CharBlock(
        label = _("Link Label"),
        help_text = _("The text to appear on the link")
    )
    text_size = HeadingSizeChoiceBlock(
        label = _("Text Size"),
        default = 'p'
    )
    icon = CharBlock(
        label = _("Link Icon"),
        help_text = _("Optional FontAwesome icon to appear left of the link (eg fas fa-file)"),
        required = False,
    )
    appearance = ButtonChoiceBlock(
        max_length=15,
        default='btn-link',
        label=_("Link Appearance")
    )
    outline = BooleanBlock(
        label = _("Outline button"),
        help_text = _("Blank for solid fill, checked for outline only"),
        default = False,
        required = False
    )
    full_width = BooleanBlock(
        label = _("Full width button"),
        help_text = _("Link button fills available width"),
        default = False,
        required = False
    )
    alignment = AlignmentChoiceBlock(
        default = 'center',
        label = _("Text Alignment"),
        help_text = _("Only used if full width button")
    )

    class Meta:
        template = "blocks/document_block.html"
        icon = "fa-file"
        label = _("Document Block")

class DocumentListBlock(StructBlock):
    tag_list = CharBlock(
        label = _("Tag List"),
        help_text = _("Comma seperated list of tags to filter by. Leave blank to list all documents."),
        required = False,
    )
    text_size = HeadingSizeChoiceBlock(
        label = _("Text Size"),
        default = 'p'
    )
    icon = CharBlock(
        label = _("Link Icon"),
        help_text = _("Optional FontAwesome icon to appear left of the link (eg fas fa-file)"),
        required = False,
    )
    appearance = ButtonChoiceBlock(
        max_length=15,
        default='btn-link',
        label=_("Link Appearance")
    )
    outline = BooleanBlock(
        label = _("Outline button"),
        help_text = _("Blank for solid fill, checked for outline only"),
        default = False,
        required = False
    )
    full_width = BooleanBlock(
        label = _("Full width button"),
        help_text = _("Link button fills available width"),
        default = False,
        required = False
    )
    alignment = AlignmentChoiceBlock(
        default = 'center',
        label = _("Text Alignment"),
        help_text = _("Only used if full width button")
    )
    sort_by = ChoiceBlock(
        choices = [
            ('created_at', _('Date (newest first)')), 
            ('title', _('Document Title')), 
        ],
        default = 'created_at',
        label = _("Sort Order"),
    )

    class Meta:
        template = "blocks/document_list_block.html"
        icon = "fa-list"
        label = "Document List"

class EmptyStaticBlock(StaticBlock):
    class Meta:
        template = 'blocks/empty_block.html'
        icon = 'placeholder'
        label = 'Empty Block'

class SpacerStaticBlock(StaticBlock):
    class Meta:
        template = 'blocks/spacer_block.html'
        icon = 'fa-square'
        label = 'Add Blank Space'

class LatestBlogPostGrid(StructBlock):
    group_label = SimpleRichTextBlock(
        blank=True,
        null=True,
        label=_("Optional heading for block"),
        help_text=_("Leave blank for no heading"),
        required=False
    )
    background = ColourThemeChoiceBlock(
        default='text-black bg-transparent',
        label=_("Card Background Colour")
    )
    post_count = IntegerBlock(
        default=2,
        min_value=1,
        max_value=20,
        label=_("Number of blog posts to show")
    )
    class Meta:
        template = 'blocks/latest_blog_posts_block.html'
        label = _("Latest Blog Post(s)")
        icon = 'fa-edit'

class TableOfContentsBlock(StructBlock):
    toc_title = CharBlock(
        max_length=60, 
        null=True, 
        blank=True,
        required=False,
        label=_("Title (optional)"),
        help_text=_("Optional title to display at the top of the table."),
    )
    
    levels = IntegerBlock(
        default = 3,
        min_value=1,
        max_value=5,
        label=_("Number of levels to include"),
        help_text=_("H1 tags are ignored. 1 level includes H2 only, 5 levels will include H2 to H6."),
    )

    class Meta:
        template = 'blocks/table_of_contents.html'
        icon = 'fas fa-stream'
        label = 'Table of Contents'
        
class CSVTableBlock(StructBlock):
    title = HeadingBlock(required=False, label=_("Table Title"))
    data = TextBlock(label=_("Comma Separated Data"))
    row_headers = BooleanBlock(required=False, help_text=_("First column contains row headers"))
    compact = BooleanBlock(required=False, help_text=_("Cell padding reduced by half"))
    caption = RichTextBlock(editor='minimal', required=False)        
    caption_alignment = TextAlignmentChoiceBlock(
        required=False, 
        default = 'end'
        )
    width = IntegerBlock(
        default=100, 
        label=_("Table Width (%)"), 
        help_text=_("Table width (as percentage of container)")
        )
    max_width = IntegerBlock(
        required=False, 
        label=_("Maximum Table Width (pixels)"), 
        help_text=_("Optional: Maximum width (in pixels) the table can grow to")
        )
    class Meta:
        template = 'blocks/csv_table_block.html'
        icon = 'list-ul'
        label = 'CSV Table'

class BaseStreamBlock(StreamBlock):
    richtext_block = SimpleRichTextBlock()
    code_block = BlogCodeBlock()
    image_block = ImageBlock()
    heading_block = HeadingBlock()
    table_of_contents = TableOfContentsBlock()
    link_button = Link()
    flex_card = FlexCard()
    call_to_action_card = CallToActionCard()
    simple_card = SimpleCard()
    simple_card_grid = SimpleCardGridBlock()
    simple_image_card = SimpleImageCard()
    simple_image_card_grid = SimpleImageCardGridBlock()
    collapsible_card_block = CollapsableCardBlock()
    social_media_embed = SocialMediaEmbedBlock()
    external_link_embed = ExternalLinkEmbedBlock()
    inline_video_block = InlineVideoBlock()
    image_carousel = ImageCarouselBlock()
    map_block = MapBlock()
    csv_table = CSVTableBlock()
    document_block = DocumentBlock()
    document_list_block = DocumentListBlock()
    latest_blog_posts = LatestBlogPostGrid()
    block_quote = BlockQuote()
    spacer_block = SpacerStaticBlock()
    empty_block = EmptyStaticBlock()
    
class TwoColumnLayoutChoiceBlock(ChoiceBlock):
    choices = [
        ('auto-', _("Left column width determined by content (care needed, test on all screen sizes)")),
        ('-auto', _("Right column width determined by content (care needed, test on all screen sizes)")),
        ('1-11', _("Left 1, Right 11")),
        ('2-10', _("Left 2, Right 10")),
        ('3-9', _("Left 3, Right 9")),
        ('4-8', _("Left 4, Right 8")),
        ('5-7', _("Left 5, Right 7")),
        ('6-6', _("Left 6, Right 6")),
        ('7-5', _("Left 7, Right 5")),
        ('8-4', _("Left 8, Right 4")),
        ('9-3', _("Left 9, Right 3")),
        ('10-2', _("Left 10, Right 2")),
        ('11-1', _("Left 11, Right 1")),
    ]

class ThreeColumnLayoutChoiceBlock(ChoiceBlock):
    choices = [
        ('-auto-', _("Centre column width determined by content (care needed, test on all screen sizes)")),
        ('4-4-4', _("Equal Width Columns")),
        ('3-6-3', _("Left 3, Centre 6, Right 3")),
        ('2-8-2', _("Left 2, Centre 8, Right 2")),
        ('1-10-1', _("Left 1, Centre 10, Right 1")),
    ]

class BreakPointChoiceBlock(ChoiceBlock):
    choices = [
        ('-', _("Columns side by side on all screen sizes (best for uneven column sizes)")),
        ('-lg', _("Columns side by side on large screen only")),
        ('-md', _("Columns side by side on medium and large screen only")),
        ('-sm', _("Single column on mobile, side by side on all other screens"))
    ]

class FullWidthBaseBlock(StructBlock):
    column = BaseStreamBlock(
        label=_("Single Column Contents"),
        blank=True,
        Null=True
    )

    class Meta:
        template = 'blocks/full_width_block.html'
        icon = 'arrows-alt-h'
        label = "Page Wide Block"

class TwoColumnBaseBlock(StructBlock):
    column_layout = TwoColumnLayoutChoiceBlock(
        default = '6-6',
        label = _("Select column size ratio")
    )
    breakpoint = BreakPointChoiceBlock(
        default = '-sm',
        label = _("Select responsive layout behaviour")
    )
    left_min = IntegerBlock(
        required=False,
        min_value=0,
        label=_("Left Column Minimum Width (pixels) - optional"),
        help_text=_("The minimum width the left column can shrink to above the breakpoint. Leave blank to kep width proportional.")
    )
    left_max = IntegerBlock(
        required=False,
        min_value=0,
        label=_("Left Column Maximum Width (pixels)"),
        help_text=_("The maximum width the left column can grow to above the breakpoint. Leave blank to kep width proportional.")
    )
    right_min = IntegerBlock(
        required=False,
        min_value=0,
        label=_("Right Column Minimum Width (pixels)"),
        help_text=_("The minimum width the right column can shrink to above the breakpoint. Leave blank to kep width proportional.")
    )
    right_max = IntegerBlock(
        required=False,
        min_value=0,
        label=_("Right Column Maximum Width (pixels)"),
        help_text=_("The maximum width the right column can grow to above the breakpoint. Leave blank to kep width proportional.")
    )
    horizontal_padding = IntegerBlock(
        default = 4,
        max_value=5
    )
    vertical_border = BooleanBlock(
        default=False,
        required=False,
        label=_("Vertical Border"),
        help_text=_("Add a vertical line between columns")
    )
    order = ChoiceBlock(
        max_length=15,
        default='left-first',
        choices=[
            ('left-first', _("Left column is first on mobile")),
            ('right-first', _("Right column is first on mobile")),
        ],
        label=_("Column order on mobile"),
        help_text=_("Select which column will appear above the other on mobile screen")
    )    
    hide = ChoiceBlock(
        max_length=15,
        default='hide-none',
        choices=[
            ('hide-none', _("Display both column contents on mobile (one above the other)")),
            ('hide-left', _("Hide the left column contents on mobile")),
            ('hide-right', _("Hide the right column contents on mobile")),
        ],
        label=_("Hide contents on mobile")
    )    

    left_column = BaseStreamBlock(
        label=_("Left Column Contents"),
        blank=True,
        Null=True
    )
    right_column = BaseStreamBlock(
        label=_("Right Column Contents"),
        blank=True,
        Null=True
    )

    class Meta:
        template = 'blocks/two_column_block.html'
        icon = 'fa-columns'
        label = "Two Column Block"

    def clean(self, value):
        errors = {}
        left_min = value.get('left_min')
        left_max = value.get('left_max')
        right_min = value.get('right_min')
        right_max = value.get('right_max')

        if left_min and left_max and left_min > left_max:
            errors['left_min'] = ErrorList([_("Please make sure minimum is less than maximum.")])
            errors['left_max'] = ErrorList([_("Please make sure minimum is less than maximum.")])
        if right_min and right_max and right_min > right_max:
            errors['right_min'] = ErrorList([_("Please make sure minimum is less than maximum.")])
            errors['right_max'] = ErrorList([_("Please make sure minimum is less than maximum.")])
        if errors:
            raise StructBlockValidationError(block_errors=errors)

        return super().clean(value)     
       
class ThreeColumnBaseBlock(StructBlock):
    column_layout = ThreeColumnLayoutChoiceBlock(
        default = '4-4-4',
        label = _("Select column size ratio")
    )
    breakpoint = BreakPointChoiceBlock(
        default = '-md',
        label = _("Select responsive layout behaviour")
    )
    outer_min = IntegerBlock(
        required=False,
        min_value=0,
        label=_("Outer Column Minimum Width (pixels)"),
        help_text=_("The minimum width the left and right columns can shrink to above the breakpoint. Leave blank to kep width proportional.")
    )
    outer_max = IntegerBlock(
        required=False,
        min_value=0,
        label=_("Outer Column Maximum Width (pixels)"),
        help_text=_("The maximum width the left and right columns can grow to above the breakpoint. Leave blank to kep width proportional.")
    )
    horizontal_padding = IntegerBlock(
        default = 4,
        max_value=5
    )
    vertical_border = BooleanBlock(
        default=False,
        required=False,
        label=_("Vertical Border"),
        help_text=_("Add a vertical line between columns")
    )
    hide = ChoiceBlock(
        max_length=15,
        default='hide-none',
        choices=[
            ('hide-none', _("Display all columns on mobile (one above the other)")),
            ('hide-sides', _("Hide the left and right columns contents on mobile")),
        ],
        label=_("Hide contents on mobile")
    )    

    left_column = BaseStreamBlock(
        label=_("Left Column Contents"),
        blank=True,
        Null=True
    )
    centre_column = BaseStreamBlock(
        label=_("Centre Column Contents"),
        blank=True,
        Null=True
    )
    right_column = BaseStreamBlock(
        label=_("Right Column Contents"),
        blank=True,
        Null=True
    )

    class Meta:
        template = 'blocks/three_column_block.html'
        icon = 'fa-columns'
        label = "Three Column Block"

    def clean(self, value):
        errors = {}
        outer_min = value.get('outer_min')
        outer_max = value.get('outer_max')

        if outer_min and outer_max and outer_min > outer_max:
            errors['outer_min'] = ErrorList([_("Please make sure minimum is less than maximum.")])
            errors['outer_max'] = ErrorList([_("Please make sure minimum is less than maximum.")])
        if errors:
            raise StructBlockValidationError(block_errors=errors)

        return super().clean(value)     

class GridStreamBlock(StreamBlock):
    page_wide_block=FullWidthBaseBlock()
    two_column_block = TwoColumnBaseBlock()
    three_column_block = ThreeColumnBaseBlock()
