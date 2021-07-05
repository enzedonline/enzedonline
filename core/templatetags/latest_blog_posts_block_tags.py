from django import template
from blog.models import BlogDetailPage
from wagtail_localize.synctree import Locale
register = template.Library()

@register.simple_tag()
def get_latest_posts(post_count):
    posts = BlogDetailPage.objects.live().public().filter(locale_id=Locale.get_active().id).reverse()
    return posts[:post_count]

    