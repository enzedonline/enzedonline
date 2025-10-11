from django import forms
from django.db import models
from django.db.models import Count
from django.utils.translation import gettext_lazy as _
from wagtail.admin.panels import FieldPanel, TitleFieldPanel
from wagtail.snippets.models import register_snippet

from core.utils import ConstGroup

TravelBlogTagTypes = ConstGroup(
    CATEGORY=20,
    KEYWORD=30
)

class TravelBlogTagManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().order_by('tag_type', 'name')

    def in_use(self):
        return self.get_queryset().annotate(ntag=Count('travelblogpage')).filter(ntag__gt=0)

    def type_in_use(self, tag_type):
        return self.get_queryset().annotate(ntag=Count('travelblogpage')).filter(ntag__gt=0, tag_type=tag_type)


@register_snippet
class TravelBlogTag(models.Model):
    icon = "backpack"
    
    TAG_TYPE_CHOICES = [
        (TravelBlogTagTypes.CATEGORY, "Category"),
        (TravelBlogTagTypes.KEYWORD, "Keyword"),
    ]
    name = models.CharField(max_length=100, verbose_name=_("Tag Name"))
    slug = models.SlugField(
        max_length=100,
        help_text=_("How the tag will appear in URL"),
        unique=True,
        allow_unicode=True,
    )
    tag_type = models.IntegerField(
        choices=TAG_TYPE_CHOICES, 
        null=True, 
        blank=False,
        default=TravelBlogTagTypes.KEYWORD
    )

    objects = TravelBlogTagManager()

    class Meta:
        verbose_name = _("Travel Blog Tag")
        verbose_name_plural = _("Travel Blog Tags")
        ordering = ["name"]

    def __str__(self):
        return self.name

    @classmethod
    def dicts_for_slugs(cls, slugs):
        """
        Given an iterable of slugs, return a list of dicts: [{slug, name}],
        preserving input order and skipping unknown slugs.
        """
        if not slugs:
            return []
        seen, ordered = set(), []
        for s in slugs:
            if s and s not in seen:
                seen.add(s)
                ordered.append(s)

        rows = cls.objects.filter(slug__in=ordered).values_list("slug", "name")
        name_by_slug = {slug: name for slug, name in rows}
        return [{"slug": s, "name": name_by_slug[s]} for s in ordered if s in name_by_slug]

    panels = [
        TitleFieldPanel("name"),
        FieldPanel("slug"),
        FieldPanel("tag_type", widget=forms.RadioSelect),
    ]