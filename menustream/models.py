from django.db import models
from django.utils.translation import gettext_lazy as _
from wagtail.admin.panels import FieldPanel, TitleFieldPanel
from wagtail.admin.widgets.slug import SlugInput
from wagtail.fields import StreamField
from wagtail.images.widgets import AdminImageChooser
from wagtail.models import (DraftStateMixin, Locale, LockableMixin,
                            PreviewableMixin, RevisionMixin, WorkflowMixin)
from wagtail.snippets.models import register_snippet

from .blocks import MenuStreamBlock

BREAKPOINT_CHOICES = (
    # ("-none", _("No breakpoint (always collapsed)")),
    # ("-sm", _("Mobile screens only (<576px)")),
    ("-md", _("Small Screens (<768px)")),
    ("-lg", _("Medium Screens (<992px)")),
    # ("-xl", _("Extra Large (<1200px)")),
    ("", _("Always expanded (no small screen format)"))
)

@register_snippet
class Menu(
    PreviewableMixin,
    WorkflowMixin,
    DraftStateMixin,
    LockableMixin,
    RevisionMixin,
    models.Model,
):
    title = models.CharField(
        max_length=255, 
        verbose_name=_("Menu Title"),
        help_text=_("A descriptive name for this menu (not displayed)")
    )
    slug = models.SlugField(unique=True)
    brand_logo = models.ForeignKey(
        "wagtailimages.Image",
        null=True,
        blank=True,
        related_name="+",
        on_delete=models.SET_NULL,
        verbose_name=_("Optional Menu Logo"),
    )
    brand_title = models.CharField(
        max_length=50, 
        null=True,
        blank=True,
        verbose_name=_("Optional Menu Display Title")
    )
    items = StreamField(
        MenuStreamBlock(), verbose_name="Menu Items", blank=True, use_json_field=True
    )
    breakpoint = models.CharField(
        max_length=4,
        choices=BREAKPOINT_CHOICES,
        default="lg",
        blank=True,
        null=False,
        verbose_name=_("Mobile Layout Breakpoint"),
    )

    panels = [
        TitleFieldPanel("title"),
        FieldPanel("slug", widget=SlugInput),
        FieldPanel("brand_logo", widget=AdminImageChooser(show_edit_link=False)),
        FieldPanel("brand_title"),
        FieldPanel("breakpoint"),
        FieldPanel("items"),
    ]

    def __str__(self) -> str:
        return self.title

    def get_preview_template(self, request, mode_name):
        return "menu/previews/menu.html"

    class Meta:
        verbose_name = _("Menu")
