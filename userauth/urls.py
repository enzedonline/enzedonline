from django.urls import path
from .views import *

urlpatterns = [
    path('profile/', profile_view, name='account_profile'),
    path('<slug:url>/update/', CustomUserUpdateView.as_view(template_name='account/update.html'), name='account_update'),
    path('<slug:url>/delete/', CustomUserDeleteView.as_view(template_name='account/delete.html'), name='account_delete'),
]