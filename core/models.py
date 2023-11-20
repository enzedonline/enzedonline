from datetime import datetime

from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models
from django.forms.utils import ErrorList
from django.utils.translation import gettext_lazy as _
from wagtail.admin.panels import FieldPanel, MultiFieldPanel
from wagtail.models import Locale, Page
from wagtail.search import index
from wagtailmetadata.models import WagtailImageMetadataMixin


def get_image_model_string():
    try:
        image_model = settings.WAGTAILIMAGES_IMAGE_MODEL
    except AttributeError:
        image_model = 'wagtailimages.Image'
    return image_model

class SEOPageMixin(index.Indexed, WagtailImageMetadataMixin, models.Model):
    search_image = models.ForeignKey(
        get_image_model_string(),
        null=True,
        blank=False,
        related_name='+',
        on_delete=models.SET_NULL,
        verbose_name=_('Search Image'),
        help_text=_("The image to use on previews of this page on external links and search results. \
                     This will also be the image used for blog posts on the index pages.")
    )

    summary = models.TextField(
        null=False,
        blank=False,
        help_text=_("A summary of the page to be used on index pages and on-site searching.")
    )

    search_engine_index = models.BooleanField(
        blank=False,
        null=False,
        default=True,
        verbose_name=_("Allow search engines to index this page?")
    )

    search_engine_changefreq = models.CharField(
        max_length=25,
        choices=[
            ("always", _("Always")),
            ("hourly", _("Hourly")),
            ("daily", _("Daily")),
            ("weekly", _("Weekly")),
            ("monthly", _("Monthly")),
            ("yearly", _("Yearly")),
            ("never", _("Never")),
        ],
        blank=True,
        null=True,
        verbose_name=_("Search Engine Change Frequency (Optional)"),
        help_text=_("How frequently the page is likely to change? (Leave blank for default)")
    )

    search_engine_priority = models.DecimalField(
        max_digits=2, 
        decimal_places=1,
        blank=True,
        null=True,
        verbose_name=_("Search Engine Priority (Optional)"),
        help_text=_("The priority of this URL relative to other URLs on your site. Valid values range from 0.0 to 1.0. (Leave blank for default)")
    )

    content_panels = Page.content_panels + [
        FieldPanel('summary'),
    ]
    
    promote_panels = [
        MultiFieldPanel([
            FieldPanel('slug'),
            FieldPanel('search_image'),
            FieldPanel('seo_title'),
            FieldPanel('search_description'),
        ], _('SEO Page Configuration')),
        MultiFieldPanel([
            FieldPanel('search_engine_index'),
            FieldPanel('search_engine_changefreq'),
            FieldPanel('search_engine_priority'),
        ], _("Search Engine Indexing")),
    ]

    def get_meta_url(self):
        return self.full_url

    def get_meta_title(self):
        return self.seo_title or self.title

    def get_meta_description(self):
        return self.search_description or self.summary

    def get_meta_image(self):
        return self.search_image

    def get_alternates(self):
        default_locale = Locale.get_default()
        x_default = None

        trans_pages = self.get_translations(inclusive=True)
        if trans_pages.count() > 1:
            alt = []
            for page in trans_pages:
                alt.append({
                    'lang_code': page.locale.language_code,
                    'location': page.get_full_url()
                })
                if page.locale == default_locale:
                    x_default = page.get_url_parts()
            # page not translated to default language, use first trans_page instead
            if not x_default:
                x_default = trans_pages.first().get_url_parts()
            # x-default - strip the language component from the url for the default-lang page
            # https://example.com/en/something/ -> https://example.com/something/
            x_default = f"{x_default[1]}/{'/'.join(x_default[2].split('/')[2:])}"
            alt.append({'lang_code': 'x-default', 'location': x_default})
            return alt
        else:
            return None

    @property
    def lastmod(self):
        return self.last_published_at or self.latest_revision_created_at

    def get_sitemap_urls(self):
        if self.search_engine_index:
            url_item = {
                "location": self.full_url,
                "lastmod": self.lastmod,
                "alternates": self.get_alternates()
            }
            if self.search_engine_changefreq:
                url_item["changefreq"] = self.search_engine_changefreq
            if self.search_engine_priority:
                url_item["priority"] = self.search_engine_priority
            return url_item
        else:
            return []

    class Meta:
        abstract = True

    def clean(self):
        super().clean()
        errors = {}
        len_search_description = len(self.search_description or self.summary)
        if len_search_description < 50 or len_search_description > 160:
            if len_search_description==0:
                msg = _("empty")
            else:
                msg = _(f"{len_search_description} character{'s' * bool(len_search_description>1)}")
            if self.search_description:
                errors['search_description'] = ErrorList([_(f'Meta Description is {msg}. It should be between 50 and 160 characters for optimum SEO.')])
            else:
                errors['search_description'] = ErrorList([_(f'Summary is {msg}. Create a meta description between 50 and 160 characters for optimum SEO.')])

        len_search_title = len(self.seo_title or self.title)
        if len_search_title < 15 or len_search_title > 70:
            if len_search_title==0:
                msg = _("empty")
            else:
                msg = _(f"{len_search_title} character{'s' * bool(len_search_title>1)}")
            if self.seo_title:
                errors['seo_title'] = ErrorList([_(f'Title tag is {msg}. It should be between 15 and 70 characters for optimum SEO.')])
            else:
                errors['seo_title'] = ErrorList([_(f'Page title is {msg}. Create a title tag between 15 and 70 characters for optimum SEO.')])

        if errors:
            raise ValidationError(errors)


class SEOPage(SEOPageMixin, Page):

    search_fields = Page.search_fields + [
        index.SearchField('summary'),
    ]

    class Meta:
        abstract = True

    def get_context(self, request, *args, **kwargs):
        context = super().get_context(request, *args, **kwargs)
        try: # WSGI request has no is_preview - thrown on contact page
            preview = request.is_preview
        except:
            preview = False

        if preview or settings.DEBUG:
            context['cache_name'] = 'preview'
            context['cache_date'] = datetime.now()
        else:
            context['cache_name'] = self.slug
            context['cache_date'] = self.last_published_at
        return context
