from django.contrib.auth.mixins import LoginRequiredMixin
from allauth.account.views import PasswordChangeView, PasswordSetView
from django.shortcuts import render
from django.urls import reverse_lazy
from django.views.generic.edit import DeleteView, UpdateView
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from wagtail.core.models import Locale

from .forms import CustomUserUpdateForm
from .models import CustomUser

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
    success_url = '/' + Locale.get_active().language_code + '/accounts/password/success/'
    
class CustomPasswordSetView(LoginRequiredMixin, PasswordSetView):
    success_url = '/' + Locale.get_active().language_code + '/accounts/password/success/'
    
