from django import forms
from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator
from django.db import models
from django.db.models import Count, Q
from django.utils.translation import gettext_lazy as _
from modelcluster.fields import ParentalManyToManyField
from wagtail.admin.panels import FieldPanel, MultiFieldPanel, TitleFieldPanel
from wagtail.contrib.routable_page.models import RoutablePageMixin, path, route
from wagtail.fields import RichTextField
from wagtail.search import index
from django.http import JsonResponse

from core.models import SEOPage
from core.panels import M2MChooserPanel
from core.utils import ConstGroup

RTF_DESCRIPTION = ['bold', 'italic', 'link']
RTF_INGREDIENTS = ['h5', 'bold', 'italic', 'ol', 'ul', 'hr']
RTF_INSTRUCTIONS = ['h5', 'bold', 'italic', 'ol', 'ul', 'blockquote', 'hr', 'fa', 'link', 'image', 'embed']

RecipeTagTypes = ConstGroup(
    CUISINE=10,
    CATEGORY=20,
    KEYWORD=30
)

class RecipeTagManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().order_by('tag_type', 'name')

    def in_use(self):
        return self.get_queryset().annotate(ntag=Count('recipepage')).filter(ntag__gt=0)

    def type_in_use(self, tag_type):
        return self.get_queryset().annotate(ntag=Count('recipepage')).filter(ntag__gt=0, tag_type=tag_type)

class RecipeTag(models.Model):
    TAG_TYPE_CHOICES = [
        (RecipeTagTypes.CUISINE, "Cuisine"),
        (RecipeTagTypes.CATEGORY, "Category"),
        (RecipeTagTypes.KEYWORD, "Keyword"),
    ]

    name = models.CharField(max_length=255)
    slug = models.SlugField(
        max_length=100,
        unique=True,
        allow_unicode=True,
    )
    tag_type = models.IntegerField(
        choices=TAG_TYPE_CHOICES, 
        null=True, 
        blank=False,
        default=RecipeTagTypes.KEYWORD
    )

    objects = RecipeTagManager() 

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

class RecipePage(SEOPage):
    template = "recipe/recipe-page.html"
    parent_page_types = ["goneforawander.RecipeListingPage"]
    subpage_types = []

    description = RichTextField(features=RTF_DESCRIPTION, null=True, blank=False, verbose_name=_("Recipe Foreword"))
    prep_time = models.PositiveIntegerField(null=True, blank=False, default=0, verbose_name=_("Preparation Time (minutes)"))
    cook_time = models.PositiveIntegerField(null=True, blank=False, default=0, verbose_name=_("Cooking Time (minutes)"))
    recipe_yield = models.CharField(max_length=100, blank=True, verbose_name=_("Recipe Yield (e.g., '4 servings')"))
    tags = ParentalManyToManyField("goneforawander.RecipeTag", blank=False, verbose_name=_("Recipe Tags"))
    ingredients = RichTextField(features=RTF_INGREDIENTS, verbose_name=_("Ingredients"))
    instructions = RichTextField(features=RTF_INSTRUCTIONS, verbose_name=_("Instructions"))
    
    content_panels = SEOPage.content_panels + [
        FieldPanel("description"),
        FieldPanel("prep_time"),
        FieldPanel("cook_time"),
        FieldPanel("recipe_yield"),
        M2MChooserPanel("tags"),
        FieldPanel("ingredients"),
        FieldPanel("instructions"),
    ]

    search_fields = SEOPage.search_fields + [
        index.SearchField("title", boost=2.0),
        index.SearchField("description"),
        index.SearchField("ingredients", boost=1.5),
        index.SearchField("instructions"),
        index.SearchField("tags_text", boost=2.0),
    ]

    class Meta:
        verbose_name = _("Recipe Page")

    @property
    def tags_text(self) -> str:
        # Make tags searchable and slash-friendly
        names = list(self.tags.values_list("name", flat=True))
        cleaned = []
        for n in names:
            # add both original and a slash-normalized variant
            cleaned.append(n)
            cleaned.append(n.replace("/", " "))
        return " ".join(cleaned)

    def get_tags_queryset(self, tag_type=None):
        qs = RecipeTag.objects.all()
        if tag_type:
            qs = qs.filter(tag_type=tag_type)
        return qs        

    def related_recipes(self, limit=5):
        """
        Return up to `limit` RecipePage objects that share the most tags with this page.
        Excludes self. Ordered by shared tag count (desc) then most recent first.
        """
        tag_ids = list(self.tags.values_list("id", flat=True))
        if not tag_ids:
            return RecipePage.objects.none()

        return (
            RecipePage.objects.live()
            .exclude(pk=self.pk)
            .filter(tags__in=tag_ids)
            .annotate(match_count=Count("tags", filter=Q(tags__in=tag_ids), distinct=True))
            .order_by("-match_count", "-first_published_at")[:limit]
        )
    
    def get_context(self, request, *args, **kwargs):
        context = super().get_context(request, *args, **kwargs)
        context['category_tags'] = list(self.tags.filter(tag_type=RecipeTagTypes.CATEGORY).values_list("name", flat=True))
        context['cuisine_tags'] = list(self.tags.filter(tag_type=RecipeTagTypes.CUISINE).values_list("name", flat=True))
        context['keyword_tags'] = list(self.tags.filter(tag_type=RecipeTagTypes.KEYWORD).values_list("name", flat=True))
        context['related_recipes'] = self.related_recipes()
        if self.prep_time:
            context['prep_time_hours'] = self.prep_time // 60
            context['prep_time_minutes'] = self.prep_time % 60
        if self.cook_time:
            context['cook_time_hours'] = self.cook_time // 60
            context['cook_time_minutes'] = self.cook_time % 60
        if self.prep_time or self.cook_time:
            total_time = (self.prep_time or 0) + (self.cook_time or 0)
            context['total_time_hours'] = total_time // 60
            context['total_time_minutes'] = total_time % 60
        return context

class RecipeListingPage(RoutablePageMixin, SEOPage):
    parent_page_types = ["goneforawander.GFWHomePage"]
    subpage_types = ["goneforawander.RecipePage"]
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

    # A method to return json of queryset - title, image, url, summary, first_published_at
    def to_json(self, qs):
        return [
            {
                "title": recipe.title,
                "summary": recipe.summary,
                "image": recipe.search_image.get_rendition("thumbnail-500x250").url if recipe.search_image else None,
                "first_published_at": recipe.first_published_at.isoformat(),
                "url": recipe.url,
            }
            for recipe in qs
        ]

    def tag_filters(self):
        tags = RecipeTag.objects.in_use()
        tag_dict = {
            "cuisine": tags.filter(tag_type=RecipeTagTypes.CUISINE),
            "category": tags.filter(tag_type=RecipeTagTypes.CATEGORY),
            "keyword": tags.filter(tag_type=RecipeTagTypes.KEYWORD),
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
        verbose_name = _("Recipe Listing Page")

    @path("")
    @path("tags/")
    def recipe_index_page(self, request):
        qs = RecipePage.objects.live().order_by('-first_published_at')
        pagination = self.paginate_qs(qs, request)
        return self.render(
            request,
            context_overrides={
                "recipes": pagination["pages"],
                "tag_filters": self.tag_filters(),
                "page_range": pagination["page_range"],
                "filter_list": None
            },
            template="recipe/recipe-listing-page.html",
        )

    @route(r"^tags/(?P<tags_path>.+)/?$")
    def filter_by_tags(self, request, tags_path):
        tag_list = [t for t in tags_path.strip("/").split("/") if t]
        qs = (
            RecipePage.objects.live()
            .filter(tags__slug__in=tag_list)
            .annotate(match_count=Count('tags', filter=Q(tags__slug__in=tag_list), distinct=True))
            .order_by('-match_count', '-first_published_at')
        )
        pagination = self.paginate_qs(qs, request)
        return self.render(
            request,
            context_overrides={
                "recipes": pagination["pages"],
                "active_tags": tag_list,
                "tag_filters": self.tag_filters(),
                "page_range": pagination["page_range"],
                "filter_list": RecipeTag.dicts_for_slugs(tag_list)
            },
            template="recipe/recipe-listing-page.html",
        )

    @path("search/")
    def search(self, request):
        search_query = request.GET.get("q", None)
        qs = RecipePage.objects.live()
        if search_query:
            qs = qs.search(search_query, order_by_relevance=True)[:30]
        pagination = self.paginate_qs(qs, request)
        return self.render(
            request,
            context_overrides={
                "recipes": pagination["pages"],
                "filter": f'?q={search_query}' if search_query else "",
                "tag_filters": self.tag_filters(),
                "page_range": pagination["page_range"],
                "filter_list": [{"name": search_query, "slug": ""}] if search_query else []
            },
            template="recipe/recipe-listing-page.html",
        )
    
    @path("api/")
    def api_root(self, request):
        qs = RecipePage.objects.live().order_by('-first_published_at')[:30]
        return JsonResponse(self.to_json(qs), safe=False)
    
    @path("api/search/")
    def api_search(self, request):
        search_query = request.GET.get("q", None)
        qs = RecipePage.objects.live()
        if search_query:
            qs = qs.search(search_query, order_by_relevance=True)[:30]
        return JsonResponse(self.to_json(qs), safe=False)
    
    @route(r"^api/tags/(?P<tags_path>.+)/?$")
    def filter_by_tags_api(self, request, tags_path):
        tag_list = [t for t in tags_path.strip("/").split("/") if t]
        qs = (
            RecipePage.objects.live()
            .filter(tags__slug__in=tag_list)
            .annotate(match_count=Count('tags', filter=Q(tags__slug__in=tag_list), distinct=True))
            .order_by('-match_count', '-first_published_at')[:30]
        )
        return JsonResponse(self.to_json(qs), safe=False)