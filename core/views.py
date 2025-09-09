import html
from urllib.parse import urlparse, urlsplit

import requests
import validators
from bs4 import BeautifulSoup
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import redirect
from django.template.response import TemplateResponse
from django.utils.http import http_date
from django.utils.translation import gettext_lazy as _
from django.views import View
from django.views.generic import TemplateView
from wagtail.models import Site

from .utils import clear_page_cache


class ExternalContentProxy(View):
    def get(self, request):
        url = request.GET.get("url", "")  # Get the URL parameter from the query string

        if not url:
            return JsonResponse({"error": "Missing URL parameter"})

        # Validate the URL format
        if not urlsplit(url).scheme: url = f'https://{url}'
        if not validators.url(url):
            return JsonResponse({"error": "Invalid URL format"})

        try:
            response = requests.get(url)

            # update url with resolved address
            url = response.url

            # Find the start and end positions of the <head> tag
            content = response.text
            head_start = content.find("<head")
            head_end = content.find("</head>", head_start) + len("</head>")

            if head_start == -1 or head_end == -1:
                return JsonResponse({"error": "No <head> tag found"})

            # Extract and parse the <head> content using BeautifulSoup
            head_content = content[head_start:head_end]
            head_soup = BeautifulSoup(head_content, "html.parser")

            title = self.extract_metadata(
                head_soup,
                [
                    "og:title",
                    "itemprop:name",
                    "twitter:title",
                ],
            )

            description = self.extract_metadata(
                head_soup,
                [
                    "og:description",
                    "itemprop:description",
                    "twitter:description",
                    'meta[name="description"]',
                ],
            )
            if description:
                description = html.unescape(description)

            image = (
                self.extract_metadata(
                    head_soup,
                    [
                        "og:image",
                        "itemprop:image",
                        "twitter:image",
                    ],
                )
                or ""
            )

            # attempt to fix relative image url
            if image and image.startswith("/"):
                parsed_url = urlparse(url)
                image = f"{parsed_url.scheme}://{parsed_url.netloc}{image}"

            metadata = {
                "url": url,
                "title": title,
                "description": description,
                "image": image,
            }

            return JsonResponse(metadata)

        except requests.exceptions.ConnectionError as e:
            if "getaddrinfo failed" in str(e):
                return JsonResponse({"error": f"Failed to resolve {url}."})
            return JsonResponse({"error": str(e)})
        except Exception as e:
            return JsonResponse({"error": str(e)})

    def extract_metadata(self, soup, keys):
        for key in keys:
            meta_tag = soup.find("meta", attrs={"property": key})
            if not meta_tag:
                meta_tag = soup.find("meta", attrs={"itemprop": key})
            if not meta_tag:
                meta_tag = soup.find("meta", attrs={"name": key})
            if meta_tag:
                if keys[0] == "og:title" and not meta_tag["content"]:
                    title_tag = soup.find("title")
                    if title_tag:
                        return title_tag.string
                return meta_tag["content"]

        if keys[0] == 'meta[name="description"]':
            description_tag = soup.find("meta", attrs={"name": "description"})
            if description_tag:
                return description_tag["content"]

        if keys[0] == "og:title":
            title_tag = soup.find("title")
            if title_tag:
                return title_tag.string

        return None


def check_image_url(request):
    image_url = request.GET.get("url")

    if not image_url:
        return JsonResponse({"valid": False})

    try:
        response = requests.head(image_url)
        if response.status_code == 200 and response.headers.get(
            "Content-Type", ""
        ).startswith("image/"):
            return JsonResponse({"valid": True})
        else:
            return JsonResponse({"valid": False})
    except requests.RequestException:
        return JsonResponse({"valid": False})


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
            if getattr(child_page, 'search_engine_index', True) is False:
                continue
            entry = child_page.get_sitemap_urls()
            if isinstance(entry, list):
                urlset.extend(entry)
            else:
                urlset.append(entry)
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
