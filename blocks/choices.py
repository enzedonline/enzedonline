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
        ('bg-wagtail-dark', _("Wagtail Dark")),
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

class TextSizeChoiceBlock(HeadingSizeChoiceBlock):
    choices=[
        ('h2', 'H2'), 
        ('h3', 'H3'), 
        ('h4', 'H4'), 
        ('h5', 'H5'), 
        ('h6', 'H6'), 
        ('p', 'Body')
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

class CollapsibleChoiceBlock(ChoiceBlock):
    choices=[
        ('disabled', _('Not Collapsible')),
        ('collapsible', _('Collapsible')),
        ('collapsed', _('Collapsed')),
    ]    

class VerticalAlignmentChoiceBlock(DefaultChoiceBlock):
    choices = [
        ('align-items-top', _('Top')), 
        ('align-items-center', _('Middle')), 
        ('align-items-bottom', _('Bottom')), 
    ]
    label=_("Vertical Alignment")
    default='align-items-top'

