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
    - <h5> = HowToSection
    - <p> and <li> = HowToStep
    - Nested <ul>/<ol> handled
    - Flat <p>/<li> before <h5> remain top-level steps
    """
    if not value:
        return mark_safe("[]")

    html = RichText(value).source
    soup = BeautifulSoup(html, "html.parser")

    instructions = []
    current_section = None
    found_sections = False

    def process_step(elem):
        text = elem.get_text(separator=" ", strip=True)
        if not text:
            return None
        return {"@type": "HowToStep", "text": text}

    # Walk through all relevant elements
    for elem in soup.find_all(["h5", "p", "li", "ul", "ol", "blockquote"]):
        if elem.name == "h5":
            found_sections = True
            if current_section:
                instructions.append(current_section)
            current_section = {
                "@type": "HowToSection",
                "name": elem.get_text(strip=True),
                "itemListElement": []
            }
        elif elem.name in ["p", "li", "blockquote"]:
            step = process_step(elem)
            if step:
                if current_section:
                    current_section["itemListElement"].append(step)
                else:
                    instructions.append(step)
        elif elem.name in ["ul", "ol"]:
            for li in elem.find_all("li", recursive=True):
                step = process_step(li)
                if step:
                    if current_section:
                        current_section["itemListElement"].append(step)
                    else:
                        instructions.append(step)

    if current_section:
        instructions.append(current_section)

    if not found_sections:
        flat_steps = [step for step in instructions if step.get("@type") == "HowToStep"]
        return mark_safe(json.dumps(flat_steps, ensure_ascii=False))

    return mark_safe(json.dumps(instructions, ensure_ascii=False))
