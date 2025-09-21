from wagtail.snippets.views.snippets import SnippetViewSet

from .models import RecipeTag


class RecipeTagViewSet(SnippetViewSet):
    model = RecipeTag
    list_display = ["name", "tag_type"]
    list_filter = {"name": ["icontains"], "slug": ["icontains"], "tag_type": ["exact"]}
    list_per_page = 50
    ordering = ["tag_type", "name"]
    add_to_admin_menu = False
    menu_icon = "food"

