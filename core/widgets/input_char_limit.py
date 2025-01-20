from django.forms import Media
from django.forms.widgets import TextInput
from django.template.loader import render_to_string
from django.utils.functional import cached_property
from django.utils.translation import gettext_lazy as _
from wagtail.admin.widgets import AdminAutoHeightTextInput
from typing import Optional


class CharLimitMixin:
    def __init__(self, min: int = 0, max: Optional[int] = None, enforced: bool = False, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.minimum = min
        self.maximum = max
        self.enforced = enforced
        self.requirements = f'{_("Characters Required")}: {self.minimum}'
        if self.maximum: self.requirements += f' - {self.maximum}'

    def render(self, name, value, attrs, renderer=None):
        rendered_field = super().render(name, value, attrs, renderer)
        if self.minimum > 0 or self.maximum != None:
            context = {
                "id": f'{attrs.get("id")}',
                "min": self.minimum,
                "max": self.maximum,
                "enforced": self.enforced,
                "requirements": self.requirements,
                "used_label": _("Used")
            }
            return rendered_field + render_to_string(
                "widgets/input-char-limit-widget.html", context
            )
        else:
            return rendered_field

    @cached_property
    def media(self):
        widget_media = super().media
        return Media(
            js=widget_media._js + ["js/widgets/input-char-limit-widget.js"],
            css={"all": ("css/widgets/input-char-limit-widget.css",)},
        )

class CharLimitTextInput(CharLimitMixin, TextInput):
    pass

class CharLimitTextArea(CharLimitMixin, AdminAutoHeightTextInput):
    pass