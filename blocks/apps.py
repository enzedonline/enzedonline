from django.apps import AppConfig


class BlocksConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "blocks"

    def ready(self):
        from .map import MapBlockSettings
