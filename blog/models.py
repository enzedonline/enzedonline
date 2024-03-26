from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator
from django.db import models
from django.forms.widgets import CheckboxSelectMultiple
from django.utils.translation import gettext_lazy as _
from modelcluster.contrib.taggit import ClusterTaggableManager
from modelcluster.fields import ParentalManyToManyField
from taggit.models import Tag
from wagtail.admin.panels import FieldPanel, MultiFieldPanel
from wagtail.fields import StreamField
from wagtail.models import Locale

from core.blocks import SimpleStreamBlock
from core.models import SEOPage
from core.utils import paginator_range

from .categories import PersonalBlogCategory, TechBlogCategory
from .detail_page import BlogDetailPage
from .panels import LocalizedSelectPanel
from .tags import PersonalBlogPageTag, TechBlogPageTag


class TechBlogDetailPage(BlogDetailPage):
    template = 'blog/blog_page.html'
    parent_page_types = ['blog.TechBlogListingPage']

    categories = ParentalManyToManyField(
        'blog.TechBlogCategory',
        verbose_name=_("Blog Categories")
    )
    tags = ClusterTaggableManager(through=TechBlogPageTag, blank=True)

    content_panels = BlogDetailPage.content_panels + [
        MultiFieldPanel(
            [
                LocalizedSelectPanel(
                    'categories', 
                    widget=CheckboxSelectMultiple, 
                    ),
            ],
            heading = _("Blog Categories"),
        ),
        FieldPanel('tags'),
    ]

    class Meta:
        verbose_name = _("Tech Blog Page")

class PersonalBlogDetailPage(BlogDetailPage):
    template = 'blog/blog_page.html'
    parent_page_types = ['blog.PersonalBlogListingPage']

    categories = ParentalManyToManyField(
        'blog.PersonalBlogCategory',
        verbose_name=_("Blog Categories")
    )
    tags = ClusterTaggableManager(through=PersonalBlogPageTag, blank=True)

    content_panels = BlogDetailPage.content_panels + [
        MultiFieldPanel(
            [
                FieldPanel(
                    'categories', 
                    widget=CheckboxSelectMultiple, 
                    ),
            ],
            heading = _("Blog Categories"),
        ),
        FieldPanel('tags'),
    ]

    class Meta:
        verbose_name = _("Personal Blog Page")

class BlogListingPage(SEOPage):
    parent_page_types = ['home.HomePage']

    banner_image = models.ForeignKey(
        'wagtailimages.Image',
        blank=False,
        null=True,
        related_name='+',
        on_delete=models.SET_NULL,
        verbose_name=_("Banner Image")
    )
    banner_headline = models.CharField(
        max_length=30,
        blank=True,
        null=True,
        verbose_name=_("Banner Headline")
    )
    banner_small_text = models.CharField(
        max_length=60,
        blank=True,
        null=True,
        verbose_name=_("Banner Small Text")
    )

    top_section = StreamField(
        SimpleStreamBlock(), 
        verbose_name=_("Content to go above the index"), 
        blank=True, 
        use_json_field=True
    )

    content_panels = SEOPage.content_panels + [
        MultiFieldPanel(
            [
                FieldPanel('banner_image'),
                FieldPanel('banner_headline'),
                FieldPanel('banner_small_text'),
            ], 
            heading=_("Choose banner image and text/button overlay options.")
        ),
        FieldPanel('top_section'),
    ]

    class Meta:
        abstract = True

    @property
    def get_child_pages(self):
        return self.get_children().public().live().specific()

    def get_context(self, request, *args, **kwargs):
        """Adds custom fields to the context"""

        context = super().get_context(request, *args, **kwargs)

        active_lang = Locale.get_active()
        default_lang = Locale.get_default()
        
        if type(self).__name__ == 'TechBlogListingPage':
            all_posts = TechBlogDetailPage.objects.filter(locale_id=default_lang.id).live().defer_streamfields().public()
            categories = TechBlogCategory.objects.filter(locale_id=active_lang.id)
            tags = Tag.objects.annotate(ntag=models.Count('blog_techblogpagetag_items')).filter(ntag__gt=0).order_by('name')
        else:
            all_posts = PersonalBlogDetailPage.objects.filter(locale_id=default_lang.id).live().defer_streamfields().public()
            categories = PersonalBlogCategory.objects.filter(locale_id=active_lang.id)
            tags = Tag.objects.annotate(ntag=models.Count('blog_personalblogpagetag_items')).filter(ntag__gt=0).order_by('name')

        category_filter = request.GET.get('category', None)
        tag_filter = request.GET.get('tag', None)

        filter = {'type': '', 'name': '', 'qstring': '', 'verbose': ''}

        if category_filter:
            category_object = categories.filter(slug=category_filter)
            if category_object:
                if active_lang == default_lang:
                    all_posts = all_posts.filter(categories__slug__exact=category_filter)
                else:
                    cat_def_lang = category_object.first().get_translation(locale=default_lang)
                    all_posts = all_posts.filter(categories__slug__exact=cat_def_lang.slug)
                filter['verbose'] = category_object.first().name
            else:
                all_posts = []
                filter['verbose'] = category_filter
            filter['type'] = 'category'
            filter['name'] = category_filter
            filter['qstring'] = '?category=' + category_filter
        elif tag_filter:
            all_posts = all_posts.filter(tags__slug__in=tag_filter.split(','))
            filter['type'] = 'tag'
            filter['name'] = tag_filter
            filter['qstring'] = '?tag=' + tag_filter
            try:
                filter['verbose'] = tags.filter(slug=tag_filter).first().name 
            except AttributeError:
                filter['verbose'] = tag_filter
        else:
            all_posts = all_posts.order_by('-first_published_at')
            
        context['filter'] = filter
        
        paginator = Paginator(all_posts, 12)

        requested_page = request.GET.get('page')

        try:
            posts = paginator.page(requested_page)
        except PageNotAnInteger:
            posts = paginator.page(1)
        except EmptyPage:
            posts = paginator.page(paginator.num_pages)
        
        context['posts'] = posts
        context['categories'] = categories
        context['tags'] = tags
        context['category_filter'] = category_filter
        context['tag_filter'] = tag_filter
        context['page_range'] = paginator_range(
            requested_page=posts.number,
            last_page_num=paginator.num_pages,
            wing_size=4
        )
        # Next two are needed as Django templates don't support accessing range properties
        context['page_range_first'] = context['page_range'][0]
        context['page_range_last'] = context['page_range'][-1]

        # canonical page for non-filtered pages are paginated
        if not (category_filter or tag_filter):
            context['cache_head'] = f'head-page{posts.number}'
        else:
            context['cache_head'] = f'head-page1'

        return context

class TechBlogListingPage(BlogListingPage):
    template = 'blog/blog_index_page.html'
    subpage_types = ['blog.TechBlogDetailPage',]
    max_count = 1

class PersonalBlogListingPage(BlogListingPage):
    template = 'blog/blog_index_page.html'
    subpage_types = ['blog.PersonalBlogDetailPage',]
    max_count = 1
