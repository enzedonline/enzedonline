from django import forms
from django_filters import BooleanFilter
from wagtail.users.views.users import UserFilterSet as WagtailUserFilterSet


class UserFilterSet(WagtailUserFilterSet):
    is_staff = BooleanFilter(
        label="Is Staff Member?", 
        field_name="is_staff",
        widget=forms.RadioSelect(choices=[(None, "All"), (True, "Yes"), (False, "No")])
    )
