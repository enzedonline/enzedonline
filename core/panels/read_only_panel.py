from wagtail.admin.panels import Panel
from django.utils.html import format_html
from wagtail.documents.models import Document
from django.db import models
import datetime

class ReadOnlyPanel(Panel):
    """ ReadOnlyPanel: a panel that displays a field in a read-only format.
        Usage:
        fieldname:          name of field to display
        style:              optional, any valid style string
        add_hidden_input:   optional, add a hidden input field to allow retrieving data in form_clean (self.data['field'])
        If the field name is invalid, or an error is received getting the value, empty string is returned.
    """
    def __init__(self, fieldname, style=None, add_hidden_input=False, *args, **kwargs):
        # if fieldname is not string, try to convert it to string
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

    class BoundPanel(Panel.BoundPanel):
        def get_value(self):
            # try to get the value of field, return empty string if failed
            try:
                value = getattr(self.instance, self.panel.fieldname)
                if callable(value):
                    value = value()
            except AttributeError:
                value = ""
            if not value:
                value = "-"
            # evaluate choices correctly
            choices = getattr(
                getattr(type(self.instance), self.panel.fieldname).field,
                "choices",
                None,
            )
            if choices:
                value = [choice[1] for choice in choices if choice[0] == value][0]
            return value
        
        def render_html(self, parent_context):
            # document fields (does not work for custom document model)
            if type(getattr(self.instance, self.panel.fieldname)) == Document:
                return format_html(
                    """
                        <div class="field" {}>
                        {}
                        <div class="field-content">
                        <div id="id_csv_file-chooser" class="chooser document-chooser " data-chooser-url="/admin/documents/chooser/">
                        <a href="{}"> 
                            <div class="chosen">
                                <svg class="icon icon-doc-full-inverse icon" aria-hidden="true" focusable="false"><use href="#icon-doc-full-inverse"></use></svg>
                                
                                    <span class="title">{}</span>
                            </div>
                            </a>
                        </div>
                        </div>
                        {}
                        </div>
                    """,
                    format_html(self.get_style()),
                    self.heading_tag("label"),
                    getattr(self.instance, self.panel.fieldname).file.url,
                    self.render(),
                    self.hidden_input(),
                )
            # render the final output
            return format_html(
                '<div class="field" {}>'
                '{}'
                '<div class="field-content">{}</div>'
                '{}'
                '</div>',
                format_html(self.get_style()), self.heading_tag('label'), self.render(), self.hidden_input())

        def render(self):
            # return formatted field value
            self.value = self.get_value()
            # format types properly
            if type(self.value) == datetime.datetime:
                self.value = self.value.strftime("%d.%m.%Y %H:%M:%S")
            # make text_field pre formated
            if type(getattr(type(self.instance), self.panel.fieldname).field) == models.TextField:
                return format_html(
                    '<div style="padding-top: 1.2em;"><pre>{}</pre></div>', self.value
                )
            return format_html('<div style="padding-top: 1em;">{}</div>', self.value)

        def hidden_input(self):
            # add a hidden input field if selected, field value can be retrieved in form_clean with self.data['field']
            if self.panel.add_hidden_input:
                input = f'<input type="hidden" name="{self.panel.fieldname}" value="{self.value}" id="id_{self.panel.fieldname}">'
                return format_html(input)
            return ''

        def heading_tag(self, tag):
            # read headline from verbose_name
            verbose_name = getattr(type(self.instance), self.panel.fieldname).field.verbose_name
            if not self.heading and verbose_name:
                self.panel.heading = verbose_name
            # add the label/legend tags only if heading supplied
            if self.panel.heading:
                if tag == 'legend':
                    return format_html('<legend class="w-field__label">{}</legend>', self.panel.heading)
                return format_html('<label class="w-field__label">{}{}</label>', self.panel.heading, ':')
            return ''

        def get_style(self):
            # add style if supplied
            if self.panel.style:
                return format_html('style="{}"', self.panel.style)
            return format_html('style="{}"', "padding-bottom: 1em;")
