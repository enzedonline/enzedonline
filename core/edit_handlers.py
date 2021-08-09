from wagtail.admin.edit_handlers import (
    FieldPanel,
)

class RegexPanel(FieldPanel):
    def __init__(self, field_name, pattern, *args, **kwargs):
        self.pattern = pattern
        super().__init__(field_name, *args, **kwargs)

    def clone_kwargs(self):
        kwargs = super().clone_kwargs()
        kwargs.update(
            field_name=self.field_name,
            pattern=self.pattern,
        )
        return kwargs

    field_template = "edit_handlers/regex_panel_field.html"

    def on_form_bound(self):
        self.form.fields[self.field_name].__setattr__('pattern',self.pattern)
        print(self.form.fields[self.field_name].__dir__())
        
        # self.form.fields[self.field_name].__class__.__name__ = 'typed_choice_field'
        super().on_form_bound()