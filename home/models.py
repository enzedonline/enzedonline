from core.blocks import GridStreamBlock
from core.models import SEOPage
# from django.core.cache import cache
# from django.core.cache.utils import make_template_fragment_key
from django.db import models
from django.utils.translation import gettext_lazy as _
from wagtail.admin.edit_handlers import (FieldPanel, MultiFieldPanel,
                                         StreamFieldPanel)
from wagtail.core.fields import StreamField
from wagtail.images.edit_handlers import ImageChooserPanel

class HomePage(SEOPage):

    template = 'home/home_page.html'
    subpage_types = [
        "service.ServicePage", 
        "contact.ContactPage", 
        "blog.PersonalBlogListingPage",
        "blog.TechBlogListingPage",
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

    body = StreamField(
        GridStreamBlock(), verbose_name="Page body", blank=True
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
        StreamFieldPanel("body"),
    ]

    class Meta:
        verbose_name = "Home Page"

    def get_sitemap_urls(self, request):
        sitemap = super().get_sitemap_urls(request)

        for locale_home in self.get_siblings(inclusive=False).live():
            for entry in locale_home.get_sitemap_urls(request):
                sitemap.append(entry)
            for child_page in locale_home.get_descendants().live():
                for entry in child_page.get_sitemap_urls(request):
                    sitemap.append(entry)
        return sitemap        

    # def flush_cache_fragments(self, fragment_keys):
    #     for fragment in fragment_keys:
    #         key = make_template_fragment_key(
    #             fragment,
    #             [self.id],
    #         )
    #         cache.delete(key)

    # def save(self, *args, **kwargs):
    #     self.flush_cache_fragments(["base", "head", "home_page", "main_menu", "banner_image", "footer"])
    #     return super().save(*args, **kwargs)

