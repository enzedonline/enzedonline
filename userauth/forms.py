from django import forms
from django.forms import ModelForm
from django.utils.translation import gettext_lazy as _
from wagtail.users.forms import UserCreationForm, UserEditForm

from .models import CustomUser

class CustomUserUpdateForm(ModelForm):
    class Meta:
        model = CustomUser
        fields = ['first_name', 'last_name', 'display_name', 'city', 'country', 'website']

class SignupForm(forms.Form):
    first_name = forms.CharField(max_length=30, label=_("First name"))
    last_name = forms.CharField(max_length=30, label=_("Last name"))
    display_name = forms.CharField(max_length=30, label=_("Display name"), help_text=_("Will be shown e.g. when commenting."))
    website = forms.CharField(max_length=30, label=_("Website"))

    def signup(self, request, user):
        display_name = self.cleaned_data['display_name']
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']
        user.display_name = display_name or f'{user.first_name} {user.last_name}'
        user.website = self.cleaned_data['website']
        user.save()

class WagtailUserCreationForm(UserCreationForm):
    display_name = forms.CharField(max_length=30, label=_("Display name"), help_text=_("Will be shown e.g. when commenting."))
    website = forms.CharField(max_length=30, label=_("Website"))

    class Meta(UserCreationForm.Meta):
        model = CustomUser

class WagtailUserEditForm(UserEditForm):
    display_name = forms.CharField(max_length=30, label=_("Display name"), help_text=_("Will be shown e.g. when commenting."))
    website = forms.CharField(max_length=30, label=_("Website"))

    class Meta(UserEditForm.Meta):
        model = CustomUser
