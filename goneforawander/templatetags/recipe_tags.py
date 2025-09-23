import json

from bs4 import BeautifulSoup
from django import template
from django.utils.html import escapejs
from django.utils.safestring import mark_safe
from wagtail.rich_text import RichText

register = template.Library()

SKIP_ELEMENTS = ["h1","h2","h3","h4","h5","h6","strong","b"]

def extract_text_elements(soup, tags=("p", "li", "blockquote"), skip_tags=None):
    """Recursively extract text from given tags, ignoring skip_tags."""
    if skip_tags is None:
        skip_tags = []

    items = []
    for elem in soup.find_all(tags):
        if elem.find_parent(skip_tags):
            continue
        if elem.name in skip_tags:
            continue
        text = elem.get_text(separator=" ", strip=True)
        if text:
            items.append(text)
    return items

@register.filter
def ingredients_to_array(value):
    """
    Convert a RichTextField into a JSON-LD recipeIngredient array.
    - Ignores headings (<h1>-<h6>) and bold/strong (<b>/<strong>)
    - Includes <p> and <li> elements (nested lists included)
    """
    if not value:
        return mark_safe("[]")

    html = RichText(value).source
    soup = BeautifulSoup(html, "html.parser")

    items = extract_text_elements(soup, tags=("p", "li", "blockquote"), skip_tags=SKIP_ELEMENTS)
    return mark_safe(json.dumps(items, ensure_ascii=False))


@register.filter
def instructions_to_array(value):
    """
    Convert a RichTextField into JSON-LD recipeInstructions.

    Rules:
    - <h5> marks the start of a HowToSection.
    - Only the next top-level <p>/<blockquote>/<ul>/<ol> belongs to that section.
      * If <p>/<blockquote>: the section has one HowToStep (that element's text).
      * If <ul>/<ol>: the section has one HowToStep per immediate <li>.
    - Other top-level blocks are added as standalone HowToStep items.
    """
    if not value:
        return mark_safe("[]")

    html = RichText(value).source
    soup = BeautifulSoup(html, "html.parser")

    def process_step(elem):
        text = elem.get_text(separator=" ", strip=True)
        return {"@type": "HowToStep", "text": text} if text else None

    def process_list(list_elem):
        steps = []
        for li in list_elem.find_all("li", recursive=True):
            # only immediate li of this list (avoid nested duplication)
            if li.find_parent(["ul", "ol"]) is not list_elem:
                continue
            st = process_step(li)
            if st:
                steps.append(st)
        return steps

    # Only top-level blocks, in order
    top_level = [
        el for el in soup.find_all(["h5", "p", "ul", "ol", "blockquote"], recursive=False)
        if getattr(el, "name", None)
    ]

    instructions = []
    any_sections = False
    i = 0
    while i < len(top_level):
        el = top_level[i]

        if el.name == "h5":
            title = el.get_text(strip=True)
            steps_for_section = []
            # Look at the immediate next top-level block only
            if i + 1 < len(top_level):
                nxt = top_level[i + 1]
                if nxt.name in ("p", "blockquote"):
                    st = process_step(nxt)
                    if st:
                        steps_for_section.append(st)
                    i += 2  # consume h5 and its following block
                elif nxt.name in ("ul", "ol"):
                    steps_for_section.extend(process_list(nxt))
                    i += 2  # consume h5 and its following list
                else:
                    i += 1  # no valid following block to consume
            else:
                i += 1

            if steps_for_section:
                any_sections = True
                instructions.append({
                    "@type": "HowToSection",
                    "name": title,
                    "itemListElement": steps_for_section,
                })
            continue

        if el.name in ("p", "blockquote"):
            st = process_step(el)
            if st:
                instructions.append(st)
            i += 1
            continue

        if el.name in ("ul", "ol"):
            instructions.extend(process_list(el))
            i += 1
            continue

        i += 1

    if not any_sections:
        # Only steps (flat array)
        flat = [item for item in instructions if item.get("@type") == "HowToStep"]
        return mark_safe(json.dumps(flat, ensure_ascii=False))

    return mark_safe(json.dumps(instructions, ensure_ascii=False))
