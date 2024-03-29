from django import template
from wagtail.documents.models import Document

register = template.Library()

@register.simple_tag()
def button_appearance(style, outline):
    if outline:
        style = style.replace("-", "-outline-")
    return style

@register.simple_tag()
def text_appearance(text_size, outline):
    style = ["font-headings", text_size.replace("h", "fs-")]
    if outline:
        style.append("p-0")
    else:
        style.append("mb-2")
    return " ".join(style)

@register.simple_tag()
def document_list(sort_by, tag_list=None):
    docs = Document.objects.all()
    if tag_list:
        docs = docs.filter(tags__slug__in=tag_list.split(','))
    if sort_by == 'title':
        return docs.order_by('title')
    return docs.order_by('created_at').reverse()
