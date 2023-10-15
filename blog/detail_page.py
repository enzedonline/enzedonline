from django.db import models
from django.utils.translation import gettext_lazy as _
from wagtail.admin.panels import FieldPanel, InlinePanel
from wagtail.fields import StreamField
from wagtail.models import Locale
from wagtail.search import index

from core.blocks import GridStreamBlock
from core.models import SEOPage
from core.panels import RichHelpPanel
from core.utils import (count_words, get_streamfield_text,
                        purge_blog_list_cache_fragments)

from .categories import PersonalBlogCategory, TechBlogCategory


class BlogDetailPage(SEOPage):
    subpage_types = []
    parent_page_types = []

    wordcount = models.IntegerField(null=True, blank=True, verbose_name="Word Count")
    body = StreamField(
        GridStreamBlock(), verbose_name=_("Page body"), blank=True, use_json_field=True
    )

    content_panels = [
        RichHelpPanel(
            '<b>Word Count:</b> {{wordcount}}', {'wordcount': 'wordcount'},
            classlist = 'wordcount-banner'
        )
        ] + SEOPage.content_panels + [
        FieldPanel('body'),
        ]

    search_fields = SEOPage.search_fields + [
        index.SearchField('body'),
    ]

    class Meta:
        verbose_name = _("Blog Page")
        # abstract = True

    def get_absolute_url(self):
        return self.get_url()

    def get_context(self, request, *args, **kwargs):
        context = super().get_context(request, *args, **kwargs)

        active_lang = Locale.get_active()
        default_lang = Locale.get_default()
        siblings = self.__class__.objects.sibling_of(self).defer_streamfields().live()
        category_filter = request.GET.get('category', None)
        tag_filter = request.GET.get('tag', None)
        
        filter = {'qstring': ''}

        if category_filter:
            if type(self).__name__ == 'TechBlogDetailPage':
                categories = TechBlogCategory.objects.filter(locale_id=active_lang.id)
            else:
                categories = PersonalBlogCategory.objects.filter(locale_id=active_lang.id)
            category_object = categories.filter(slug=category_filter)

            if category_object:
                if active_lang == default_lang:
                    siblings = siblings.filter(categories__slug__exact=category_filter)
                else:
                    cat_def_lang = category_object.first().get_translation(locale=default_lang)
                    siblings = siblings.filter(categories__slug__exact=cat_def_lang.slug)

            filter['qstring'] = '?category=' + category_filter
            
        elif tag_filter:
            siblings = siblings.filter(tags__slug__in=tag_filter.split(','))
            filter['qstring'] = '?tag=' + tag_filter

        context['filter'] = filter

        context['next_post'], context['previous_post'] = self.get_next_prev(siblings.order_by('-first_published_at'))

        return context

    def get_next_prev(self, queryset):
        idx = self.get_queryset_index(queryset)
        return (
            queryset[idx-1] if idx > 0 else None,
            queryset[idx+1] if (idx != -1 and idx < queryset.count()-1) else None
        )

    def get_queryset_index(self, queryset):
        li = list(queryset.values_list('path'))
        try:
            return li.index((self.path,))
        except:
            return -1

    def save(self, *args, **kwargs):
        purge_blog_list_cache_fragments()
        super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        purge_blog_list_cache_fragments()
        super().delete(*args, **kwargs)

    def blog_type(self):
        return self.__class__.__name__

    def corpus(self):
        return get_streamfield_text(
            self.body, strip_tags=["style", "script", "code"]
        )

    def get_wordcount(self, corpus=None):
        if not corpus:
            corpus = self.corpus()
        return count_words(corpus)