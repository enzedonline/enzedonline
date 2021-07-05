from django.shortcuts import render
from django.urls import reverse_lazy
from django.views.generic.edit import DeleteView, UpdateView
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied

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
    success_url = reverse_lazy('account_signup')
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

def validate_user(request, user_object) -> bool:
    try:
        user = user_object.get_object()
    except:
        return False
    return (user.pk == request.user.pk)

@login_required
def profile_view(request):
    return render(request, 'account/profile.html')
   