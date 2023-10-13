from wagtail.admin.panels import Panel
from django.utils.html import format_html
import importlib
from datetime import date, datetime, time

class RichHelpPanel(Panel):
    """ RichHelpPanel Panel Class - built on the ReadOnlyPanel
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
                    value can be retrieved from a nested property or method using ::: for the path separator
                    Note: leave brackets off methods - parameters not supported
                    i.e owner:::get_full_name:::upper retrieves owner.get_fullname().upper()
                    any matched tokens will have an associated string hidden input field with name & id from the {{tag}}
                    e.g. <input type="hidden" name="wordcount" value="1354" id="id_wordcount">
                    value can also be any function path and kwarg function
                    supply as list with first element = 'fn', second element = full path to function, optional third is kwarg dict
                    e.g. value_dict={'rnd': ['fn', 'random.randint', {'a': 1,'b': 9999}]} 
                    this will swap the token {{rnd}} with the result of random.randint(a=1, b=9999)
        style:      optional, any valid style string      
        datetime_format: optional, any valid strftime() formatting string, applied to any datetime objects returned
        """
    def __init__(self, text, value_dict={}, style=None, datetime_format='%c', add_hidden_fields=False, *args, **kwargs):
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
        self.datetime_format = datetime_format
        self.add_hidden_fields = add_hidden_fields
        super().__init__(*args, **kwargs)

    def clone(self):
        return self.__class__(
            text=self.text,
            value_dict = self.value_dict,
            style=self.style,
            datetime_format=self.datetime_format,
            add_hidden_fields=self.add_hidden_fields
        )

    class BoundPanel(Panel.BoundPanel):

        def get_value(self, object, property_list):
            if isinstance(property_list, list) and isinstance(property_list[0], dict):
                if 'module' in property_list[0].keys() and 'method' in property_list[0].keys():
                    parameters = property_list[0].copy()
                    value = self.get_method_value(parameters.pop('module'), parameters.pop('method'), parameters)
                elif 'object' in property_list[0].keys() and 'method' in property_list[0].keys():
                    parameters = property_list[0].copy()
                    obj = parameters.pop('object')
                    prop_list = parameters.pop('method')
                    if not isinstance(prop_list, list):
                        prop_list = [prop_list]
                    value = self.get_object_value(obj, prop_list)
                else:
                    value = self.get_object_value(object, property_list)
                if value and len(property_list) > 1:
                    value = self.get_object_value(value, property_list[1:])
            else:
                value = self.get_object_value(object, property_list)
            return value

        def get_object_value(self, object, property_list):
            kwargs = {}
            args = []
            if not isinstance(property_list, list):
                value = getattr(object, property_list, None) 
            elif isinstance(property_list[0], tuple):
                value = getattr(object, property_list[0][0], None)
                args, kwargs = self.parse_args_and_kwargs(property_list[0][1])
            else:
                value = getattr(object, property_list[0], None)    
            if callable(value):
                value = value(*args, **kwargs)    
            if len(property_list) > 1:
                value = self.get_object_value(value, property_list[1:])
            try:
                if type(value).__name__ in ['date', 'datetime', 'time']:
                    value = value.strftime(self.panel.datetime_format)
            except:
                pass
            return value

        def get_method_value(self, module, method, kwargs={}):
            args, kwargs = self.parse_args_and_kwargs(kwargs)
            # try:
            if not isinstance(kwargs, dict):
                raise TypeError('kwargs must be supplied as a dictionary')
            try:
                mod = importlib.import_module(module)
                func = getattr(mod, method)
            except ModuleNotFoundError:
                # module may not be a package (e.g. builtins.str), try one level up
                package = module.rsplit('.', 1)
                package_mod = importlib.import_module(package[0])
                mod = getattr(package_mod, package[1])
                func = getattr(mod, method)
            if callable(func):
                value = func(*args, **kwargs)
            else:
                value = func
            # except Exception as e:
            #     print(f"{type(e).__name__} at line {e.__traceback__.tb_lineno} of {__file__}: {e}") 
                # str_args = ', '.join(args) if isinstance(args, list) else str(args)
                # str_kwargs = ', '.join([f'{key}={value}' for key, value in kwargs.items()]) if isinstance(kwargs, dict) else str(kwargs)
                # params = f'{str_args}, {str_kwargs}' if str_args and str_kwargs else ((str_args or str_kwargs) or '')
                # value = f"Error evaluating {module}.{method}({params})"
            return value

        def parse_args_and_kwargs(self, kwarg_dict):
            args=[]
            if isinstance(kwarg_dict, dict):
                kwargs = kwarg_dict.copy()
                for item in kwargs:
                    if isinstance(kwargs[item], list):
                        if kwargs[item][0] == 'panel':
                            attr_list = kwargs[item][1:]
                            kwargs[item] = self.get_value(self, attr_list)
                        elif kwargs[item][0] == 'self':
                            attr_list = kwargs[item][1:]
                            kwargs[item][0] = self.get_value(self.instance, attr_list)
                        elif isinstance(kwargs[item][0], dict):
                            if 'module' in kwargs[item][0].keys() and 'method' in kwargs[item][0].keys():
                                kwargs[item][0] = self.get_method_value(
                                    kwargs[item][0].pop('module'), kwargs[item][0].pop('method'), kwargs[item][0]
                                )
                            elif 'object' in kwargs[item][0].keys() and 'method' in kwargs[item][0].keys():
                                obj = kwargs[item].pop('object')
                                prop_list = kwargs[item].pop('method')
                                if not isinstance(prop_list, list):
                                    prop_list = [prop_list]
                                kwargs[item][0] = self.get_object_value(obj, prop_list)
                        if item == 'args':
                            args = [kwargs[item][0]]

                    elif isinstance(kwargs[item], dict):
                        if 'module' in kwargs[item].keys() and 'method' in kwargs[item].keys():
                            kwargs[item] = self.get_method_value(
                                kwargs[item].pop('module'), kwargs[item].pop('method'), kwargs[item]
                            )
                        elif 'object' in kwargs[item].keys() and 'method' in kwargs[item].keys():
                            obj = kwargs[item].pop('object')
                            prop_list = kwargs[item].pop('method')
                            if not isinstance(prop_list, list):
                                prop_list = [prop_list]
                            kwargs[item] = self.get_object_value(obj, prop_list)
                        if item == 'args':
                            args = kwargs[item]

                if 'args' in kwargs:
                    kwargs.pop('args')

                return args, kwargs

            else:
                return [], {}

        def hidden_input(self, hidden_fields):
            # add a hidden input field if selected, field value can be retrieved in form_clean with self.data['field']
            if hidden_fields:
                input = ''
                for item in hidden_fields:
                    input += f'<input type="hidden" name="{item}" value="{hidden_fields[item]}" id="id_{item}">'
                return input
            return ''

        def render_html(self, parent_context):
            return format_html(
                '<div{}>{}</div>', 
                self.get_style(), 
                self.parse_text()
            )

        def parse_text(self):
            # loop through the the value dictionary if present, 
            # swap out {{tag}}'s that match key names with the corresponding values or returning function calls
            # keep looping on error
            # return text unchanged if not a string, or error message for badly formed function call
            # try:
            hidden_fields = {}
            parsed_text = self.panel.text
            for item in self.panel.value_dict:
                # try:
                value_to_parse = self.panel.value_dict[item]
                if not isinstance(value_to_parse, list):
                    value_to_parse = [value_to_parse]
                value = self.get_value(self.instance, value_to_parse)
                parsed_text = parsed_text.replace('{{' + item + '}}', str(value))
                hidden_fields[item] = str(value)
                # except Exception as e:
                #     print(f"{type(e).__name__} at line {e.__traceback__.tb_lineno} of {__file__}: {e}") 
                #     parsed_text = self.panel.text # return the text back unchanged
            return format_html(
                f'{parsed_text} {self.hidden_input(hidden_fields) if self.panel.add_hidden_fields else ""}'
            )
            # except TypeError:
            #     return format_html(self.panel.text)

        def get_style(self):
            # add style if supplied
            if self.panel.style:
                return format_html(' style="{}"', self.panel.style)
            return ''

