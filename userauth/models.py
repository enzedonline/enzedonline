import random
import string

from django.contrib.auth.models import AbstractUser
from django.db import models
from django.urls import reverse
from django.utils.translation import gettext_lazy as _
from django_countries.fields import CountryField
from django_extensions.db.fields import AutoSlugField
from wagtail.coreutils import safe_md5

class CustomUser(AbstractUser):
    display_name = models.CharField(
        verbose_name=_("Display name"), 
        max_length=30, 
        help_text=_("Will be shown e.g. when commenting")
        )
    city = models.CharField(verbose_name=_("City"), max_length=1024, blank=True, null=True)
    country = CountryField(blank=True, null=True)
    website = models.URLField(blank=True, null=True)
    url = AutoSlugField(populate_from='username') # type: ignore

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
        if not self.display_name: self.display_name=f'{self.first_name} {self.last_name}'[:30]
        self.icon_url = self.get_absolute_url()
        super().save(*args, **kwargs)

    @property
    def comments_icon(self):
        try:
            email = self.email
        except:
            email = False
        if not email:
            email = 'nobody@nowhere.xyz'
        hash = safe_md5(email.lower().encode("utf-8"), usedforsecurity=False).hexdigest()
        return f"//www.gravatar.com/avatar/{hash}?d=mp"
