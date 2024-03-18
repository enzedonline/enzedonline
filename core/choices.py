from django.utils.translation import gettext_lazy as _
from wagtail.blocks import ChoiceBlock

class DefaultChoiceBlock(ChoiceBlock):

    def __init__(self, *args, **kwargs):

        default = kwargs.pop("default", getattr(self, "default", None))
        label = kwargs.pop("label", getattr(self, "label", None))
        help_text = kwargs.pop("help_text", getattr(self, "help_text", None))
        required = kwargs.pop("required", getattr(self, "required", True))

        super().__init__(
            *args,
            default=default,
            label=label,
            help_text=help_text,
            required=required,
            **kwargs
        )
        
class AlignmentChoiceBlock(DefaultChoiceBlock):
    choices=[
        ('start', _('Left')), 
        ('center', _('Centre')), 
        ('end', _('Right'))
    ]

class TextAlignmentChoiceBlock(DefaultChoiceBlock):
    choices=[
        ('justify', _('Justified')), 
        ('start', _('Left')), 
        ('center', _('Centre')), 
        ('end', _('Right'))
    ]

class ColourThemeChoiceBlock(DefaultChoiceBlock):
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

class ButtonChoiceBlock(DefaultChoiceBlock):
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
    label=_("Button Appearance")
    
class ButtonSizeChoiceBlock(DefaultChoiceBlock):
    choices=[
        ('btn-sm', _("Small")),
        (' ', _("Standard")),
        ('btn-lg', _("Large")),
    ]
    default=' '
    label=_("Button Size")
    
class HeadingSizeChoiceBlock(DefaultChoiceBlock):
    choices=[
        ('h2', 'H2'), 
        ('h3', 'H3'), 
        ('h4', 'H4'), 
        ('h5', 'H5'), 
        ('h6', 'H6'), 
    ]

class ImageFormatChoiceBlock(DefaultChoiceBlock):
    choices=[
        ('4-1', _("4:1 Horizontal Letterbox Banner")),
        ('3-1', _("3:1 Horizontal Panorama Banner")),
        ('4-3', _("4:3 Horizontal Standard Format")),
        ('1-1', _("1:1 Square Format")),
        ('3-4', _("3:4 Portrait Standard Format")),
        ('1-3', _("1:3 Vertical Panorama Banner")),
    ]

class RouteOptionChoiceBlock(DefaultChoiceBlock):
     choices=[
        ('no-route', "None"),
        ('walking', "Walking"),
        ('cycling', "Cycling"),
        ('driving', "Driving"),
        ('driving-traffic', "Driving (with traffic conditions)")
     ]

class FlexCardLayoutChoiceBlock(DefaultChoiceBlock):
    choices=[
        ('image-left-responsive', _("Responsive Horizontal (Image left of text on widescreen only)")),
        ('image-right-responsive', _("Responsive Horizontal (Image right of text on widescreen only)")),
        ('image-left-fixed', _("Fixed Horizontal (Image left of text on all screen sizes)")),
        ('image-right-fixed', _("Fixed Horizontal (Image right of text on all screen sizes)")),
        ('vertical', _("Vertical (Image above text on on all screen sizes)")),
    ]

class BreakpointChoiceBlock(DefaultChoiceBlock):
    choices=[
        ('sm', _("Small screen only")),
        ('md', _("Small and medium screens")),
    ]

class CodeChoiceBlock(DefaultChoiceBlock):
    choices=[
        ('python', 'Python'),
        ('css', 'CSS'),
        ('html', 'HTML'),
        ('javascript', 'Javascript'),
        ('bash', 'Bash/Shell'),
        ('django', 'Django Template'),
        ('json', 'JSON'),
        ('sql', 'SQL'),
        ('xml', 'XML'),
        ('git', 'Git'),
        ('powershell', 'PowerShell'),
        ('r', 'R'),
        ('vba', 'VBA'),
        ('vbnet', 'VB.NET'),
    ]

class CollapsibleChoiceBlock(ChoiceBlock):
    choices=[
        ('simple', 'Not Collapsible'),
        ('collapsible', 'Collapsible'),
        ('collapsed', 'Collapsed'),
    ]    

class VerticalAlignmentChoiceBlock(DefaultChoiceBlock):
    choices = [
        ('align-items-top', _('Top')), 
        ('align-items-center', _('Middle')), 
        ('align-items-bottom', _('Bottom')), 
    ]
    label=_("Vertical Alignment")
    default='align-items-top'
    
class DocumentListSortChoiceBlock(DefaultChoiceBlock):
    choices = [
        ('created_at', _('Date (newest first)')), 
        ('title', _('Document Title')), 
    ]
    default = 'created_at'
    label = _("Sort Order")

#-----------------------------------------------------
# GridStream options
#-----------------------------------------------------
    
class TwoColumnCollapseOrderChoiceBlock(DefaultChoiceBlock):
    default='left-first'
    choices=[
        ('left-first', _("Left column is first on mobile")),
        ('right-first', _("Right column is first on mobile")),
    ]
    label=_("Column order on mobile")
    help_text=_("Select which column will appear above the other on mobile screen")
    
class TwoColumnHideChoiceBlock(DefaultChoiceBlock):
    default='hide-none'
    choices=[
        ('hide-none', _("Display both column contents on mobile (one above the other)")),
        ('hide-left', _("Hide the left column contents on mobile")),
        ('hide-right', _("Hide the right column contents on mobile")),
    ]
    label=_("Hide contents on mobile")

class TwoColumnLayoutChoiceBlock(DefaultChoiceBlock):
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
    default = '6-6',
    label = _("Select column size ratio")

class ThreeColumnHideChoiceBlock(DefaultChoiceBlock):
    default='hide-none'
    choices=[
        ('hide-none', _("Display all columns on mobile (one above the other)")),
        ('hide-sides', _("Hide the left and right columns contents on mobile")),
    ]
    label=_("Hide contents on mobile")
    
class ThreeColumnLayoutChoiceBlock(DefaultChoiceBlock):
    choices = [
        ('-auto-', _("Centre column width determined by content (care needed, test on all screen sizes)")),
        ('4-4-4', _("Equal Width Columns")),
        ('3-6-3', _("Left 3, Centre 6, Right 3")),
        ('2-8-2', _("Left 2, Centre 8, Right 2")),
        ('1-10-1', _("Left 1, Centre 10, Right 1")),
    ]

class BreakPointChoiceBlock(DefaultChoiceBlock):
    choices = [
        ('-', _("Columns side by side on all screen sizes (best for uneven column sizes)")),
        ('-lg', _("Columns side by side on large screen only")),
        ('-md', _("Columns side by side on medium and large screen only")),
        ('-sm', _("Single column on mobile, side by side on all other screens"))
    ]
    label = _("Select responsive layout behaviour")

