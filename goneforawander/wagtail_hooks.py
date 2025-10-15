from django.contrib import messages
from wagtail import hooks
from wagtail.snippets.models import register_snippet

from .models import TravelBlogPage
from .recipe.views import RecipeTagViewSet

register_snippet(RecipeTagViewSet)

@hooks.register("after_create_page")
@hooks.register("after_edit_page")
def get_wordcount(request, page):
    if issubclass(page.specific_class, TravelBlogPage):
        try:
            page.wordcount = page.get_wordcount()
            if page.has_unpublished_changes:
                page.save_revision()
            else:
                page.save()
        except Exception as e:
            print(f"{type(e).__name__} at line {e.__traceback__.tb_lineno} of {__file__}: {e}")
            messages.error(
                request, 'There was a problem generating the word count')