from django.forms.widgets import Select
from django.utils.html import format_html
from wagtail.admin.panels import FieldPanel
from wagtail.models import Locale


class SubMenuFieldPanel(FieldPanel):
    # Usage: field_name - database field to bind to
    #        list_queryset - queryset to parse for the dropdown options
    #                      - amend _get_choice_list() to filter and return list of value/display tuples
    #        DO NOT add choices to field definition or pass a widget to this panel
    #
    # Customised FieldPanel to allow dynamic drop down content based on the parent properties.
    # Very specific to the SubMenu orderble but could be reworked for a more generic needs.
    # To repurpose, pass the desired queryset to the list_queryset argument, amend _get_choice_list
    #
    # Filters menu choices based on locale and excludes the current menu from the list
    # Needs revisiting - couldn't find any way to access parent class (Menu) properties from here
    # in the end, used uri which has parent id (if it has been saved) or locale if it's a new menu
    # if it has been saved, locale can be derived from the parent id
    #
    # Make sure field model does not declare choices - this makes the choices static
    # Queryset must be passed in as it is the Menu object set. Importing in this module 
    # causes circular reference.

    def __init__(self, field_name, list_queryset, *args, **kwargs):
        self.list_queryset = list_queryset
        super().__init__(field_name, *args, **kwargs)

    def clone_kwargs(self):
        return {
            'heading': self.heading,
            'classname': self.classname,
            'help_text': self.help_text,
            'list_queryset': self.list_queryset,
            'field_name': self.field_name,
        }

    class BoundPanel(FieldPanel.BoundPanel):
        def __init__(self, **kwargs):
            super().__init__(**kwargs)           
            # declare widget with choices (this event seems to get called twice)
            # change field type to typed_choice_field otherwise it'll appear as a text field with
            # dropdown behaviour
            self.form.fields[self.field_name].widget = Select(choices=self._get_choice_list())
            self.form.fields[self.field_name].__class__.__name__ = 'typed_choice_field'

        # Get parent id (if any) and locale id - logic based on uri of form
        # uri ends with parent id if it is in edit mode, ends in add/?locale=code if it is in add new mode
        # Fudge to get around lack of access to parent object
        # Must be called after request is bound
        # Called from form_bound event via _get_choice_list() here
        def _get_locale_and_parent(self):
            path = str(self.request)
            if path.split('/')[-2] == 'add':
                locale_id = Locale.objects.get(language_code=path.split('/')[-1].replace('?locale=','')).pk
                parent_menu_id = None
            else:
                parent_menu = self.panel.list_queryset.get(id=int(path.split('/')[-2]))
                parent_menu_id = getattr(parent_menu, 'id')  
                locale_id = getattr(parent_menu, 'locale_id')  
            return parent_menu_id, locale_id

        # Create a list from the full queryset filtered by locale, exclude parent
        def _get_choice_list(self):
            parent_menu_id, locale_id = self._get_locale_and_parent()
            menu_list = self.panel.list_queryset
            if locale_id:
                menu_list = menu_list.filter(locale_id=locale_id)
            if parent_menu_id:
                menu_list = menu_list.exclude(id=parent_menu_id)
            return [('', '------')] + list(menu_list.values_list('id','title'))
