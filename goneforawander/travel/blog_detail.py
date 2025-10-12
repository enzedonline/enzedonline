from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from modelcluster.fields import ParentalManyToManyField
from wagtail.admin.panels import FieldPanel, MultiFieldPanel
from wagtail.fields import StreamField
from wagtail.search import index

from blocks.streamblocks.grid import GridStreamBlock
from core.models import SEOPage
from core.panels import RichHelpPanel, M2MChooserPanel
from core.utils import count_words, get_streamfield_text


class TravelBlogPage(SEOPage):
    og_type = 'article'
    template = 'goneforawander/travel/travelblog-page.html'
    parent_page_types = ['goneforawander.TravelBlogListingPage']
    subpage_types = []

    banner_image = models.ForeignKey(
        'wagtailimages.Image',
        blank=False,
        null=True,
        related_name='+',
        on_delete=models.SET_NULL,
        verbose_name=_("Banner Image")
    )
    banner_headline = "goneforawander"
    banner_small_text = "Hiking, Travel, Photography..."
    banner_image_caption = models.CharField(
        max_length=60,
        blank=True,
        null=True,
    )
    tags = ParentalManyToManyField(
        'goneforawander.TravelBlogTag',
        verbose_name=_("Blog Tags")
    )
    published = models.DateField(default=timezone.now, verbose_name=_("Published Date"))
    location = models.CharField(
        max_length=100,
        blank=True,
        null=True,
    )
    wordcount = models.IntegerField(
        null=True, blank=True, verbose_name="Word Count")
    body = StreamField(
        GridStreamBlock(), verbose_name=_("Page body"), blank=True, use_json_field=True
    )

    content_panels = [
        RichHelpPanel(
            '<b>Word Count:</b> {{wordcount}}', {'wordcount': 'wordcount'},
            classlist='wordcount-banner'
        )
    ] + SEOPage.content_panels + [
        MultiFieldPanel(
            [
                FieldPanel('banner_image'),
                FieldPanel('banner_image_caption'),
            ], 
            heading=_("Choose banner image and text/button overlay options.")
        ),
        M2MChooserPanel('tags'),
        FieldPanel('published'),
        FieldPanel('location'),
        FieldPanel('body'),
    ]

    search_fields = SEOPage.search_fields + [
        index.SearchField('body'),
    ]

    class Meta:
        verbose_name = _("Travel Blog Page")

    def get_absolute_url(self):
        return self.full_url

    def get_context(self, request, *args, **kwargs):
        context = super().get_context(request, *args, **kwargs)
        siblings = self.__class__.objects.sibling_of(self).defer_streamfields().live()

        context['next_post'], context['previous_post'] = self.get_next_prev(
            siblings.order_by('-published')
        )

        return context

    def get_next_prev(self, queryset):
        idx = self.get_queryset_index(queryset)
        return (
            queryset[idx-1] if idx > 0 else None,
            queryset[idx+1] if (idx != -1 and idx <
                                queryset.count()-1) else None
        )

    def get_queryset_index(self, queryset):
        li = list(queryset.values_list('path'))
        try:
            return li.index((self.path,))
        except:
            return -1

    # def save(self, *args, **kwargs):
    #     purge_blog_list_cache_fragments()
    #     super().save(*args, **kwargs)

    # def delete(self, *args, **kwargs):
    #     purge_blog_list_cache_fragments()
    #     super().delete(*args, **kwargs)

    # def blog_type(self):
    #     return self.__class__.__name__

    def corpus(self):
        return get_streamfield_text(
            self.body, strip_tags=["style", "script", "code"]
        )

    def get_wordcount(self, corpus=None):
        if not corpus:
            corpus = self.corpus()
        return count_words(corpus)
