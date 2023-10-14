from wagtail.admin.panels import FieldPanel

class RegexPanel(FieldPanel):

    def __init__(self, field_name, pattern, *args, **kwargs):
        self.pattern = pattern
        super().__init__(field_name, *args, **kwargs)

    def clone_kwargs(self):
        kwargs = super().clone_kwargs()
        kwargs.update(
            pattern=self.pattern,
        )
        return kwargs
        
    class BoundPanel(FieldPanel.BoundPanel):
        def __init__(self, **kwargs):
            super().__init__(**kwargs)           
            self.form.fields[self.field_name].__setattr__('pattern', self.panel.pattern)

        field_template_name = "edit_handlers/regex_panel_field.html"
