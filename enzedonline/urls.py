from django.conf import settings
from django.conf.urls.i18n import i18n_patterns
from django.contrib import admin
from django.http import HttpResponsePermanentRedirect
from django.urls import include, path, re_path
from django.views import defaults as default_views
from django.views.i18n import JavaScriptCatalog
from wagtail import urls as wagtail_urls
from wagtail.admin import urls as wagtailadmin_urls
from wagtail.documents import urls as wagtaildocs_urls

from core.views import (ExternalContentProxy, RobotsView, check_image_url,
                        refresh_page_cache, sitemap)
from search.views import enzed_search
from userauth.views import (CustomPasswordChangeView, CustomPasswordSetView,
                            CustomUserDeleteView, CustomUserUpdateView,
                            delete_success, password_change_success,
                            profile_view)

from .views import error_429_view


def trigger_error(request):
    division_by_zero = 1 / 0

urlpatterns = [
    path('django-admin/', admin.site.urls),
    path('admin/', include(wagtailadmin_urls)),
    path('documents/', include(wagtaildocs_urls)),
    re_path(r'^robots\.txt$', RobotsView.as_view(), name='robots'),
    re_path(r'^sitemap.xml$', sitemap, name='sitemap'),
    re_path(r'^comments/', include('django_comments_xtd.urls')),
    path('sentry-debug/', trigger_error),
    path(r'jsi18n/', JavaScriptCatalog.as_view(), name='javascript-catalog'),
    re_path(r'^en/accounts/linkedin_oauth2/login/$', lambda x: HttpResponsePermanentRedirect('/accounts/oidc_linkedin/login/')),
    path('external-content-proxy/', ExternalContentProxy.as_view(), name='external-content-proxy'),
    path('check-image-url/', check_image_url, name='check_image_url'),
]

if settings.DEBUG:
    from django.conf.urls.static import static
    from django.contrib.staticfiles.urls import staticfiles_urlpatterns

    # Serve static and media files from development server
    urlpatterns += staticfiles_urlpatterns()
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
       
    urlpatterns += [
        re_path(r'^403/$', default_views.permission_denied, kwargs={'exception': Exception("Permission Denied")}),
        re_path(r'^404/$', default_views.page_not_found, kwargs={'exception': Exception("Page not Found")}),
        re_path(r'^429/$', error_429_view, kwargs={'exception': Exception("Too Many Requests")}),
        re_path(r'^500/$', default_views.server_error),
    ]

# These paths are translatable so will be given a language prefix (eg, '/en', '/fr')
urlpatterns = urlpatterns + i18n_patterns(
    path('search/', enzed_search, name='search'),

    re_path(r'^accounts/password/success/', password_change_success, name="password_change_success"),
    re_path(r'^accounts/password/change/', CustomPasswordChangeView.as_view(), name="account_change_password"),
    re_path(r'^accounts/password/set/', CustomPasswordSetView.as_view(), name="account_set_password"),
    re_path(r'^accounts/profile/', profile_view, name='account_profile'),
    path('accounts/<slug:url>/update/', CustomUserUpdateView.as_view(template_name='account/update.html'), name='account_update'),
    path('accounts/<slug:url>/delete/', CustomUserDeleteView.as_view(template_name='account/delete.html'), name='account_delete'),
    path('accounts/deleted/', delete_success, name='delete_success'),
    # Creates urls like yourwebsite.com/accounts/login/
    re_path(r'^accounts/', include('allauth.urls')),

    path('clear-cache', refresh_page_cache, name="refresh-page-cache"),
    path("", include(wagtail_urls)),
)

