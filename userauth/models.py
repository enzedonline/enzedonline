import glob
import os
import random
import string

from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.urls import reverse
from django.utils.translation import gettext_lazy as _
from django_countries.fields import CountryField
from django_extensions.db.fields import AutoSlugField
from django_resized import ResizedImageField


def rename_avatar(instance, filename):
    upload_to = 'avatars'
    if instance.url:
        ext = filename.split('.')[-1]
        filename = '{}.{}'.format(instance.url, ext)

    return os.path.join(upload_to, filename)

class CustomUser(AbstractUser):
    display_name = models.CharField(
        verbose_name=_("Display name"), 
        max_length=30, 
        help_text=_("Will be shown e.g. when commenting")
        )
    city = models.CharField(verbose_name=_("City"), max_length=1024, blank=True, null=True)
    country = CountryField(blank=True, null=True)
    photo = ResizedImageField(
        verbose_name=_("Icon"), 
        size=[60, 60], 
        quality=75, 
        crop=['middle', 'center'], 
        force_format='PNG',
        upload_to=rename_avatar, 
        blank=True, 
        null=True
        )
    url = AutoSlugField(populate_from='username')

    class Meta:
        ordering = ['last_name']

    def __str__(self):
        return f"{self.username}: {self.first_name} {self.last_name}"

    def get_absolute_url(self):
        return reverse('account_profile')

    def slugify_function(self, content):
        return ''.join((random.choice(string.ascii_uppercase + string.digits) for i in range(12)))
         
    def delete_avatar(self):
        avatar = os.path.join(settings.BASE_DIR, 'media', 'avatars', self.url + '*.*') 
        for filename in glob.glob(avatar):
            os.remove(filename)

    def save(self, *args, **kwargs):
        avatar = 'avatars/' + self.url + '.apng'
        if avatar != self.photo:
            self.delete_avatar()
        if not self.display_name:
            self.display_name = self.first_name + ' ' + self.last_name       
        super(CustomUser, self).save(*args, **kwargs) 

    def delete(self, *args, **kwargs):
        self.delete_avatar()
        super(CustomUser, self).delete(*args, **kwargs) 

