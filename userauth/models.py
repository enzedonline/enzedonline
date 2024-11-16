import random
import string

from django.contrib.auth.models import AbstractUser
from django.db import models
from django.urls import reverse
from django.utils.functional import cached_property
from django.utils.translation import gettext_lazy as _
from django_countries.fields import CountryField
from django_extensions.db.fields import AutoSlugField
from django.conf import settings
from django.utils.http import urlencode
from wagtail.coreutils import safe_md5
from site_settings.models import DefaultUserIcon

class CustomUser(AbstractUser):
    display_name = models.CharField(
        verbose_name=_("Display name"), 
        max_length=30, 
        help_text=_("Will be shown e.g. when commenting")
        )
    city = models.CharField(verbose_name=_("City"), max_length=1024, blank=True, null=True)
    country = CountryField(blank=True, null=True)
    website = models.URLField(blank=True, null=True)
    url = AutoSlugField(populate_from='username')

    class Meta:
        ordering = ['last_name']
        verbose_name = _("User")
        verbose_name_plural = _("Users")

    def __str__(self):
        return f"{self.username}: {self.first_name} {self.last_name}"

    def get_absolute_url(self):
        return reverse('account_profile')

    def slugify_function(self, content):
        return ''.join((random.choice(string.ascii_uppercase + string.digits) for i in range(12)))
         
    def save(self, *args, **kwargs):
        if not self.display_name: self.display_name=f'{self.first_name} {self.last_name}'
        self.icon_url = self.get_absolute_url()
        super().save(*args, **kwargs)

    @cached_property
    def default_menu_icon(self):
        try:
            default = settings.WAGTAILADMIN_BASE_URL + DefaultUserIcon.load().menu_icon.get_rendition('original').url
        except:
            default = "mp"
        return default
        
    @cached_property
    def default_comments_icon(self):
        try:
            default = settings.WAGTAILADMIN_BASE_URL + DefaultUserIcon.load().comments_icon.get_rendition('original').url
        except:
            default = "mp"
        return default

    @property
    def menu_icon(self):
        return self.get_user_icon()
    
    @property
    def comments_icon(self):
        return self.get_user_icon(isMenuIcon=False)
        

    def get_user_icon(self, isMenuIcon=True, size=50):
        default = self.default_menu_icon if isMenuIcon else self.default_comments_icon
        size = (
            int(size) * 2
        )
        gravatar_provider_url = getattr(
            settings, "WAGTAIL_GRAVATAR_PROVIDER_URL", "//www.gravatar.com/avatar"
        )
        try:
            email = self.email
        except:
            email = False
            
        if (not email) or (gravatar_provider_url is None):
            return None

        email_bytes = email.lower().encode("utf-8")
        hash = safe_md5(email_bytes, usedforsecurity=False).hexdigest()
        gravatar_url = "{gravatar_provider_url}/{hash}?{params}".format(
            gravatar_provider_url=gravatar_provider_url.rstrip("/"),
            hash=hash,
            params=urlencode({"s": size, "d": default}),
        )

        return gravatar_url
