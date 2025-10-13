from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator
from django.db import models
from django.db.models import Count, Q
from django.utils.translation import gettext_lazy as _
from wagtail.admin.panels import FieldPanel, MultiFieldPanel
from wagtail.contrib.routable_page.models import RoutablePageMixin, path, route
from wagtail.fields import RichTextField

from core.models import SEOPage

from .blog_detail import TravelBlogPage
from .tags import TravelBlogTag, TravelBlogTagTypes


class TravelBlogListingPage(RoutablePageMixin, SEOPage):
    parent_page_types = ["goneforawander.GFWHomePage"]
    subpage_types = ["goneforawander.TravelBlogPage"]
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
    banner_image_caption = models.CharField(
        max_length=60,
        blank=True,
        null=True,
    )

    intro = RichTextField(blank=True, verbose_name=_("Introduction"))
    
    content_panels = SEOPage.content_panels + [
        MultiFieldPanel(
            [
                FieldPanel('banner_image'),
                FieldPanel('banner_headline'),
                FieldPanel('banner_small_text'),
                FieldPanel('banner_image_caption'),
            ], 
            heading=_("Choose banner image and text/button overlay options.")
        ),
        FieldPanel("intro"),
    ]

    def tag_filters(self):
        tags = TravelBlogTag.objects.in_use()
        tag_dict = {
            "category": tags.filter(tag_type=TravelBlogTagTypes.CATEGORY),
            "keyword": tags.filter(tag_type=TravelBlogTagTypes.KEYWORD),
        }
        return tag_dict

    def paginate_qs(self, qs, request, per_page=20, param_name="page", on_each_side=2, on_ends=1):
        """
        Paginate a queryset and return a dict with:
          - 'page_obj': the current page object
          - 'page_range': an elided range of page numbers

        param_name: the GET parameter to read the page number from (?p=2)
        on_each_side / on_ends: controls the elision around the current page
        """
        paginator = Paginator(qs, per_page)
        page_number = request.GET.get(param_name)

        try:
            page_obj = paginator.page(page_number)
        except PageNotAnInteger:
            page_obj = paginator.page(1)
        except EmptyPage:
            page_obj = paginator.page(paginator.num_pages)

        page_range = list(paginator.get_elided_page_range(
            page_obj.number,
            on_each_side=on_each_side,
            on_ends=on_ends,
        ))

        return {
            "pages": page_obj,
            "page_range": page_range,
        }

    class Meta:
        verbose_name = _("Travel Blog Listing Page")

    @path("")
    @path("tags/")
    def travel_blog_index_page(self, request):
        qs = TravelBlogPage.objects.live().order_by('-published', '-first_published_at')
        pagination = self.paginate_qs(qs, request)
        return self.render(
            request,
            context_overrides={
                "travelblogs": pagination["pages"],
                "tag_filters": self.tag_filters(),
                "page_range": pagination["page_range"],
                "filter_list": None
            },
            template="goneforawander/travel/travelblog-listing-page.html",
        )
    @route(r"^tags/(?P<tags_path>.+)/?$")
    def filter_by_tags(self, request, tags_path):
        tag_list = [t for t in tags_path.strip("/").split("/") if t]
        qs = (
            TravelBlogPage.objects.live()
            .filter(tags__slug__in=tag_list)
            .annotate(match_count=Count('tags', filter=Q(tags__slug__in=tag_list), distinct=True))
            .order_by('-match_count', '-published', '-first_published_at')
        )
        pagination = self.paginate_qs(qs, request)
        return self.render(
            request,
            context_overrides={
                "travelblogs": pagination["pages"],
                "active_tags": tag_list,
                "tag_filters": self.tag_filters(),
                "page_range": pagination["page_range"],
                "filter_list": TravelBlogTag.dicts_for_slugs(tag_list)
            },
            template="goneforawander/travel/travelblog-listing-page.html",
        )

    @path("search/")
    def search(self, request):
        search_query = request.GET.get("q", None)
        qs = TravelBlogPage.objects.live()
        if search_query:
            qs = qs.search(search_query, order_by_relevance=True)
        pagination = self.paginate_qs(qs, request)
        return self.render(
            request,
            context_overrides={
                "travelblogs": pagination["pages"],
                "filter": f'?q={search_query}' if search_query else "",
                "tag_filters": self.tag_filters(),
                "page_range": pagination["page_range"],
                "filter_list": [{"name": search_query, "slug": ""}] if search_query else []
            },
            template="goneforawander/travel/travelblog-listing-page.html",
        )
    