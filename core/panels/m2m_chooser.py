from bs4 import BeautifulSoup
from django.conf import settings
from django.core.exceptions import ImproperlyConfigured
from django.forms.models import ModelChoiceIterator, ModelMultipleChoiceField
from django.forms.widgets import SelectMultiple
from django.template.loader import render_to_string
from django.utils.safestring import mark_safe
from django.utils.translation import gettext_lazy as _
from wagtail.admin.panels import FieldPanel


class M2MChooserPanel(FieldPanel):
    """
    FieldPanel with pop-over chooser style form to select items in ParentalManyToManyField.
    """

    def __init__(
            self, 
            field_name, 
            select_button_text=_("Select"),
            clear_button_text=_("Clear Choices"),
            delete_choice_button_text=_("Remove"),
            submit_button_text=_("Submit"),
            search_text=_("Search"),
            cancel_text=_("Close without changes"),
            clear_filter_text=_("Clear filter"),
            filter_no_results_text=_("No matching records found."),
            widget=None, 
            disable_comments=None, 
            permission=None, 
            read_only=False, 
            **kwargs
            ):
        super().__init__(
            field_name=field_name,
            widget=SelectMultiple(),  # override any widget with SelectMultiple
            disable_comments=disable_comments,
            permission=permission,
            read_only=read_only,
            **kwargs
        )
        self.select_button_text = select_button_text
        self.clear_button_text = clear_button_text
        self.delete_choice_button_text = delete_choice_button_text
        self.submit_button_text = submit_button_text
        self.search_text = search_text
        self.cancel_text = cancel_text
        self.clear_filter_text = clear_filter_text
        self.filter_no_results_text = filter_no_results_text

    def clone_kwargs(self):
        kwargs = super().clone_kwargs()
        kwargs.update(
            select_button_text=self.select_button_text,
            clear_button_text=self.clear_button_text,
            delete_choice_button_text=self.delete_choice_button_text,
            submit_button_text=self.submit_button_text,
            search_text=self.search_text,
            cancel_text=self.cancel_text,
            clear_filter_text=self.clear_filter_text,            
            filter_no_results_text=self.filter_no_results_text,
        )
        return kwargs

    def on_model_bound(self):
        """
        Check field is multiple choice field, only in DEBUG mode
        """
        if settings.DEBUG:
            if not isinstance(self.db_field.formfield(), ModelMultipleChoiceField):
                raise ImproperlyConfigured(
                    _("M2MChooser should only be used with ModelMultipleChoiceField (e.g. ParentalManyToManyField)")
                )

    class BoundPanel(FieldPanel.BoundPanel):
        def __init__(self, **kwargs):
            super().__init__(**kwargs)
            self.opts = {
                "field_id": str(self.id_for_label()),
                "heading": self.heading,
                "select_button_text": self.panel.select_button_text,
                "clear_button_text": self.panel.clear_button_text,
                "delete_choice_button_text": self.panel.delete_choice_button_text,
                "submit_button_text": self.panel.submit_button_text,
                "search_text": self.panel.search_text,
                "cancel_text": self.panel.cancel_text,
                "clear_filter_text": self.panel.clear_filter_text,
                "filter_no_results_text": self.panel.filter_no_results_text,
            }
            if settings.USE_I18N:
                self.localise_choices()

        def localise_choices(self):
            """
            Filter choices based on locale_id of instance
            """
            locale_id = getattr(self.instance, 'locale_id', False)
            if locale_id:
                try:
                    form_field = self.form.fields[self.field_name]
                    form_field.queryset = form_field.queryset.filter(locale_id=locale_id)
                    form_field.widget = SelectMultiple(
                        choices=ModelChoiceIterator(form_field)
                    )
                except:
                    pass

        def get_choice_list(self, iterator):
            """
            Convert iterator to list of choices
            """
            choice_list = [{'value': value.value, 'label': label} for value, label in iterator]
            return choice_list

        def get_context_data(self, parent_context=None):
            context = super().get_context_data(parent_context)
            choices = self.get_choice_list(self.bound_field.field.choices)
            context.update(
                {
                    "opts": self.opts,
                    "choices": choices,
                }
            )
            return context

        @mark_safe
        def render_html(self, parent_context=None):
            """
            Add rendered chooser + modal html to wrapper element
            """
            html = super().render_html(parent_context)
            soup = BeautifulSoup(html, "html.parser")
            select = soup.find("select")
            # hide default select element
            select["hidden"] = "true"
            # create uid on wrapper element
            wrapper = soup.find(class_="w-field__wrapper")
            wrapper["class"] = wrapper.get("class", []) + [
                f'm2mchooser-{self.opts["field_id"]}'
            ]
            chooser_html = render_to_string(
                "panels/m2m_chooser.html", 
                self.get_context_data()
            )
            wrapper.append(BeautifulSoup(chooser_html, "html.parser"))
            return str(soup)
