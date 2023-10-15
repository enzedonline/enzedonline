from allauth.account.forms import LoginForm
from django import template

register = template.Library()

@register.simple_tag()
def get_login_form():
    return LoginForm()


# response.context_data['login_form'] = LoginForm()