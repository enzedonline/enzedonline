from django.core.exceptions import ImproperlyConfigured
from django.forms.models import ModelChoiceIterator
from django.forms.widgets import (
    CheckboxSelectMultiple,
    RadioSelect,
    Select,
    SelectMultiple,
)
from django.utils.translation import gettext_lazy as _
from wagtail.admin.panels import FieldPanel


class LocalizedSelectPanel(FieldPanel):
    """
    Customised FieldPanel to filter choices based on locale of page/model being created/edited
    Usage:
    widget - optional, override field widget type
           - must be one of CheckboxSelectMultiple, RadioSelect, Select or SelectMultiple
    typed_choice_field - set to True with Select widget forces drop down list
    """

    def __init__(
        self,
        field_name,
        widget=None,
        disable_comments=None,
        permission=None,
        read_only=False,
        typed_choice_field=False,
        **kwargs
    ):
        if not widget in [
            None,
            CheckboxSelectMultiple,
            RadioSelect,
            Select,
            SelectMultiple,
        ]:
            raise ImproperlyConfigured(
                _(
                    "widget should be a Django form widget class of type "
                    "CheckboxSelectMultiple, RadioSelect, Select or SelectMultiple"
                )
            )
        super().__init__(
            field_name,
            widget,
            disable_comments,
            permission,
            read_only,
            **kwargs,
        )
        self.typed_choice_field = typed_choice_field

    def clone_kwargs(self):
        kwargs = super().clone_kwargs()
        kwargs.update(typed_choice_field=self.typed_choice_field)
        return kwargs

    class BoundPanel(FieldPanel.BoundPanel):
        def __init__(self, **kwargs):
            super().__init__(**kwargs)
            if not self.panel.widget:
                self.form.fields[self.field_name].widget.choices = self.choice_list
            else:
                self.form.fields[self.field_name].widget = self.panel.widget(
                    choices=self.choice_list
                )
            if self.panel.typed_choice_field:
                self.form.fields[
                    self.field_name
                ].__class__.__name__ = "typed_choice_field"
            pass

        @property
        def choice_list(self):
            self.form.fields[self.field_name].queryset = self.form.fields[
                self.field_name
            ].queryset.filter(locale_id=self.instance.locale_id)
            choices = ModelChoiceIterator(self.form.fields[self.field_name])
            return choices
