from django import template

register = template.Library()

@register.simple_tag()
def get_query_selector(level):
    selector = []
    for level in range(2, level+1):
        selector.append(f"h{level}")
    return ",".join(selector)
