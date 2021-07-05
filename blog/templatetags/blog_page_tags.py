from django import template
from blog.models import BlogListingPage
from wagtail.images.models import Image

register = template.Library()

@register.simple_tag()
def get_blog_index():
    blog_list_page = BlogListingPage.objects.all().first().localized
    return blog_list_page

@register.simple_tag()
def get_prev_next(page):
    prev = page.get_prev_siblings().specific(defer=False).live().first()
    next = page.get_next_siblings().specific(defer=False).live().first()
    return {'prev': prev, 'next': next}