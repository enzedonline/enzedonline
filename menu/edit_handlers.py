from django.forms.widgets import Select
from wagtail_localize.synctree import Locale
from django.utils.html import format_html
from wagtail.admin.panels import (
    EditHandler,
    FieldPanel,
)

class ReadOnlyPanel(EditHandler):
    """ ReadOnlyPanel EditHandler Class - built from ideas on https://github.com/wagtail/wagtail/issues/2893
        Most credit to @BertrandBordage for this.
        Usage:
        fieldname:          name of field to display
        style:              optional, any valid style string
        add_hidden_input:   optional, add a hidden input field to allow retrieving data in form_clean (self.data['field'])
        If the field name is invalid, or an error is received getting the value, empty string is returned.
        """
    def __init__(self, fieldname, style=None, add_hidden_input=False, *args, **kwargs):
        # error if fieldname is not string
        if type(fieldname)=='str':
            self.fieldname = fieldname
        else:
            try:
                self.fieldname = str(fieldname)
            except:
                pass
        self.style = style
        self.add_hidden_input = add_hidden_input
        super().__init__(*args, **kwargs)

    def clone(self):
        return self.__class__(
            fieldname=self.fieldname,
            heading=self.heading,
            help_text=self.help_text,
            style=self.style,
            add_hidden_input=self.add_hidden_input,
        )
        
    class BoundPanel(EditHandler.BoundPanel):

        def get_value(self):
            # try to get the value of field, return empty string if failed
            try:
                value = getattr(self.instance, self.panel.fieldname)
                if callable(value):
                    value = value()
            except AttributeError:
                value = ''
            return value
        
        def render_html(self):
            # return formatted field value
            self.value = self.get_value()
            return format_html('<div style="padding-top: 1.2em;">{}</div>', self.value)

        def render(self):
            # return formatted field value
            self.value = self.get_value()
            return format_html('<div style="padding-top: 1.2em;">{}</div>', self.value)

        def render_as_object(self):
            return format_html(
                '<fieldset>{}'
                '<ul class="fields"><li><div class="field">{}</div></li></ul>'
                '</fieldset>',
                self.panel.heading('legend'), self.render())

        def hidden_input(self):
            # add a hidden input field if selected, field value can be retrieved in form_clean with self.data['field']
            if self.panel.add_hidden_input:
                input = f'<input type="hidden" name="{self.panel.fieldname}" value="{self.value}" id="id_{self.panel.fieldname}">'
                return format_html(input)
            return ''

        def heading_tag(self, tag):
            # add the label/legend tags only if heading supplied
            if self.heading:
                if tag == 'legend':
                    return format_html('<legend>{}</legend>', self.panel.heading)
                return format_html('<label>{}{}</label>', self.panel.heading, ':')
            return ''

        def get_style(self):
            # add style if supplied
            if self.panel.style:
                return format_html('style="{}"', self.panel.style)
            return ''

        def render_as_field(self):
            # render the final output
            return format_html(
                '<div class="field" {}>'
                '{}'
                '<div class="field-content">{}</div>'
                '{}'
                '</div>',
                format_html(self.get_style()), self.heading_tag('label'), self.render(), self.hidden_input())  

class RichHelpPanel(EditHandler):
    """ RichHelpPanel EditHandler Class - built on the ReadOnlyPanel
        Like the HelpPanel but with basic HTML tags and dynamic content
        Supply a Django template like text and a value dictionary
        Template tags ({{tag}}) that match dictionary keys will be replaced with the value from the dictionary.
        If the key/tag matches a field name, the value of that field will be swapped in.
        If the key/tag is not a field, then the value from the dictionary (eg a function result) is swapped in.
        Usage:
        text:       unparsed text to display - use template tags {{tag}} as placeholders for data to be swapped in
                    basic html tags are rendered (formatting, links, line breaks etc)
        value_dict: optional dictionary containing tags and corresponding values
                    key name must match a {{tag}} in the text to be swapped in
                    if the value matches a field name, the value from that field is swapped in
                    if the value doesn't match (eg value is the return from a function), the dictionary value is swapped in
        style:      optional, any valid style string

        Example usage:
        msg=_('This snippet\'s slug is <b>{{the_slug}}</b>.<br>Today\'s date is {{today}}<br><a href="/somepage" target="_blank">Read More</a>')
        values={'the_slug': 'slug', 'today': datetime.today().strftime('%d-%B-%Y')}
        style="color:blue;text-align:center"
        panels = [
            RichHelpPanel(
                msg, 
                style=style,
                value_dict=values,
                heading=_("Rich Help Panel Test")
            ), 
        ]       
        """
    def __init__(self, text, value_dict={}, style=None, *args, **kwargs):
        # make sure text is a string
        if type(text)=='str':
            self.text = text
        else:
            try:
                self.text = str(text)
            except:
                pass
        self.value_dict = value_dict
        self.text = text
        self.style = style
        super().__init__(*args, **kwargs)

    def clone(self):
        return self.__class__(
            text=self.text,
            heading=self.heading,
            #classname=self.classname,
            help_text=self.help_text,
            value_dict = self.value_dict,
            style=self.style,
        )

    class BoundPanel(EditHandler.BoundPanel):

        def get_value(self, field_name):
            # if field_name is a valid name, return data, otherwise return field name unchanged
            try:
                value = getattr(self.instance, field_name)
                if callable(value):
                    value = value()
            except (AttributeError, TypeError) as e:
                value = field_name
            return field_name

        def parse_text(self):
            # loop through the the value dictionary if present, 
            # swap out {{tag}}'s that match key names with the corresponding values
            # keep looping on error
            # return text unchanged if not a string
            try:
                parsed_text = self.panel.text
                for item in self.panel.value_dict:
                    try:
                        parsed_text = parsed_text.replace('{{' + item + '}}', self.get_value(str(self.panel.value_dict[item])))
                    except:
                        pass
                return format_html(parsed_text)
            except TypeError:
                return format_html(self.panel.text)

        def render(self):
            # render the parsed text in a div
            return format_html('<div style="padding-top: 1.2em;">{}</div>', self.parse_text())

        def label(self):
            # add label tag if heading supplied
            if self.panel.heading:
                return format_html('<label>{}{}</label>', self.panel.heading, ':')
            return ''

        def get_style(self):
            # add style if supplied
            if self.panel.style:
                return format_html('style="{}"', self.panel.style)
            return ''

        def render_as_field(self):
            # return assembled HTML
            return format_html(
                '<div class="field" {}>'
                '{}'
                '<div class="field-content">{}</div>'
                '</div>',
                format_html(self.get_style()), self.label(), self.render())  

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

        
## Wagtail 2.x
#        
# class SubMenuFieldPanel(FieldPanel):
#     # Usage: field_name - database field to bind to
#     #        list_queryset - queryset to parse for the dropdown options
#     #                      - amend _get_choice_list() to filter and return list of value/display tuples
#     #        DO NOT add choices to field definition or pass a widget to this panel
#     #
#     # Customised FieldPanel to allow dynamic drop down content based on the parent properties.
#     # Very specific to the SubMenu orderble but could be reworked for a more generic needs.
#     # To repurpose, pass the desired queryset to the list_queryset argument, amend _get_choice_list
#     #
#     # Filters menu choices based on locale and excludes the current menu from the list
#     # Needs revisiting - couldn't find any way to access parent class (Menu) properties from here
#     # in the end, used uri which has parent id (if it has been saved) or locale if it's a new menu
#     # if it has been saved, locale can be derived from the parent id
#     #
#     # Make sure field model does not declare choices - this makes the choices static
#     # Queryset must be passed in as it is the Menu object set. Importing in this module 
#     # causes circular reference.

#     def __init__(self, field_name, list_queryset, *args, **kwargs):
#         self.list_queryset = list_queryset
#         super().__init__(field_name, *args, **kwargs)

#     def clone_kwargs(self):
#         return {
#             'heading': self.heading,
#             'classname': self.classname,
#             'help_text': self.help_text,
#             'list_queryset': self.list_queryset,
#             'field_name': self.field_name,
#         }

#     # Get parent id (if any) and locale id - logic based on uri of form
#     # uri ends with parent id if it is in edit mode, ends in add/?locale=code if it is in add new mode
#     # Fudge to get around lack of access to parent object
#     # Must be called after request is bound
#     # Called from form_bound event via _get_choice_list() here
#     def _get_locale_and_parent(self):
#         path = self.request.get_raw_uri()
#         if path.split('/')[-2] == 'add':
#             locale_id = Locale.objects.get(language_code=path.split('/')[-1].replace('?locale=','')).pk
#             parent_menu_id = None
#         else:
#             parent_menu = self.list_queryset.get(id=int(path.split('/')[-2]))
#             parent_menu_id = getattr(parent_menu, 'id')  
#             locale_id = getattr(parent_menu, 'locale_id')  
#         return parent_menu_id, locale_id

#     # Create a list from the full queryset filtered by locale, exclude parent
#     def _get_choice_list(self):
#         parent_menu_id, locale_id = self._get_locale_and_parent()
#         menu_list = self.list_queryset
#         if locale_id:
#             menu_list = menu_list.filter(locale_id=locale_id)
#         if parent_menu_id:
#             menu_list = menu_list.exclude(id=parent_menu_id)
#         return [('', '------')] + list(menu_list.values_list('id','title'))

#     # declare widget with choices (this event seems to get called twice)
#     # change field type to typed_choice_field otherwise it'll appear as a text field with
#     # dropdown behaviour
#     def on_form_bound(self):
#         self.form.fields[self.field_name].widget = Select(choices=self._get_choice_list())
#         self.form.fields[self.field_name].__class__.__name__ = 'typed_choice_field'
#         super().on_form_bound()
