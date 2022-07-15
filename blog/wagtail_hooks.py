from wagtail import hooks
from taggit.models import Tag
from django.db.models import Count
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

