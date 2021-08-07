from allauth.socialaccount.forms import DisconnectForm
from django import template

register = template.Library()

@register.simple_tag()
def social_accounts(request):
    disconnect_list = DisconnectForm(request=request)
    return disconnect_list.accounts