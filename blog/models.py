from core.blocks import GridStreamBlock
from core.models import SEOPage
from django import forms
# from django.core.cache import cache
# from django.core.cache.utils import make_template_fragment_key
from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator
from django.db import models
from django.utils.translation import gettext_lazy as _
from django_extensions.db.fields import AutoSlugField
from modelcluster.contrib.taggit import ClusterTaggableManager
from modelcluster.fields import ParentalManyToManyField
from modelcluster.models import ParentalKey
from taggit.models import Tag, TaggedItemBase
from wagtail.admin.edit_handlers import (FieldPanel, MultiFieldPanel,
                                         StreamFieldPanel)
from wagtail.core.fields import StreamField
from wagtail.core.models import TranslatableMixin
from wagtail.images.edit_handlers import ImageChooserPanel
from wagtail.snippets.models import register_snippet

@register_snippet
class TechBlogCategory(TranslatableMixin, models.Model):
    name = models.CharField(max_length=200)
    slug = AutoSlugField(
        populate_from=['name'],
        verbose_name='slug',
        allow_unicode=True,
        max_length=200,
    )

    panels = [
        FieldPanel('name'),
    ]

    class Meta:
        verbose_name = 'Tech Blog Category'
        verbose_name_plural = 'Tech Blog Categories'
        ordering = ['name']
        unique_together = ('translation_key', 'locale')
    
    def __str__(self):
        return self.name

@register_snippet
class PersonalBlogCategory(TranslatableMixin, models.Model):
    name = models.CharField(max_length=200)
    slug = AutoSlugField(
        populate_from=['name'],
        verbose_name='slug',
        allow_unicode=True,
        max_length=200,
    )

    panels = [
        FieldPanel('name'),
    ]

    class Meta:
        verbose_name = 'Personal Blog Category'
        verbose_name_plural = 'Personal Blog Categories'
        ordering = ['name']
        unique_together = ('translation_key', 'locale')
    
    def __str__(self):
        return self.name

class TechBlogPageTag(TaggedItemBase):
    content_object = ParentalKey(
        'TechBlogDetailPage',
        related_name='tagged_items',
        on_delete=models.CASCADE,
    )

class PersonalBlogPageTag(TaggedItemBase):
    content_object = ParentalKey(
        'PersonalBlogDetailPage',
        related_name='tagged_items',
        on_delete=models.CASCADE,
    )

class BlogDetailPage(SEOPage):
    subpage_types = []

    body = StreamField(
        GridStreamBlock(), verbose_name="Page body", blank=True
    )

    content_panels = SEOPage.content_panels + [
        StreamFieldPanel("body"),
    ]

    class Meta:
        verbose_name = _("Blog Page")
        abstract = True

    # def flush_cache_fragments(self, fragment_keys):
    #     for fragment in fragment_keys:
    #         key = make_template_fragment_key(
    #             fragment,
    #             [self.id],
    #         )
    #         cache.delete(key)

    # def save(self, *args, **kwargs):
    #     self.flush_cache_fragments(["base", "head", "blog_page", "main_menu", "banner_image", "footer"])
    #     return super().save(*args, **kwargs)

class TechBlogDetailPage(BlogDetailPage):
    template = "blog/blog_page.html"
    parent_page_types = ['blog.TechBlogListingPage']

    categories = ParentalManyToManyField(
        'blog.TechBlogCategory',
    )
    tags = ClusterTaggableManager(through=TechBlogPageTag, blank=True)

    content_panels = BlogDetailPage.content_panels + [
        MultiFieldPanel(
            [
                FieldPanel(
                    'categories',
                    widget = forms.CheckboxSelectMultiple,
                ),
            ],
            heading = "Blog Categories",
        ),
        FieldPanel("tags"),
    ]

    class Meta:
        verbose_name = _("Tech Blog Page")

    def get_context(self, request, *args, **kwargs):
        context = super().get_context(request, *args, **kwargs)
        context["blog_url"] = "tech-blog"
        return context

class PersonalBlogDetailPage(BlogDetailPage):
    template = "blog/blog_page.html"
    parent_page_types = ['blog.PersonalBlogListingPage']

    categories = ParentalManyToManyField(
        'blog.PersonalBlogCategory',
    )
    tags = ClusterTaggableManager(through=PersonalBlogPageTag, blank=True)

    content_panels = BlogDetailPage.content_panels + [
        MultiFieldPanel(
            [
                FieldPanel(
                    'categories',
                    widget = forms.CheckboxSelectMultiple,
                ),
            ],
            heading = "Blog Categories",
        ),
        FieldPanel("tags"),
    ]

    class Meta:
        verbose_name = _("Personal Blog Page")

    def get_context(self, request, *args, **kwargs):
        context = super().get_context(request, *args, **kwargs)
        context["blog_url"] = "personal-blog"
        return context

class BlogListingPage(SEOPage):
    parent_page_types = ['home.HomePage']

    banner_image = models.ForeignKey(
        'wagtailimages.Image',
        blank=False,
        null=True,
        related_name='+',
        on_delete=models.SET_NULL,
    )
    banner_headline = models.CharField(
        max_length=30,
        blank=True,
        null=True,
    )
    banner_small_text = models.CharField(
        max_length=60,
        blank=True,
        null=True,
    )

    top_section = StreamField(
        GridStreamBlock(), 
        verbose_name="Content to go above the index", 
        blank=True
    )
    bottom_section = StreamField(
        GridStreamBlock(), 
        verbose_name="Content to go below the index", 
        blank=True
    )

    content_panels = SEOPage.content_panels + [
        MultiFieldPanel(
            [
                ImageChooserPanel('banner_image'),
                FieldPanel('banner_headline'),
                FieldPanel('banner_small_text'),
            ], 
            heading=_("Choose banner image and text/button overlay options.")
        ),
        StreamFieldPanel("top_section"),
        StreamFieldPanel("bottom_section"),
    ]

    class Meta:
        abstract = True

    @property
    def get_child_pages(self):
        return self.get_children().public().live()

    # def flush_cache_fragments(self, fragment_keys):
    #     for fragment in fragment_keys:
    #         key = make_template_fragment_key(
    #             fragment,
    #             [self.id],
    #         )
    #         cache.delete(key)

    # def save(self, *args, **kwargs):
    #     self.flush_cache_fragments(["base", "head", "blog_index_page", "main_menu", "banner_image", "footer"])
    #     return super().save(*args, **kwargs)

class TechBlogListingPage(BlogListingPage):
    template = "blog/blog_index_page.html"
    subpage_types = ["blog.TechBlogDetailPage",]
    max_count = 1

    def get_context(self, request, *args, **kwargs):
        """Adds custom fields to the context"""
        context = super().get_context(request, *args, **kwargs)
        all_posts = TechBlogDetailPage.objects.child_of(self).live().public().reverse()
        
        context['categories'] = TechBlogCategory.objects.all()
        category_filter = request.GET.get("category", None)
        if category_filter:
            all_posts = all_posts.filter(categories__slug__in=category_filter.split(","))

        tag_filter = request.GET.get("tag", None)
        if tag_filter:
            # distinct not supported in sqlite
            # all_posts = all_posts.filter(tags__slug__in=['tag1','tag2']).distinct('id')
            all_posts = all_posts.filter(tags__slug__in=tag_filter.split(','))
            
            verbose_tag_list = ""
            for item in tag_filter.split(','):
                try:
                    verbose_tag_list += "'" + Tag.objects.get(slug=item).name + "' "
                except TechBlogPageTag.DoesNotExist:
                    verbose_tag_list += "'" + item + "' "

        TechBlogPageTag.objects.last()
        paginator = Paginator(all_posts, 8)

        requested_page = request.GET.get("page")

        try:
            posts = paginator.page(requested_page)
        except PageNotAnInteger:
            posts = paginator.page(1)
        except EmptyPage:
            posts = paginator.page(paginator.num_pages)
        
        context['page_range'] = paginator_range(
            requested_page=posts.number,
            last_page_num=paginator.num_pages,
            wing_size=4
        )
        # Next two are needed as Django templates don't support accessing range properties
        context['page_range_first'] = context['page_range'][0]
        context['page_range_last'] = context['page_range'][-1]
        context["posts"] = posts
        context["category_filter"] = category_filter
        context['tag_filter'] = verbose_tag_list
        context["blog_url"] = "tech-blog"

        return context

class PersonalBlogListingPage(BlogListingPage):
    template = "blog/blog_index_page.html"
    subpage_types = ["blog.PersonalBlogDetailPage",]
    max_count = 1

    def get_context(self, request, *args, **kwargs):
        """Adds custom fields to the context"""
        context = super().get_context(request, *args, **kwargs)
        all_posts = PersonalBlogDetailPage.objects.child_of(self).live().public().reverse()
        
        context['categories'] = PersonalBlogCategory.objects.all()
        category_filter = request.GET.get("category", None)
        if category_filter:
            all_posts = all_posts.filter(categories__slug__in=category_filter.split(","))

        paginator = Paginator(all_posts, 8)

        requested_page = request.GET.get("page")

        try:
            posts = paginator.page(requested_page)
        except PageNotAnInteger:
            posts = paginator.page(1)
        except EmptyPage:
            posts = paginator.page(paginator.num_pages)
        
        context['page_range'] = paginator_range(
            requested_page=posts.number,
            last_page_num=paginator.num_pages,
            wing_size=4
        )
        # Next two are needed as Django templates don't support accessing range properties
        context['page_range_first'] = context['page_range'][0]
        context['page_range_last'] = context['page_range'][-1]
        context["posts"] = posts
        context["category_filter"] = category_filter
        context["blog_url"] = "personal-blog"

        return context

def paginator_range(requested_page, last_page_num, wing_size=5):
    """ Given a 'wing size', return a range for pagination. 
        Wing size is the number of pages that flank either side of the selected page
        Presuming missing pages will be denoted by an elipse '...', 
        the minimum width is 2xelipse + 2x wing size + selcted page
        if the elipse is one off the outer limit, replace it with the outer limit
        The range returned will always return a fixed number of boxes to the properly configured pagination nav"""

    # If last page number is within minimum size, just return entire range
    if last_page_num <= ((2 * (wing_size + 1)) + 1):
        return range(1, last_page_num + 1)

    # find the start page or return 1 if within wing range
    start_page = max([requested_page - wing_size, 1])

    if start_page == 1:
        # first elipse is 1, add one to the end and also one for the selected page (also 1 in this case) 
        end_page = (2 * wing_size) + 2
    else:
        # return range end or last page if over that
        end_page = min([requested_page + wing_size, last_page_num])
        if end_page == last_page_num:
            # last elipse is taken by last page number, start is twice the wing plus 1 for the selected page 
            # and 1 for the replaced elipse
            start_page = last_page_num - ((2 * wing_size) + 1)

    # if the ends are within one place of the end points, replace with the actual end point
    # otherwise it's just an elipse where the endpoint would be ... pointless
    if start_page == 2:
        start_page = 1 
    if end_page == last_page_num - 1:
        end_page = last_page_num
    return range(start_page, end_page + 1)

