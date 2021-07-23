from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
from django.forms.utils import ErrorList
from wagtail.core.blocks.field_block import IntegerBlock, URLBlock
from wagtail.images.blocks import ImageChooserBlock
from wagtail.embeds.blocks import EmbedBlock
from wagtail.core import blocks as wagtail_blocks
from wagtail.core.blocks import CharBlock, TextBlock, StreamBlock, StructBlock, RawHTMLBlock
from wagtail_localize.synctree import Locale

import core.metadata 

class HiddenCharBlock(CharBlock):
    pass

class ColourThemeChoiceBlock(wagtail_blocks.ChoiceBlock):
    choices=[
        ('text-black bg-transparent', _("Transparent")),
        ('text-white bg-primary', _("Primary")),
        ('text-white bg-secondary', _("Secondary")),
        ('text-white bg-success', _("Success")),
        ('text-white bg-info', _("Info")),
        ('text-white bg-warning', _("Warning")),
        ('text-white bg-danger', _("Danger")),
        ('text-black bg-light', _("Light")),
        ('text-white bg-dark', _("Dark")),
    ]

class ButtonChoiceBlock(wagtail_blocks.ChoiceBlock):
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

class ImageFormatChoiceBlock(wagtail_blocks.ChoiceBlock):
    choices=[
        ('4-1', _("4:1 Horizontal Letterbox Banner")),
        ('3-1', _("3:1 Horizontal Panorama Banner")),
        ('4-3', _("4:3 Horizontal Standard Format")),
        ('1-1', _("1:1 Square Format")),
        ('3-4', _("3:4 Portrait Standard Format")),
        ('1-3', _("1:3 Vertical Panorama Banner")),
    ]

class SEOImageChooseBlock(StructBlock):
    file = ImageChooserBlock(required=True, label=_("Image"))
    seo_title = CharBlock(
        required=True,
        label=_("SEO Title")
    )

class ImageBlock(StructBlock):
    """
    Custom `StructBlock` for utilizing images with associated caption and
    attribution data
    """
    image = SEOImageChooseBlock(required=True, label=_("Select Image & Enter Details"))
    caption = CharBlock(required=False, label=_("Image Caption (optional)"))
    attribution = CharBlock(required=False, label=_("Image Attribution (optional)"))
    background = ColourThemeChoiceBlock(
        default='bg-transparent',
        label=_("Card Background Colour")
    )
    class Meta:
        icon = 'image'
        template = "blocks/image_block.html"

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

class Link_Value(wagtail_blocks.StructValue):
    """ Additional logic for the Link class """

    def url(self) -> str:
        internal_page = self.get("internal_page")
        url_link = self.get("url_link")
        if internal_page:
            return internal_page.localized.url
        elif url_link:
            if url_link.startswith('/'): # presumes internal link starts with '/' and no lang code
                url = '/' + Locale.get_active().language_code + url_link
            else: # external link, do not translate but add new tab instruction
                #@TODO: target blank doesn't work on buttons, look for a workaround
                url = url_link + '" target="_blank' 
            return url
        else:
            return None

class Link(wagtail_blocks.StructBlock):
    button_text = wagtail_blocks.CharBlock(
        max_length=50,
        null=False,
        blank=False,
        label=_("Button Text")
    )
    internal_page = wagtail_blocks.PageChooserBlock(
        required=False,
        label=_("Link to internal page")
    )
    url_link = wagtail_blocks.CharBlock(
        required=False,
        label=_("Link to external site or internal URL")
    )
    appearance = ButtonChoiceBlock(
        max_length=15,
        default='btn-primary',
        label=_("Button Appearance")
    )
    placement = wagtail_blocks.ChoiceBlock(
        max_length=15,
        default='right',
        choices=[
            ('start', _("Left")),
            ('center', _("Centre")),
            ('end', _("Right")),
        ],
        label=_("Button Placement")
    )
    size = wagtail_blocks.ChoiceBlock(
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
            errors['internal_page'] = ErrorList(["Please select an internal page or an external link (but not both)"])
            errors['url_link'] = ErrorList(["Please select an internal page or an external link (but not both)"])

        if errors:
            raise ValidationError("Please check the errors below and correct before saving", params=errors)

        return super().clean(value)

class SimpleRichTextBlock(wagtail_blocks.StructBlock):
    alignment = wagtail_blocks.ChoiceBlock(
        choices = [
            ('justify', 'Justified'), 
            ('start', 'Left'), 
            ('center', 'Centre'), 
            ('end', 'Right')
        ],
        default='justify'
    )
    content = wagtail_blocks.RichTextBlock(
        features= [
            'h1', 'h2', 'h3', 'h4', 'h5', 'h6',
            'bold',
            'italic',
            'ol',
            'ul',
            'link',
            'hr',
			'small',
            'code',
        ]
    )

    class Meta:
        template = 'blocks/simple_richtext_block.html'
        label = _("Formatted Text Block")
        icon = 'fa-text-height'

class FlexCard(wagtail_blocks.StructBlock):
    
    format = wagtail_blocks.ChoiceBlock(
        max_length=15,
        default='vertical',
        choices=[
            ('image-left-responsive', _("Responsive Horizontal (Image left of text on widescreen only)")),
            ('image-right-responsive', _("Responsive Horizontal (Image right of text on widescreen only)")),
            ('image-left-fixed', _("Fixed Horizontal (Image left of text on all screen sizes)")),
            ('image-right-fixed', _("Fixed Horizontal (Image right of text on all screen sizes)")),
            ('vertical', _("Vertical (Image above text on on all screen sizes)")),
        ],
        label=_("Card Format")
    )    
    background = ColourThemeChoiceBlock(
        default='bg-transparent',
        label=_("Card Background Colour")
    )
    border = wagtail_blocks.BooleanBlock(
        default=True,
        required=False,
        label=_("Border"),
        help_text=_("Draw a border around the card?")
    )
    full_height = wagtail_blocks.BooleanBlock(
        default=True,
        required=False,
        label=_("Full Height"),
        help_text=_("Card uses all available height")
    )
    text = SimpleRichTextBlock(
        label=_("Card Body Text"),
        help_text=_("Body text for this card."),
    )
    image = SEOImageChooseBlock(
        label=_("Select Image & Enter Details"),
        help_text=_("Card Image (approx 1:1.4 ratio - ideally upload 2100x1470px)."),
    )

    class Meta:
        template = 'blocks/flex_card_block.html'
        label = _("Image & Text Card")
        icon = 'fa-address-card'

class CallToActionCard(FlexCard):
    link = Link(
        label=_("Link Button"),
        help_text = _("Enter a link or select a page and choose button options."),
        required=False,
    )
    class Meta:
        template = 'blocks/call_to_action_card_block.html'
        label = _("Call-To-Action Card (Image/Text/Button)")
        icon = 'fa-address-card'

class SimpleCard(wagtail_blocks.StructBlock):
    background = ColourThemeChoiceBlock(
        default='bg-transparent',
        label=_("Card Background Colour")
    )    
    border = wagtail_blocks.BooleanBlock(
        default=True,
        required=False,
        label=_("Border"),
        help_text=_("Draw a border around the card?")
    )
    full_height = wagtail_blocks.BooleanBlock(
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

class SimpleCardGridBlock(wagtail_blocks.StructBlock):
    columns = wagtail_blocks.ChoiceBlock(
        max_length=40,
        default='row-cols-1 row-cols-sm-2 row-cols-md-3 row-cols-lg-4',
        choices=[
            ('row-cols-1 row-cols-sm-2 row-cols-md-3 row-cols-lg-4', _("Mobile:1 Max:4")),
            ('row-cols-1 row-cols-md-2', _("Mobile:1 Max:2")),
            ('row-cols-2 row-cols-md-3 row-cols-lg-4', _("Mobile:2 Max:4")),
        ],
        label=_("Maximum Cards per Row")
    )
    cards = SimpleCardStreamBlock()

    class Meta:
        template = "blocks/simple_card_grid_block.html"
        icon = 'fa-th'
        label = _("Flexible Grid of Simple Cards")

class InlineVideoBlock(wagtail_blocks.StructBlock):
    video = EmbedBlock(
        label=_("Video URL"),
        help_text = _("eg 'https://www.youtube.com/watch?v=kqN1HUMr22I'")
    )
    caption = CharBlock(required=False, label=_("Caption"))
    float = wagtail_blocks.ChoiceBlock(
        required=False,
        choices=[('right', _("Right")), ('left', _("Left")), ('center', _("Center"))],
        default='right',
        label=_("Float"),
    )
    size = wagtail_blocks.ChoiceBlock(
        required=False,
        choices=[('small', _("Small")), ('medium', _("Medium")), ('large', _("Large"))],
        default='small',
        label=_("Size"),
    )

    class Meta:
        icon = 'media'
        template = 'blocks/inline_video_block.html'
        label = _("Embed external video")    

class SocialMediaEmbedBlock(wagtail_blocks.StructBlock):
    embed_code = RawHTMLBlock(
        label=_("Paste Embed code block from Provider"),
        help_text=_("Paste in only embed code. For Facebook, only Step 2 on the JavaScript SDK tab")
    )
    class Meta:
        template='blocks/social_media_embed.html'
        icon = 'fa-share-alt-square'
        label = _("Embed Social Media Post")

class HtmlBlock(wagtail_blocks.StructBlock):
    code = RawHTMLBlock(
        label=_("Enter HTML Code")
    )
    class Meta:
        template='blocks/html_code_block.html'
        icon = 'fa-file-code'
        label = _("Embed HTML Code")

class ExternalLinkEmbedBlock(wagtail_blocks.StructBlock):
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
    format = wagtail_blocks.ChoiceBlock(
        max_length=15,
        default='vertical',
        choices=[
            ('image-left-responsive', _("Responsive Horizontal (Image left of text on widescreen only)")),
            ('image-right-responsive', _("Responsive Horizontal (Image right of text on widescreen only)")),
            ('image-left-fixed', _("Fixed Horizontal (Image left of text on all screen sizes)")),
            ('image-right-fixed', _("Fixed Horizontal (Image right of text on all screen sizes)")),
            ('vertical', _("Vertical (Image above text on on all screen sizes)")),
        ],
        label=_("Card Format")
    )    
    background = ColourThemeChoiceBlock(
        default='bg-transparent',
        label=_("Card Background Colour")
    )
    border = wagtail_blocks.BooleanBlock(
        default=True,
        required=False,
        label=_("Border"),
        help_text=_("Draw a border around the card?")
    )
    full_height = wagtail_blocks.BooleanBlock(
        default=True,
        required=False,
        label=_("Full Height"),
        help_text=_("Card uses all available height")
    )
    button_text = wagtail_blocks.CharBlock(
        label=_("Text for link to article"),
        default=_("Read Full Article")
    )
    button_appearance = ButtonChoiceBlock(
        max_length=15,
        default='btn-primary',
        label=_("Button Appearance")
    )
    button_placement = wagtail_blocks.ChoiceBlock(
        max_length=15,
        default='right',
        choices=[
            ('left', _("Left")),
            ('center', _("Centre")),
            ('right', _("Right")),
        ],
        label=_("Button Placement")
    )
    button_size = wagtail_blocks.ChoiceBlock(
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

            if errors:
                raise ValidationError(_("Please check the errors below and correct before saving"), params=errors)

        return super().clean(value)

class CarouselImageBlock(wagtail_blocks.StructBlock):
    image = SEOImageChooseBlock(label=_("Select Image & Enter Details"))
    title = wagtail_blocks.CharBlock(label=_("Optional Image Title"), required=False)
    caption = wagtail_blocks.TextBlock(label=_("Optional Image Caption"), required=False)
    link = wagtail_blocks.PageChooserBlock(
        required=False,
        label=_("Optional Link to Internal Page")
    )
    class Meta:
        icon = 'image'
        label = _("Image for Carousel")

class CarouselImageStreamBlock(StreamBlock):
    carousel_image = CarouselImageBlock()

class ImageCarouselBlock(wagtail_blocks.StructBlock):
    format = ImageFormatChoiceBlock(
        default='4-3',
        label=_("Select image aspect ratio"),
    )
    heading = wagtail_blocks.CharBlock(
        label=_("Carousel Title"), 
        required=False,
    )
    carousel_images = CarouselImageStreamBlock(min_num=2, max_num=5)
    
    class Meta:
        template='blocks/image_carousel.html'
        icon="fa-clone"
        label = _("Image Carousel")

class CollapsableCard(wagtail_blocks.StructBlock):
    header = wagtail_blocks.CharBlock(
        label=_("Card Banner Title")
    )
    text = SimpleRichTextBlock(
        label=_("Card Body Text"),
        help_text=_("Body text for this card."),
    )

class CollapsableCardStreamBlock(StreamBlock):
    collapsable_card = CollapsableCard()

class CollapsableCardBlock(wagtail_blocks.StructBlock):
    header_colour  = ColourThemeChoiceBlock(
        default='text-white bg-dark',
        label=_("Card Header Background Colour")
    )    
    body_colour  = ColourThemeChoiceBlock(
        default='text-black bg-light',
        label=_("Card Body Background Colour")
    )
    cards = CollapsableCardStreamBlock(min_num=2)

    class Meta:
        template='blocks/collapsable_card_block.html'
        icon="fa-stack-overflow"
        label = _("Collapsable Text Block")

CODE_CHOICES  = (
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
)

class BlogCodeBlock(wagtail_blocks.StructBlock):
    language = wagtail_blocks.ChoiceBlock(choices=CODE_CHOICES, default='python')
    code = wagtail_blocks.TextBlock()

    class Meta:
        template = "blocks/code_block.html"
        icon = "fa-code"
        label = "Code Block"

class EmptyStaticBlock(wagtail_blocks.StaticBlock):
    class Meta:
        template = 'blocks/empty_block.html'
        icon = 'placeholder'
        label = 'Empty Block'

class SpacerStaticBlock(wagtail_blocks.StaticBlock):
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
        default='bg-transparent',
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

class BaseStreamBlock(StreamBlock):
    richtext_block = SimpleRichTextBlock()
    image_block = ImageBlock()
    block_quote = BlockQuote()
    link_button = Link()
    flex_card = FlexCard()
    call_to_action_card = CallToActionCard()
    simple_card = SimpleCard()
    simple_card_grid = SimpleCardGridBlock()
    collapsible_card_block = CollapsableCardBlock()
    social_media_embed = SocialMediaEmbedBlock()
    external_link_embed = ExternalLinkEmbedBlock()
    inline_video_block = InlineVideoBlock()
    image_carousel = ImageCarouselBlock()
    code_block = BlogCodeBlock()
    latest_blog_posts = LatestBlogPostGrid()
    spacer_block = SpacerStaticBlock()
    empty_block = EmptyStaticBlock()

class TwoColumnLayoutChoiceBlock(wagtail_blocks.ChoiceBlock):
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

class ThreeColumnLayoutChoiceBlock(wagtail_blocks.ChoiceBlock):
    choices = [
        ('-auto-', _("Centre column width determined by content (care needed, test on all screen sizes)")),
        ('4-4-4', _("Equal Width Columns")),
        ('3-6-3', _("Left 3, Centre 6, Right 3")),
        ('2-8-2', _("Left 2, Centre 8, Right 2")),
        ('1-10-1', _("Left 1, Centre 10, Right 1")),
    ]

class BreakPointChoiceBlock(wagtail_blocks.ChoiceBlock):
    choices = [
        ('-', _("Columns side by side on all screen sizes (best for uneven column sizes)")),
        ('-lg', _("Columns side by side on large screen only")),
        ('-md', _("Columns side by side on medium and large screen only")),
        ('-sm', _("Single column on mobile, side by side on all other screens"))
    ]

class FullWidthBaseBlock(wagtail_blocks.StructBlock):
    column = BaseStreamBlock(
        label=_("Single Column Contents"),
        blank=True,
        Null=True
    )

    class Meta:
        template = 'blocks/full_width_block.html'
        icon = 'arrows-alt-h'
        label = "Page Wide Block"

class TwoColumnBaseBlock(wagtail_blocks.StructBlock):
    column_layout = TwoColumnLayoutChoiceBlock(
        default = '6-6',
        label = _("Select column size ratio")
    )
    breakpoint = BreakPointChoiceBlock(
        default = '-sm',
        label = _("Select responsive layout behaviour")
    )
    horizontal_padding = IntegerBlock(
        default = 4,
        max_value=5
    )
    vertical_border = wagtail_blocks.BooleanBlock(
        default=False,
        required=False,
        label=_("Vertical Border"),
        help_text=_("Add a vertical line between columns")
    )
    order = wagtail_blocks.ChoiceBlock(
        max_length=15,
        default='left-first',
        choices=[
            ('left-first', _("Left column is first on mobile")),
            ('right-first', _("Right column is first on mobile")),
        ],
        label=_("Column order on mobile"),
        help_text=_("Select which column will appear above the other on mobile screen")
    )    
    hide = wagtail_blocks.ChoiceBlock(
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

class ThreeColumnBaseBlock(wagtail_blocks.StructBlock):
    column_layout = ThreeColumnLayoutChoiceBlock(
        default = '4-4-4',
        label = _("Select column size ratio")
    )
    breakpoint = BreakPointChoiceBlock(
        default = '-md',
        label = _("Select responsive layout behaviour")
    )
    horizontal_padding = IntegerBlock(
        default = 4,
        max_value=5
    )
    vertical_border = wagtail_blocks.BooleanBlock(
        default=False,
        required=False,
        label=_("Vertical Border"),
        help_text=_("Add a vertical line between columns")
    )
    hide = wagtail_blocks.ChoiceBlock(
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

class GridStreamBlock(StreamBlock):
    page_wide_block=FullWidthBaseBlock()
    two_column_block = TwoColumnBaseBlock()
    three_column_block = ThreeColumnBaseBlock()
