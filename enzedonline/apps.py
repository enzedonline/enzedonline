from wagtail.users.apps import WagtailUsersAppConfig

class CustomUsersAppConfig(WagtailUsersAppConfig):
    user_viewset = "userauth.viewsets.UserViewSet"
