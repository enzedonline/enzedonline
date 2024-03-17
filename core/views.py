from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect
from django.template.response import TemplateResponse
from django.utils.http import http_date
from django.utils.translation import gettext_lazy as _
from django.views.generic import TemplateView
from wagtail.models import Page, Site

from .utils import clear_page_cache


@login_required()
def refresh_page_cache(r):
    try:
        clear_page_cache()
        messages.success(r, _('Page Cache has been refreshed!'))
    except:
        messages.error(r, _('There was a problem refreshing the Page Cache'))
    return redirect(r.META['HTTP_REFERER'])


class RobotsView(TemplateView):
    content_type = 'text/plain'

    def get_template_names(self):
        return 'robots.txt'


def sitemap(request):
    site = Site.find_for_request(request)
    urlset = []
    for locale_home in site.root_page.get_translations(inclusive=True).defer_streamfields():
        for child_page in locale_home.get_descendants(inclusive=True).defer_streamfields().live().public().specific():
            urlset.append(child_page.get_sitemap_urls())
    try:
        urlset.remove([])
    except:
        pass
    last_modified = max([x['lastmod'] for x in urlset])

    return TemplateResponse(
        request,
        template='sitemap.xml',
        context={'urlset': urlset},
        content_type='application/xml',
        headers={
            "X-Robots-Tag": "noindex, noodp, noarchive",
            "last-modified": http_date(last_modified.timestamp()),
            "vary": "Accept-Encoding",
        }
    )
