from wagtail.users.views.users import UserViewSet as WagtailUserViewSet

from .forms import WagtailUserCreationForm, WagtailUserEditForm
from .filters import UserFilterSet

class UserViewSet(WagtailUserViewSet):
    filterset_class = UserFilterSet

    # This replaces the WAGTAIL_USER_EDIT_FORM and WAGTAIL_USER_CREATION_FORM settings
    def get_form_class(self, for_update=False):
        if for_update:
            return WagtailUserEditForm
        return WagtailUserCreationForm
    
