import fnmatch
import importlib
import os
import re
from collections import OrderedDict
from html import unescape

from bs4 import BeautifulSoup
from django.core.cache import caches
from django.db import connection
from lxml import etree
from wagtail.blocks import ListBlock, StreamValue


def strip_svg_markup(svg_markup):
    """Strip <script> tags, height and width attributes from svg markup"""
    root = etree.fromstring(svg_markup.encode('utf-8'))
    for element in root.findall(".//{http://www.w3.org/2000/svg}script"):
        element.getparent().remove(element)
    for element in root.iter():
        element.attrib.pop('height', None)
        element.attrib.pop('width', None)
    return etree.tostring(root, encoding='unicode', method='xml', xml_declaration=False)
    
def clear_page_cache():
    caches["default"].clear()
    caches["renditions"].clear()


def purge_page_cache_fragments(slug):
    sql = f"DELETE FROM public.cache_table WHERE cache_key LIKE '%template.cache.{slug}.%';"
    with connection.cursor() as cursor:
        cursor.execute(sql)


def purge_menu_cache_fragments():
    sql = f"DELETE FROM public.cache_table WHERE cache_key LIKE '%.menu.%';"
    with connection.cursor() as cursor:
        cursor.execute(sql)
    sql = f"DELETE FROM public.cache_table WHERE cache_key LIKE '%.footer.%';"
    with connection.cursor() as cursor:
        cursor.execute(sql)


def purge_blog_list_cache_fragments():
    sql = f"DELETE FROM public.cache_table WHERE cache_key LIKE '%next_prev%';"
    with connection.cursor() as cursor:
        cursor.execute(sql)
    sql = f"DELETE FROM public.cache_table WHERE cache_key LIKE '%blog_list%';"
    with connection.cursor() as cursor:
        cursor.execute(sql)


def paginator_range(requested_page, last_page_num, wing_size=5):
    """Given a 'wing size', return a range for pagination.
    Wing size is the number of pages that flank either side of the selected page
    Presuming missing pages will be denoted by an elipse '...',
    the minimum width is 2xelipse + 2x wing size + selcted page
    if the elipse is one off the outer limit, replace it with the outer limit
    The range returned will always return a fixed number of boxes to the properly configured pagination nav"""

    # If last page number is within minimum size, just return entire range
    if last_page_num <= ((2 * (wing_size + 1)) + 1):
        return range(1, last_page_num + 1)

    # find the start page or return 1 if within wing range
    start_page = max([requested_page - wing_size, 1])

    if start_page == 1:
        # first elipse is 1, add one to the end and also one for the selected page (also 1 in this case)
        end_page = (2 * wing_size) + 2
    else:
        # return range end or last page if over that
        end_page = min([requested_page + wing_size, last_page_num])
        if end_page == last_page_num:
            # last elipse is taken by last page number, start is twice the wing plus 1 for the selected page
            # and 1 for the replaced elipse
            start_page = last_page_num - ((2 * wing_size) + 1)

    # if the ends are within one place of the end points, replace with the actual end point
    # otherwise it's just an elipse where the endpoint would be ... pointless
    if start_page == 2:
        start_page = 1
    if end_page == last_page_num - 1:
        end_page = last_page_num
    return range(start_page, end_page + 1)


def isfloat(element: str) -> bool:
    try:
        float(element)
        return True
    except ValueError:
        return False


PUNCTUATION = "!\"#$%&'()*+,-:;<=>?@[\\]^_`{|}~“”‘’–«»‹›¿¡"
TRANSLATION_TABLE = str.maketrans("", "", PUNCTUATION)

def get_streamfield_text(
    streamfield,
    strip_newlines=True,
    strip_punctuation=True,
    lowercase=False,
    strip_tags=["style", "script"],
):
    """
    Extracts and processes text from a StreamField.

    Args:
        streamfield: The StreamField to extract text from.
        strip_newlines (bool): Whether to strip newlines from the text. Default is True.
        strip_punctuation (bool): Whether to strip punctuation from the text. Default is True.
        lowercase (bool): Whether to convert the text to lowercase. Default is False.
        strip_tags (list): List of HTML tags to strip from the text. Default is ["style", "script"].

    Returns:
        str: The processed text extracted from the StreamField.
    """

    html = streamfield.render_as_block()
    soup = BeautifulSoup(unescape(html), "html.parser")

    # strip unwanted tags tags (e.g. ['code', 'script', 'style'])
    # <style> & <script> by default
    if strip_tags:
        for script in soup(strip_tags):
            script.extract()

    inner_text = " ".join(soup.findAll(text=True))

    # replace &nbsp; with space
    inner_text = inner_text.replace("\xa0", " ")

    # replace & with and
    inner_text = inner_text.replace(" & ", " and ")

    # strip font awesome text
    inner_text = re.sub(r"\bfa-[^ ]*", "", inner_text)

    if strip_newlines:
        # Replace multiple newlines followed by any character with a single space
        inner_text = re.sub(r"([\n]+.?)+", " ", inner_text)

    if strip_punctuation:
        # replace xx/yy with xx yy
        inner_text = re.sub(r"(?<=\S)/(?=\S)", " ", inner_text)
        # strip full stops, leave decimal points and point separators
        inner_text = re.sub(r"\.(?=\s)", "", inner_text)
        inner_text = inner_text.translate(TRANSLATION_TABLE)

    if lowercase:
        inner_text = inner_text.lower()

    # strip excess whitespace
    inner_text = re.sub(r" +", " ", inner_text).strip()

    return inner_text


def count_words(text):
    """
    Count the number of words in a given text.

    Args:
        text (str): The text to count words in.

    Returns:
        int: The number of words in the text, or -1 if an error occurs.
    """
    try:
        if not text: return 0
        word_break_chars = "[\n|\r|\t|\f| ]"
        ignore_words = ["", "-", "−", "–", "/"]
        return len(
            [x for x in re.split(word_break_chars, text) if not x in ignore_words]
        )
    except Exception:
        return -1


def get_custom_icons():
    # Specify the root folder
    root_folder = 'enzedonline/templates'
    icons_folder = 'icons'

    # Specify the file extension you're looking for
    file_extension = '*.svg'

    # Initialize an empty list to store relative file paths
    icons = []

    # Construct the path to the 'enzedonline/templates/icons' folder
    icons_path = os.path.join(root_folder, icons_folder)

    # Walk through the directory and find .svg files in the 'enzedonline/templates/icons' folder
    for foldername, subfolders, filenames in os.walk(icons_path):
        for filename in fnmatch.filter(filenames, file_extension):
            file_path = os.path.join(foldername, filename)
            relative_path = os.path.relpath(file_path, root_folder)
            icons.append(relative_path)

    return icons

def list_block_instances(streamfield):
    def list_bound_blocks(data):
        list = []
        bound_blocks = None

        if isinstance(data, StreamValue):
            bound_blocks = data._bound_blocks
        else:
            value = getattr(data, "value", None)
            if value:
                bound_blocks = getattr(value, "bound_blocks", getattr(value, "_bound_blocks", None))

        if not bound_blocks:
            return None

        if isinstance(bound_blocks, OrderedDict):
            for key, value in bound_blocks.items():
                child_blocks = list_bound_blocks(value)
                item = {
                    "type": key,
                    "class": f"{value.block.__class__.__module__}.{value.block.__class__.__name__}",
                }
                if child_blocks:
                    item["child_blocks"] = child_blocks
                list += [item]
        else:
            for bound_block in bound_blocks:
                if bound_block:
                    item = {
                        "type": bound_block.block.name,
                        "class": f"{bound_block.block.__class__.__module__}.{bound_block.block.__class__.__name__}",
                    }
                    child_blocks = list_bound_blocks(bound_block)
                    if child_blocks:
                        item["child_blocks"] = child_blocks
                    list += [item]
        return list
    
    if streamfield.is_lazy: r = streamfield.render_as_block() # force lazy object to load
    return list_bound_blocks(streamfield)

def block_instances_by_class(streamfield, block_class):
    def find_blocks(data, block_class):
        list = []
        bound_blocks = None

        if isinstance(data, StreamValue):
            bound_blocks = data._bound_blocks
        else:
            value = getattr(data, "value", None)
            if value:
                bound_blocks = getattr(value, "bound_blocks", getattr(value, "_bound_blocks", None))

        if not bound_blocks:
            return []

        if isinstance(bound_blocks, OrderedDict):
            bound_blocks = bound_blocks.values()
    
        for bound_block in bound_blocks:
            if type(bound_block.block) is block_class: list += [bound_block]
            list += find_blocks(bound_block, block_class)
        return list

    if type(block_class)==str:
        try:
            module_name, class_name = block_class.rsplit('.', 1)
            module = importlib.import_module(module_name)
            block_class = getattr(module, class_name)().__class__
        except:
            return ['Unable to parse class path. Try passing the class object instead.']    
    if streamfield.is_lazy: r = streamfield.render_as_block() # force lazy object to load

    return find_blocks(streamfield, block_class)

def block_prepvalues_by_class(streamfield, block_class):
    def find_blocks(data, block_class):
        list = []
        bound_blocks = None
        if isinstance(data, StreamValue):
            bound_blocks = data._bound_blocks
        else:
            value = getattr(data, "value", None)
            if value:
                bound_blocks = getattr(value, "bound_blocks", getattr(value, "_bound_blocks", None))
        if not bound_blocks:
            return []
        if isinstance(bound_blocks, OrderedDict):
            bound_blocks = bound_blocks.values()
        for bound_block in bound_blocks:
            if type(bound_block.block) is block_class: list += [bound_block.get_prep_value()]
            list += find_blocks(bound_block, block_class)
        return list
    if type(block_class)==str:
        try:
            module_name, class_name = block_class.rsplit('.', 1)
            module = importlib.import_module(module_name)
            block_class = getattr(module, class_name)().__class__
        except:
            return ['Unable to parse class path. Try passing the class object instead.']    
    if streamfield.is_lazy: r = streamfield.render_as_block() # force lazy object to load
    return find_blocks(streamfield, block_class)


def list_streamfield_blocks(streamfield):
    def list_child_blocks(child_blocks):
        list = []
        for key, value in child_blocks.items():
            item = {
                "type": key,
                "class": f"{value.__class__.__module__}.{value.__class__.__name__}",
            }
            if getattr(value, 'child_blocks', False):
                item["child_blocks"] = list_child_blocks(value.child_blocks)
            elif isinstance(value, ListBlock):
                item["child_blocks"] = list_child_blocks({value.child_block.name: value.child_block})
            list += [item]
        return list
    
    return list_child_blocks(streamfield.stream_block.child_blocks)
    