from django import template

register = template.Library()

@register.simple_tag()
def get_blog_index(blog_page):
    blog_index = blog_page.get_parent().specific
    return blog_index

@register.simple_tag()
def get_prev_next(page):
    page = page.specific
    prev = page.get_prev_siblings().specific(defer=False).live().first()
    next = page.get_next_siblings().specific(defer=False).live().first()
    return {'prev': prev, 'next': next}