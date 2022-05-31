from django.core.cache import caches
from django.db import connection

def clear_page_cache():
    caches['default'].clear()    
    caches['renditions'].clear()

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
    """ Given a 'wing size', return a range for pagination. 
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