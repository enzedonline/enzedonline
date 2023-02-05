from django.contrib import messages
from django.db.models import Count
from taggit.models import Tag
from wagtail import hooks

from .models import PersonalBlogDetailPage, TechBlogDetailPage


def purge_unused_tags():
    tags = Tag.objects.annotate(ntech=Count('blog_techblogpagetag_items')).filter(ntech=0)
    tags.annotate(npersonal=Count('blog_personalblogpagetag_items')).filter(npersonal=0).delete()

@hooks.register('after_delete_page')
def do_after_delete_page(request, page):
    index_type = page.__class__
    if(index_type== PersonalBlogDetailPage or index_type== TechBlogDetailPage):
        purge_unused_tags()

@hooks.register('after_publish_page')
def do_after_publish_page(request, page):
    index_type = page.__class__
    if(index_type== PersonalBlogDetailPage or index_type== TechBlogDetailPage):
        purge_unused_tags()

@hooks.register("after_edit_page")
def get_wordcount(request, page):
    if page.specific_class in [TechBlogDetailPage, PersonalBlogDetailPage]:
        try:
            page.wordcount = page.get_wordcount()
            if page.has_unpublished_changes:
                page.save_revision()
            else:
                page.save()
        except Exception as e:
            print(f"{type(e).__name__} at line {e.__traceback__.tb_lineno} of {__file__}: {e}")       
            messages.error(request, 'There was a problem generating the word count')
