import os
from django.urls import reverse_lazy

PROJECT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BASE_DIR = os.path.dirname(PROJECT_DIR)

INSTALLED_APPS = [
    'home',
    'search',
    'service',
    'blog',
    'menu',
    'core',
    'site_settings',
    'contact',
    'userauth',

    'adv_cache_tag',
    'rest_framework',
    'wagtailmetadata',
    'widget_tweaks',
    'django_comments_xtd',
    'django_comments',
    'django_extensions',
    'wagtail_localize',
    'wagtail_localize.locales',

    'wagtail.contrib.forms',
    'wagtail.contrib.redirects',
    'wagtail.contrib.routable_page',
    'wagtail.contrib.modeladmin',
    'wagtail.contrib.settings',
    'wagtail.embeds',
    'wagtail.sites',
    'wagtail.users',
    'wagtail.snippets',
    'wagtail.documents',
    'wagtail.images',
    'wagtail.search',
    'wagtail.admin',
    'wagtail',

    'modelcluster',
    'taggit',

    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.sites',    

    'allauth',
    'allauth.account',
    'allauth.socialaccount',
    'allauth.socialaccount.providers.facebook',
    'allauth.socialaccount.providers.google',
    'allauth.socialaccount.providers.linkedin_oauth2',

    'captcha',
    'wagtailcaptcha',
]

MIDDLEWARE = [
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'django.middleware.locale.LocaleMiddleware',
    'wagtail.contrib.redirects.middleware.RedirectMiddleware',
    "allauth.account.middleware.AccountMiddleware",
]

ROOT_URLCONF = 'enzedonline.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [
            os.path.join(PROJECT_DIR, 'templates'),
            os.path.join(PROJECT_DIR, 'templates/userauth/'),
            os.path.join(PROJECT_DIR, 'templates/userauth/account'),
        ],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'wagtail.contrib.settings.context_processors.settings',
            ],
        },
    },
]

WSGI_APPLICATION = 'enzedonline.wsgi.application'

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
    
]

AUTHENTICATION_BACKENDS = (
    # Needed to login by username in Django admin, regardless of `allauth`
    'django.contrib.auth.backends.ModelBackend',

    # `allauth` specific authentication methods, such as login by e-mail
    'allauth.account.auth_backends.AuthenticationBackend',
)

# Internationalization
LANGUAGE_CODE = 'en-gb'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_L10N = True
WAGTAIL_I18N_ENABLED = True
USE_TZ = True

WAGTAIL_CONTENT_LANGUAGES = LANGUAGES = [
    ('en', "English"),
]

CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.db.DatabaseCache',
        'LOCATION': 'cache_table',
        'TIMEOUT': None,
    },
    'renditions': {
        'BACKEND': 'django.core.cache.backends.db.DatabaseCache',
        'LOCATION': 'image_cache',
        'TIMEOUT': 600,
        'OPTIONS': {
            'MAX_ENTRIES': 2000
        }
    }
}

# ADVANCED CACHE
ADV_CACHE_RESOLVE_NAME = True
ADV_CACHE_INCLUDE_PK = True
ADV_CACHE_VERSIONING = True

# MAX IMAGE SIZE
WAGTAILIMAGES_MAX_UPLOAD_SIZE = 10 * 1024 * 1024

# Static files (CSS, JavaScript, Images)

STATICFILES_FINDERS = [
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
]

STATICFILES_DIRS = [
    os.path.join(PROJECT_DIR, 'static'),
    os.path.join(PROJECT_DIR, 'static/css'),
    os.path.join(BASE_DIR, 'media'),
]

# ManifestStaticFilesStorage is recommended in production, to prevent outdated
# JavaScript / CSS assets being served from cache (e.g. after a Wagtail upgrade).
# See https://docs.djangoproject.com/en/3.1/ref/contrib/staticfiles/#manifeststaticfilesstorage
STATICFILES_STORAGE = 'django.contrib.staticfiles.storage.ManifestStaticFilesStorage'

STATIC_ROOT = os.path.join(BASE_DIR, 'static')
STATIC_URL = '/static/'

MEDIA_ROOT = os.path.join(BASE_DIR, 'media')
MEDIA_URL = '/media/'

WAGTAILEMBEDS_RESPONSIVE_HTML = True

# Wagtail settings

WAGTAIL_SITE_NAME = "enzedonline"

# Embeds
WAGTAILEMBEDS_FINDERS = [
    {
        'class': 'wagtail.embeds.finders.oembed',
        'class': 'core.oembedfinder.YouTubeShortsFinder'      
    }
]
WAGTAILEMBEDS_RESPONSIVE_HTML = True

# multiple configs not supported for one backend type
# revisit at some later date if this gets addressed
# change search config to 'simple' if needing multi-lingual
WAGTAILSEARCH_BACKENDS = {
    'default': {
        'BACKEND': 'wagtail.search.backends.database',
        'SEARCH_CONFIG': 'english_extended',
    },
    # 'es': {
    #     'BACKEND': 'wagtail.search.backends.database',
    #     'SEARCH_CONFIG': 'spanish_extended',
    #     'INDEX' : 'es'
    # },
    # 'en': {
    #     'BACKEND': 'wagtail.search.backends.database',
    #     'SEARCH_CONFIG': 'english_extended',
    #     'INDEX' : 'en'
    # },
}

# # ALLAUTH settings
AUTH_USER_MODEL = 'userauth.CustomUser'
WAGTAIL_USER_CREATION_FORM = 'userauth.forms.WagtailUserCreationForm'
WAGTAIL_USER_EDIT_FORM = 'userauth.forms.WagtailUserEditForm'
WAGTAIL_USER_CUSTOM_FIELDS = ['display_name', 'city', 'country', 'website']
ACCOUNT_AUTHENTICATION_METHOD = 'email'
ACCOUNT_EMAIL_REQUIRED = True
ACCOUNT_EMAIL_VERIFICATION = 'mandatory'
ACCOUNT_USERNAME_REQUIRED = False
ACCOUNT_SIGNUP_FORM_CLASS = 'userauth.forms.SignupForm'
ACCOUNT_LOGIN_ON_PASSWORD_RESET = True
ACCOUNT_LOGIN_ON_EMAIL_CONFIRMATION = True
ACCOUNT_SESSION_REMEMBER = True
# ACCOUNT_AUTHENTICATED_LOGIN_REDIRECTS = False
LOGIN_URL = reverse_lazy('account_login')
# LOGIN_REDIRECT_URL = reverse_lazy('account_profile')

SOCIALACCOUNT_AUTO_SIGNUP = True
SOCIALACCOUNT_EMAIL_VERIFICATION = "none"

SOCIALACCOUNT_PROVIDERS = {
    'google': {
        'SCOPE': [
            'profile',
            'email',
        ],
        'AUTH_PARAMS': {
            'access_type': 'online',
        }
    },
    'facebook': {
        'METHOD': 'oauth2',
        'SCOPE': ['email', 'public_profile'],
        'VERIFIED_EMAIL': True,
    },
    'linkedin': {
        'SCOPE': [
            'r_basicprofile',
            'r_emailaddress'
        ],
        'PROFILE_FIELDS': [
            'id',
            'first-name',
            'last-name',
            'email-address',
            'picture-url',
            'public-profile-url',
        ],
        'VERIFIED_EMAIL': True,
    }

}

WAGTAILADMIN_RICH_TEXT_EDITORS = {
    'default': {
        'WIDGET': 'wagtail.admin.rich_text.DraftailRichTextArea',
        'OPTIONS': {
            'features': ['h2', 'h3', 'h4', 'h5', 'h6', 'bold', 'italic', 'underline', 
                         'ol', 'ul', 'checklist',
                         'link', 'hr', 'larger', 'smaller', 'highlight', 'inline-code', 'document-link', 
                         'fa', 'blockquote',
                         'left-align', 'centre-align', 'right-align', 'code-block']
        }
    },
    'minimal': {
        'WIDGET': 'wagtail.admin.rich_text.DraftailRichTextArea',
        'OPTIONS': {
            'features': ['bold', 'italic', 'link']
        }
    },
    'basic': {
        'WIDGET': 'wagtail.admin.rich_text.DraftailRichTextArea',
        'OPTIONS': {
            'features': ['h2', 'h3', 'h4', 'bold', 'italic', 'link', 'ol', 'ul', 'hr', 'fa']
        }
    },
}

WAGTAILMETADATA_IMAGE_FILTER = "thumbnail-688x272|format-png"

# FIX NEEDED FOR DJANGO 3.2.x
DEFAULT_AUTO_FIELD = 'django.db.models.AutoField'

