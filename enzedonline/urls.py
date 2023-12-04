from django.conf import settings
from django.conf.urls.i18n import i18n_patterns
from django.contrib import admin
from django.urls import include, path, re_path
from django.views import defaults as default_views
from django.views.i18n import JavaScriptCatalog
from wagtail import urls as wagtail_urls
from wagtail.admin import urls as wagtailadmin_urls
from wagtail.documents import urls as wagtaildocs_urls

from core.views import RobotsView, refresh_page_cache, sitemap
from search.views import enzed_search
from userauth.views import (CustomPasswordChangeView, CustomPasswordSetView,
                            CustomUserDeleteView, CustomUserLoginView,
                            CustomUserSignupView, CustomUserUpdateView,
                            delete_success, password_change_success,
                            profile_view)


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
]

if settings.DEBUG:
    from django.conf.urls.static import static
    from django.contrib.staticfiles.urls import staticfiles_urlpatterns

    # Serve static and media files from development server
    urlpatterns += staticfiles_urlpatterns()
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    re_path(r'^403/$', default_views.permission_denied, kwargs={'exception': Exception("Permission Denied")}),
    re_path(r'^404/$', default_views.page_not_found, kwargs={'exception': Exception("Page not Found")}),
    re_path(r'^500/$', default_views.server_error),    # For anything not caught by a more specific rule above, hand over to

# These paths are translatable so will be given a language prefix (eg, '/en', '/fr')
urlpatterns = urlpatterns + i18n_patterns(
    path('search/', enzed_search, name='search'),

    re_path(r'^accounts/password/success/', password_change_success, name="password_change_success"),
    re_path(r'^accounts/password/change/', CustomPasswordChangeView.as_view(), name="account_change_password"),
    re_path(r'^accounts/password/set/', CustomPasswordSetView.as_view(), name="account_set_password"),
    re_path(r'^accounts/profile/', profile_view, name='account_profile'),
    path('accounts/login/', CustomUserLoginView.as_view(template_name='account/login.html'), name='account_login'),
    path('accounts/signup/', CustomUserSignupView.as_view(template_name='account/signup.html'), name='account_signup'),
    path('accounts/<slug:url>/update/', CustomUserUpdateView.as_view(template_name='account/update.html'), name='account_update'),
    path('accounts/<slug:url>/delete/', CustomUserDeleteView.as_view(template_name='account/delete.html'), name='account_delete'),
    path('accounts/deleted/', delete_success, name='delete_success'),
    # Creates urls like yourwebsite.com/accounts/login/
    re_path(r'^accounts/', include('allauth.urls')),

    path('clear-cache', refresh_page_cache, name="refresh-page-cache"),
    path("", include(wagtail_urls)),
)

