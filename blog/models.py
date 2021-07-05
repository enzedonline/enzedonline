from core.blocks import GridStreamBlock
from core.models import SEOPage
# from django.core.cache import cache
# from django.core.cache.utils import make_template_fragment_key
from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator
from django.db import models
from django.utils.translation import gettext_lazy as _
from wagtail.admin.edit_handlers import (FieldPanel, MultiFieldPanel,
                                         StreamFieldPanel)
from wagtail.core.fields import StreamField
from wagtail.images.edit_handlers import ImageChooserPanel

class BlogDetailPage(SEOPage):
    template = "blog/blog_page.html"
    subpage_types = []
    parent_page_types = ['blog.BlogListingPage']

    body = StreamField(
        GridStreamBlock(), verbose_name="Page body", blank=True
    )

    content_panels = SEOPage.content_panels + [
        StreamFieldPanel("body"),
    ]

    class Meta:
        verbose_name = _("Blog Page")

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


class BlogListingPage(SEOPage):
    template = "blog/blog_index_page.html"
    parent_page_types = ['home.HomePage']
    subpage_types = [
        "blog.BlogDetailPage", 
    ]
    max_count = 1

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

    @property
    def get_child_pages(self):
        return self.get_children().public().live()

    def get_context(self, request, *args, **kwargs):
        """Adds custom fields to the context"""
        context = super().get_context(request, *args, **kwargs)
        # all_posts = self.get_children().public().live().order_by('-first_published_at')
        all_posts = BlogDetailPage.objects.child_of(self).live().public().reverse()
        
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

        return context

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

