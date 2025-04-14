from allauth.account.forms import LoginForm as BaseLoginForm
from allauth.account.forms import SignupForm as BaseSignupForm
from django import forms
from django.forms import ModelForm
from django.utils.translation import gettext_lazy as _
from django_countries.fields import CountryField
from django_recaptcha.fields import ReCaptchaField
from django_recaptcha.widgets import ReCaptchaV3
from wagtail.users.forms import UserCreationForm, UserEditForm

from .models import CustomUser


class LoginForm(BaseLoginForm):
    recaptcha = ReCaptchaField(widget=ReCaptchaV3(action='login'))
    
class SignupForm(BaseSignupForm):
    first_name = forms.CharField(max_length=30, label=_("First name"))
    last_name = forms.CharField(max_length=30, label=_("Last name"))
    display_name = forms.CharField(max_length=30, label=_("Display name"), help_text=_("Will be shown e.g. when commenting."))
    website = forms.CharField(max_length=30, label=_("Website"), required=False)
    country = CountryField().formfield(required=False, widget=forms.Select())
    recaptcha = ReCaptchaField(widget=ReCaptchaV3(action='signup'))
        
    def signup(self, request, user):
        display_name = self.cleaned_data['display_name']
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']
        user.display_name = display_name or f'{user.first_name} {user.last_name}'
        user.website = self.cleaned_data['website']
        user.country = self.cleaned_data['country']
        user.save()

class CustomUserUpdateForm(ModelForm):
    class Meta:
        model = CustomUser
        fields = ['first_name', 'last_name', 'display_name', 'website', 'country']

class WagtailUserCreationForm(UserCreationForm):
    display_name = forms.CharField(max_length=30, label=_("Display name"), help_text=_("Will be shown e.g. when commenting."))
    website = forms.CharField(max_length=30, label=_("Website"), required=False)

    class Meta(UserCreationForm.Meta):
        model = CustomUser
        fields = UserEditForm.Meta.fields | {'display_name', 'country', 'website'}

class WagtailUserEditForm(UserEditForm):
    display_name = forms.CharField(max_length=30, label=_("Display name"), help_text=_("Will be shown e.g. when commenting."))
    website = forms.CharField(max_length=30, label=_("Website"), required=False)

    class Meta(UserEditForm.Meta):
        model = CustomUser
        fields = UserEditForm.Meta.fields | {'display_name', 'country', 'website'}
