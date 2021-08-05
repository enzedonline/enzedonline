from allauth.account.forms import LoginForm
from core.blocks import GridStreamBlock
from core.models import SEOPage
from core.utils import paginator_range
from django import forms
# from django.core.cache import cache
# from django.core.cache.utils import make_template_fragment_key
from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator
from django.db import models
from django.utils.translation import gettext_lazy as _
from django_comments_xtd.models import XtdComment
from django_extensions.db.fields import AutoSlugField
from modelcluster.contrib.taggit import ClusterTaggableManager
from modelcluster.fields import ParentalManyToManyField
from modelcluster.models import ParentalKey
from taggit.models import Tag, TaggedItemBase
from wagtail.admin.edit_handlers import (FieldPanel, InlinePanel,
                                         MultiFieldPanel, StreamFieldPanel)
from wagtail.core.fields import StreamField
from wagtail.core.models import TranslatableMixin
from wagtail.images.edit_handlers import ImageChooserPanel
from wagtail.search import index
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
    parent_page_types = []

    body = StreamField(
        GridStreamBlock(), verbose_name="Page body", blank=True
    )

    content_panels = SEOPage.content_panels + [
        StreamFieldPanel("body"),
        InlinePanel('customcomments', label=_("Comments")),    
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
        siblings = self.__class__.objects.sibling_of(self).live()
        category_filter = request.GET.get("category", None)
        tag_filter = request.GET.get("tag", None)
        if category_filter:
            siblings = siblings.filter(categories__slug__in=category_filter.split(","))
            context["filter"] = '?category=' + category_filter
            context["showing"] = 'Showing blogs in ' + category_filter + ' category.'
        elif tag_filter:
            siblings = siblings.filter(tags__slug__in=tag_filter.split(','))
            context["filter"] = '?tag=' + tag_filter
            context["showing"] = 'Showing blogs tagged with ' + tag_filter + '.'
        else:
            context["filter"] = ''
            context["showing"] = None
        context["next_post"] = siblings.filter(path__gt=self.path).first()
        context["previous_post"] = siblings.filter(path__lt=self.path).last()

        return context

    def serve(self, request, *args, **kwargs):
        response = super().serve(request, 'blog/blog_page.html')
        response.context_data['login_form'] = LoginForm()
        return response

    def blog_type(self):
        return self.__class__.__name__

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

class CustomComment(XtdComment):
    page = ParentalKey(BlogDetailPage, on_delete=models.CASCADE, related_name='customcomments')

    def save(self, *args, **kwargs):
        if self.user:
            self.user_name = self.user.display_name
        self.page = BlogDetailPage.objects.get(pk=self.object_pk)
        super(CustomComment, self).save(*args, **kwargs)

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

    def get_context(self, request, *args, **kwargs):
        """Adds custom fields to the context"""

        index_type = self.__class__
        context = super().get_context(request, *args, **kwargs)
        
        if index_type == TechBlogListingPage:
            all_posts = TechBlogDetailPage.objects.child_of(self).live().public().reverse()
            categories = TechBlogCategory.objects.all()
            tags = Tag.objects.all().filter(id__in=TechBlogPageTag.objects.all().values_list('tag_id', flat=True))
        else:
            all_posts = PersonalBlogDetailPage.objects.child_of(self).live().public().reverse()
            categories = PersonalBlogCategory.objects.all()
            tags = Tag.objects.all().filter(id__in=PersonalBlogPageTag.objects.all().values_list('tag_id', flat=True))

        category_filter = request.GET.get("category", None)
        tag_filter = request.GET.get("tag", None)

        if category_filter:
            all_posts = all_posts.filter(categories__slug__in=category_filter.split(","))
            context["filter"] = '?category=' + category_filter
            context["showing"] = "Showing blogs in '" + categories.filter(slug=category_filter).first().name + "' category."
        elif tag_filter:
            all_posts = all_posts.filter(tags__slug__in=tag_filter.split(','))
            context["filter"] = '?tag=' + tag_filter
            context["showing"] = "Showing blogs tagged with '#" + tags.filter(slug=tag_filter).first().name + "'"
        else:
            context["filter"] = ''
            context["showing"] = None

        paginator = Paginator(all_posts, 8)

        requested_page = request.GET.get("page")

        try:
            posts = paginator.page(requested_page)
        except PageNotAnInteger:
            posts = paginator.page(1)
        except EmptyPage:
            posts = paginator.page(paginator.num_pages)
        
        context["posts"] = posts
        context['categories'] = categories
        context['tags'] = tags
        context["category_filter"] = category_filter
        context['tag_filter'] = tag_filter
        context['page_range'] = paginator_range(
            requested_page=posts.number,
            last_page_num=paginator.num_pages,
            wing_size=4
        )
        # Next two are needed as Django templates don't support accessing range properties
        context['page_range_first'] = context['page_range'][0]
        context['page_range_last'] = context['page_range'][-1]

        return context

class TechBlogListingPage(BlogListingPage):
    template = "blog/blog_index_page.html"
    subpage_types = ["blog.TechBlogDetailPage",]
    max_count = 1

class PersonalBlogListingPage(BlogListingPage):
    template = "blog/blog_index_page.html"
    subpage_types = ["blog.PersonalBlogDetailPage",]
    max_count = 1


