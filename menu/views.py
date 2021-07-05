from django import urls
from django.conf import settings
from django.http import HttpResponseRedirect
from django.utils import translation
from urllib.parse import urlparse
from wagtail_localize.synctree import Page as LocalizePage, Locale

def set_language_from_url(request, language_code):
    # call url with ?next=<<translated url>> to redirect to translated page
    # if no next url supplied, will attempt to find it from referring url
    # if fails that, will send to home page of the language_code
    # if requested language is not a registered locale, send to home page
    try:
        requested_locale = Locale.objects.get(language_code=language_code)
    except Locale.DoesNotExist:
        return HttpResponseRedirect('/')

    next_url = request.GET.get("next", None)

    # /?next= missing from referring url, attempt to translate
    if not next_url:
        try:
            # get the full path of the referring page;
            previous = request.META['HTTP_REFERER']

            try:
                # split off the path of the previous page
                prev_path = urlparse(previous).path

                # IMPORTANT - ENSURE THE HOME PAGE SLUGS MATCH THEIR LANGUAGE CODE
                # wagtail-localize uses a different root in the actual path for each language in wagtailcore_page
                # (lang1 -> home, lang2 -> home-1, lang3 -> home-3 etc)
                # Matching the slug to lang code means lang1->lang1 etc, the path is valid url_path
                prev_page = LocalizePage.objects.get(url_path=prev_path)

                # Get the url of page in requested language
                # If that doesn't exist, get url of page in default language
                # If the page doesn't exist in the default language, default to home page
                next_page = prev_page.get_translation_or_none(locale=requested_locale)
                if next_page == None:
                    next_page = prev_page.get_translation_or_none(locale=Locale.get_default())
                if next_page != None:
                    next_url = next_page.url
                else:
                    next_url = '/'

            except (LocalizePage.DoesNotExist, Locale.DoesNotExist):
                # previous page is not a LocalizePage, try if previous path can be translated by 
                # changing the language code
                next_url = urls.translate_url(previous, language_code)

                # if no translation is found, translate_url will return the original url
                # in that case, go to the home page in the requested language
                if next_url == previous:
                    next_url = '/' + language_code + '/'

        except KeyError:
            # if for some reason the previous page cannot be found, go to the home page
            next_url = '/' + language_code +'/'

    # activate the language, set the cookie (gets around expiring session cookie issue), redirect to translated page
    translation.activate(language_code)

    response = HttpResponseRedirect(next_url)
    response.set_cookie(settings.LANGUAGE_COOKIE_NAME, language_code, max_age=60*60*24*365)

    return response
