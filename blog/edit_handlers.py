from django.core.exceptions import ImproperlyConfigured
from django.forms.models import ModelChoiceIterator
from django.forms.widgets import (CheckboxSelectMultiple, RadioSelect, Select,
                                  SelectMultiple)
from django.utils.translation import gettext_lazy as _
from wagtail.admin.panels import FieldPanel


class LocalizedSelectPanel(FieldPanel):
    """
    Customised FieldPanel to filter choices based on locale of page/model being created/edited
    Usage: 
    widget_class - optional, override field widget type
                 - should be CheckboxSelectMultiple, RadioSelect, Select or SelectMultiple
    typed_choice_field - set to True with Select widget forces drop down list 
    """

    def __init__(self, field_name, widget_class=None, typed_choice_field=False, *args, **kwargs):
        if not widget_class in [None, CheckboxSelectMultiple, RadioSelect, Select, SelectMultiple]:
            raise ImproperlyConfigured(_(
                "widget_class should be a Django form widget class of type "
                "CheckboxSelectMultiple, RadioSelect, Select or SelectMultiple"
            ))
        self.widget_class = widget_class
        self.typed_choice_field = typed_choice_field
        super().__init__(field_name, *args, **kwargs)

    def clone_kwargs(self):
        return {
            'heading': self.heading,
            'classname': self.classname,
            'help_text': self.help_text,
            'widget_class': self.widget_class,
            'typed_choice_field': self.typed_choice_field,
            'field_name': self.field_name,
        }

    class BoundPanel(FieldPanel.BoundPanel): 
        def __init__(self, **kwargs):
            super().__init__(**kwargs)           
            if not self.panel.widget_class:
                self.form.fields[self.field_name].widget.choices=self.choice_list
            else:
                self.form.fields[self.field_name].widget = self.panel.widget_class(choices=self.choice_list)
            if self.panel.typed_choice_field:
                self.form.fields[self.field_name].__class__.__name__ = 'typed_choice_field'
            pass

        @property
        def choice_list(self):
            self.form.fields[self.field_name].queryset = self.form.fields[self.field_name].queryset.filter(locale_id=self.instance.locale_id)
            choices = ModelChoiceIterator(self.form.fields[self.field_name])
            return choices
        
