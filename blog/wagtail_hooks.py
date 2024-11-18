from django.contrib import messages
from django.db.models import Count
from taggit.models import Tag
from wagtail import hooks

from .models import BlogDetailPage

def purge_unused_tags():
    unused_tags = Tag.objects.annotate(
        ntech=Count('blog_techblogpagetag_items'),
        npersonal=Count('blog_personalblogpagetag_items')
    ).filter(
        ntech=0, npersonal=0
    ).values('id')
    
    if unused_tags:
        unused_tag_ids = {tag['id'] for tag in unused_tags}    
        draft_tags=set()
        pages_with_drafts=BlogDetailPage.objects.filter(has_unpublished_changes=True)
        for page in pages_with_drafts:
            draft=page.get_latest_revision_as_object()
            tag_ids = draft.tags.values('id', flat=True)
            draft_tags |= set(tag_ids)
        unused_tag_ids = unused_tag_ids.difference(draft_tags)
        if unused_tag_ids:
            Tag.objects.filter(id__in=unused_tag_ids).delete()

@hooks.register('after_delete_page')
@hooks.register('after_publish_page')
def do_after_publish_delete_page(request, page):
    if issubclass(page.specific_class, BlogDetailPage):
        purge_unused_tags()

@hooks.register("after_create_page")
@hooks.register("after_edit_page")
def get_wordcount(request, page):
    if issubclass(page.specific_class, BlogDetailPage):
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
