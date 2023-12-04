from allauth.account.views import (LoginView, PasswordChangeView, PasswordSetView,
                                   SignupView)
from django import forms
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import PermissionDenied
from django.shortcuts import render
from django.urls import reverse_lazy
from django.views.generic.edit import DeleteView, UpdateView
from wagtail.models import Locale

from .forms import CustomUserUpdateForm
from .models import CustomUser


class CustomUserSignupView(SignupView):
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['recaptcha_key'] = settings.RECAPTCHA_PUBLIC_KEY
        return context
    
class CustomUserLoginView(LoginView):
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['recaptcha_key'] = settings.RECAPTCHA_PUBLIC_KEY
        return context

class CustomUserUpdateView(UpdateView):
    model = CustomUser
    form_class = CustomUserUpdateForm
    slug_field = 'url'
    slug_url_kwarg = 'url'

    def get(self, request, *args, **kwargs):
        if validate_user(request, self):
            return super().post(request, *args, **kwargs)
        else:
            raise PermissionDenied()

    def post(self, request, *args, **kwargs):
        if validate_user(request, self):
            return super().post(request, *args, **kwargs)
        else:
            raise PermissionDenied()

class CustomUserDeleteView(DeleteView):
    model = CustomUser
    success_url = reverse_lazy('delete_success')
    slug_field = 'url'
    slug_url_kwarg = 'url'

    def get(self, request, *args, **kwargs):
        if validate_user(request, self):
            return render(request, 'account/delete.html')
        else:
            raise PermissionDenied()

    def post(self, request, *args, **kwargs):
        if validate_user(request, self):
            return super().post(request, *args, **kwargs)
        else:
            raise PermissionDenied()

def delete_success(request):
    return render(request, 'account/delete_success.html')

def validate_user(request, user_object) -> bool:
    try:
        user = user_object.get_object()
    except:
        return False
    return (user.pk == request.user.pk)

@login_required
def profile_view(request):
    return render(request, 'account/profile.html')
   
@login_required
def password_change_success(request):
    return render(request, 'account/password_change_success.html')
   
class CustomPasswordChangeView(LoginRequiredMixin, PasswordChangeView):
    def get_success_url(self):
        return '/' + Locale.get_active().language_code + '/accounts/password/success/'
    
class CustomPasswordSetView(LoginRequiredMixin, PasswordSetView):
    def get_success_url(self):
        return '/' + Locale.get_active().language_code + '/accounts/password/success/'
    
