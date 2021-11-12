from django import template

register = template.Library()

@register.simple_tag()
def get_query_selector(level):
    selector = []
    for h_level in range(2, 2 + level):
        selector.append(f"h{h_level}")
    return ",".join(selector)
