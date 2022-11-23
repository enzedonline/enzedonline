from allauth.account.forms import LoginForm
from core.blocks import GridStreamBlock
from core.models import SEOPage
from core.utils import purge_blog_list_cache_fragments
from django.utils.translation import gettext_lazy as _
from wagtail.admin.panels import FieldPanel, InlinePanel
from wagtail.fields import StreamField
from wagtail.search import index
from wagtail_localize.synctree import Locale

from .categories import PersonalBlogCategory, TechBlogCategory


class BlogDetailPage(SEOPage):
    subpage_types = []
    parent_page_types = []

    body = StreamField(
        GridStreamBlock(), verbose_name=_("Page body"), blank=True, use_json_field=True
    )

    content_panels = SEOPage.content_panels + [
        FieldPanel('body'),
        # InlinePanel('customcomments', label=_("Comments")),    
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
        siblings = self.__class__.objects.sibling_of(self).live().defer_streamfields()
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

            # siblings = siblings.filter(categories__slug__in=category_filter.split(','))
            filter['qstring'] = '?category=' + category_filter
            
        elif tag_filter:
            siblings = siblings.filter(tags__slug__in=tag_filter.split(','))
            filter['qstring'] = '?tag=' + tag_filter

        context['filter'] = filter

        context['next_post'] = siblings.filter(path__gt=self.path).first()
        context['previous_post'] = siblings.filter(path__lt=self.path).last()

        return context

    def save(self, *args, **kwargs):
        purge_blog_list_cache_fragments()
        super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        purge_blog_list_cache_fragments()
        super().delete(*args, **kwargs)

    def serve(self, request, *args, **kwargs):
        response = super().serve(request, 'blog/blog_page.html')
        response.context_data['login_form'] = LoginForm()
        return response

    def blog_type(self):
        return self.__class__.__name__

