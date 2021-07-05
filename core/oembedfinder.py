from urllib.parse import parse_qs, urlencode, urlparse, urlunparse

from django.core.exceptions import ImproperlyConfigured

from bs4 import BeautifulSoup
from wagtail.embeds.finders.oembed import OEmbedFinder
from wagtail.embeds.oembed_providers import youtube
import requests

class YouTubePreserveRelFinder(OEmbedFinder):
    """ OEmbed finder which preserves the rel=0 parameter on YouTube URLs

    This finder operates on the youtube provider only, and reproduces the
    source URL's rel=0 parameter if present (because YouTube's OEmbed API
    endpoint strips it from the formatted HTML it returns).
    """

    def __init__(self, providers=None, options=None):
        if providers is None:
            providers = [youtube]

        if providers != [youtube]:
            raise ImproperlyConfigured(
                'The YouTubePreserveRelFinder only operates on the youtube provider'
            )
        super().__init__(providers=providers, options=options)

    def find_embed(self, url, max_width=None):
        try:
            embed = super().find_embed(url, max_width)
        except:
            response = requests.get('https://www.youtube.com/oembed/?url=' + url)   
            result = response.json()
            embed = {
                'title': result['title'], 
                'author_name': result['author_name'], 
                'provider_name': result['provider_name'], 
                'type': result['type'], 
                'thumbnail_url': result['thumbnail_url'], 
                'width': result['width'],  
                'height': result['height'], 
                'html': result['html'], 
            }

        rel = parse_qs(urlparse(url).query).get('rel')
        if rel is not None:

            soup = BeautifulSoup(embed['html'], 'html.parser')
            iframe_url = soup.find('iframe').attrs['src']
            scheme, netloc, path, params, query, fragment = urlparse(iframe_url)
            querydict = parse_qs(query)
            if querydict.get('rel') != rel:
                querydict['rel'] = rel
                query = urlencode(querydict, doseq=1)

                iframe_url = urlunparse((scheme, netloc, path, params, query, fragment))
                soup.find('iframe').attrs['src'] = iframe_url
                embed['html'] = str(soup)

        return embed

