from .recipe.views import RecipeTagViewSet
from wagtail.snippets.models import register_snippet

register_snippet(RecipeTagViewSet)