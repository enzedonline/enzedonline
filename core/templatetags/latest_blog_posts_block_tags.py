from django import template
from blog.models import BlogDetailPage
from wagtail.models import Locale

register = template.Library()


@register.simple_tag()
def get_latest_posts(post_count):
    # .order_by('first_published_at') required to pick up both blog types in order
    posts = (
        BlogDetailPage.objects.live().defer_streamfields()
        .public()
        .filter(locale_id=Locale.get_active().id)
        .order_by("first_published_at")
        .reverse()
    )
    return posts[:post_count]
