# core/widgets/import_textarea.py

from django import forms
from django.template.loader import render_to_string
from django.utils.functional import cached_property
from django.utils.translation import gettext_lazy as _
from wagtail.admin.widgets import AdminAutoHeightTextInput


class ImportTextAreaWidget(AdminAutoHeightTextInput):
    def __init__(self, file_type_filter=None, attrs={}):
        self.accept = file_type_filter
        if not attrs.get("rows"):
            attrs["rows"] = 5
        super().__init__(attrs)

    msg = {
        "help": _("Use 'Choose File' or drag/drop to import data from file."),
        "button_label": _("Choose file"),
    }

    def render(self, name, value, attrs, renderer=None):
        context = {
            "id": f'{attrs.get("id")}',
            "label": self.msg["button_label"],
            "help": self.msg["help"],
            "accept": self.accept,
        }
        return super().render(name, value, attrs, renderer) + render_to_string(
            "widgets/import_textarea_widget.html", context
        )

    @cached_property
    def media(self):
        widget_media = super().media
        return forms.Media(
            js=widget_media._js + ["js/widgets/import-textarea-widget.js"],
            css={"all": ("css/widgets/import-textarea-widget.css",)},
        )
