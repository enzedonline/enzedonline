from django.forms.widgets import CheckboxSelectMultiple
from wagtail.admin.panels import FieldPanel
from wagtail.models import Page

class MultiChoiceLocaleFieldPanel(FieldPanel):
    # Usage: field_name - database field to bind to
    #        list_queryset - queryset to parse for the dropdown options
    #                      - amend _get_choice_list() to filter and return list of value/display tuples
    #        display_field - field name in queryset to use as label for choices
    #        DO NOT add choices to field definition or pass a widget to this panel
    #
    # Customised FieldPanel to allow dynamic multi-choice checkboxes based on the parent properties.
    # To repurpose, pass the desired queryset to the list_queryset argument, amend _get_choice_list
    #
    # Filters choices based on locale of page being created/edited
    #
    # Make sure field model does not declare choices - this makes the choices static

    def __init__(self, field_name, list_queryset, display_field, *args, **kwargs):
        self.list_queryset = list_queryset
        self.display_field = display_field
        super().__init__(field_name, *args, **kwargs)

    def clone_kwargs(self):
        return {
            'heading': self.heading,
            'classname': self.classname,
            'help_text': self.help_text,
            'list_queryset': self.list_queryset,
            'field_name': self.field_name,
            'display_field': self.display_field,
        }

    class BoundPanel(FieldPanel.BoundPanel):
        def __init__(self, **kwargs):
            super().__init__(**kwargs)           
            # declare widget with choices 
            self.form.fields[self.field_name].widget = CheckboxSelectMultiple(choices=self._get_choice_list())

        # Get locale id - logic based on uri of form
        # uri ends with parent id if it is in add new mode, ends in /edit/ if it is in edit mode
        # In edit made, take the id of page being edited to find locale, in add new mode, take the parent id to find locale
        # Fudge to get around lack of access to locale
        # Must be called after request is bound
        def _get_locale(self):
            path = str(self.request)
            if path.split('/')[-2] == 'edit':
                page = Page.objects.get(id=int(path.split('/')[-3]))
            else:
                page = Page.objects.get(id=int(path.split('/')[-2]))
            locale_id = getattr(page, 'locale_id')
            return locale_id

        # Create a list from the full queryset filtered by locale
        def _get_choice_list(self):
            locale_id = self._get_locale()
            choices = self.panel.list_queryset
            if locale_id:
                choices = choices.filter(locale_id=locale_id)
            return list(choices.values_list('id', self.panel.display_field))
