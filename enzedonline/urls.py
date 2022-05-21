from core.views import RobotsView
from search.views import enzed_search
from django.conf import settings
from django.urls import re_path
from django.conf.urls.i18n import i18n_patterns
from django.contrib import admin
from django.urls import include, path
from django.views import defaults as default_views
from django.views.i18n import JavaScriptCatalog
# from search import views as search_views
from core.views import refresh_page_cache
from userauth.views import *
from wagtail.admin import urls as wagtailadmin_urls
from wagtail.contrib.sitemaps.views import sitemap
from wagtail import urls as wagtail_urls
from wagtail.documents import urls as wagtaildocs_urls
from wagtail.models import Locale
from django.views.generic import RedirectView

lang = Locale.get_active().language_code

def trigger_error(request):
    division_by_zero = 1 / 0

urlpatterns = [
    path('django-admin/', admin.site.urls),
    path('admin/', include(wagtailadmin_urls)),
    path('documents/', include(wagtaildocs_urls)),
    re_path(r'^robots\.txt$', RobotsView.as_view(), name='robots'),
    re_path(r'^sitemap.xml$', sitemap),
    re_path(r'^comments/', include('django_comments_xtd.urls')),
    path('sentry-debug/', trigger_error),
    path(r'jsi18n/', JavaScriptCatalog.as_view(), name='javascript-catalog'),
    re_path(r'^accounts/password/success/', RedirectView.as_view(pattern_name='password_change_success', permanent=False)),
    re_path(r'^accounts/password/reset/done/', RedirectView.as_view(pattern_name='password_change_success', permanent=False)),
    re_path(r'^accounts/profile/', RedirectView.as_view(pattern_name='account_profile', permanent=False)),
    path('', RedirectView.as_view(url='/' + lang +'/', permanent=False)),
    # Language Switcher
    # path('lang/<str:language_code>/', set_language_from_url, name='set_language_from_url'),
]

if settings.DEBUG:
    from django.conf.urls.static import static
    from django.contrib.staticfiles.urls import staticfiles_urlpatterns

    # Serve static and media files from development server
    urlpatterns += staticfiles_urlpatterns()
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

# These paths are translatable so will be given a language prefix (eg, '/en', '/fr')
urlpatterns = urlpatterns + i18n_patterns(
    re_path(r'^accounts/password/success/', password_change_success, name="password_change_success"),
    re_path(r'^accounts/password/change/', CustomPasswordChangeView.as_view(), name="account_change_password"),
    re_path(r'^accounts/password/set/', CustomPasswordSetView.as_view(), name="account_set_password"),
    re_path(r'^accounts/profile/', profile_view, name='account_profile'),
    path('search/', enzed_search, name='search'),
    re_path(r'^403/$', default_views.permission_denied, kwargs={'exception': Exception("Permission Denied")}),
    re_path(r'^404/$', default_views.page_not_found, kwargs={'exception': Exception("Page not Found")}),
    re_path(r'^500/$', default_views.server_error),    # For anything not caught by a more specific rule above, hand over to
    # Creates urls like yourwebsite.com/login/
    re_path(r'', include('allauth.urls')),
    # Creates urls like yourwebsite.com/accounts/login/
    re_path(r'^accounts/', include('allauth.urls')),

    path('accounts/<slug:url>/update/', CustomUserUpdateView.as_view(template_name='account/update.html'), name='account_update'),
    path('accounts/<slug:url>/delete/', CustomUserDeleteView.as_view(template_name='account/delete.html'), name='account_delete'),
    path('accounts/deleted/', delete_success, name='delete_success'),

    path('clear-cache', refresh_page_cache, name="refresh-page-cache"),

    # Wagtail's page serving mechanism. This should be the last pattern in
    # the list:
    path("", include(wagtail_urls)),

    # Alternatively, if you want Wagtail pages to be served from a subpath
    # of your site, rather than the site root:
    #    path("pages/", include(wagtail_urls)),
)

