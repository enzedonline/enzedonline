import random
import string

from django.contrib.auth.models import AbstractUser
from django.db import models
from django.urls import reverse
from django.utils.translation import gettext_lazy as _
from django_countries.fields import CountryField
from django_extensions.db.fields import AutoSlugField

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
        super().save(*args, **kwargs)
