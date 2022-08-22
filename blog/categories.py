from core.edit_handlers import RegexPanel
from django.core.exceptions import ValidationError
from django.db import models
from django.utils.translation import gettext_lazy as _
from wagtail.admin.forms import WagtailAdminModelForm
from wagtail.admin.panels import FieldPanel
from wagtail.models import TranslatableMixin
from wagtail.snippets.models import register_snippet


class CategoryForm(WagtailAdminModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['name'].widget.attrs['id'] = 'id_title'
        
class CategorySlugField(models.SlugField):
    def validate(self, value, instance, *args, **kwargs):
        super().validate(self, value)
        cat_type = instance.__class__
        found = cat_type.objects.filter(locale=instance.locale.id).filter(slug=instance.slug).exclude(pk=instance.pk)
        if found.count()>0:
            raise ValidationError(_(f"'{instance.slug}' is already in use by '{found.first()}'. Please select a unique slug."))

class BlogCategory(TranslatableMixin, models.Model):
    name = models.CharField(max_length=100, verbose_name=_("Category Name"))
    slug = CategorySlugField(
        max_length=100,
        help_text=_("How the category will appear in URL"),
        # unique=True, <= can't use unique on translatable field
        allow_unicode=True,
    )

    base_form_class = CategoryForm

    panels = [
        FieldPanel("name"),
        RegexPanel(field_name="slug", pattern='^[-\w]+$'),
    ]

    class Meta:
        abstract = True

    def __str__(self):
        return self.name

                     
@register_snippet
class TechBlogCategory(BlogCategory):
    pass

    class Meta:
        verbose_name = _("Tech Blog Category")
        verbose_name_plural = _("Tech Blog Categories")
        ordering = ["name"]
        unique_together = ('translation_key', 'locale'), ('locale', 'slug')

@register_snippet
class PersonalBlogCategory(BlogCategory):
    pass

    class Meta:
        verbose_name = _("Personal Blog Category")
        verbose_name_plural = _("Personal Blog Categories")
        ordering = ["name"]
        unique_together = ('translation_key', 'locale'), ('locale', 'slug')


