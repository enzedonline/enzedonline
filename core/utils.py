from django.core.cache import caches
from django.db import connection

def clear_page_cache():
    caches['default'].clear()    
    caches['renditions'].clear()

def purge_page_cache_fragments(slug):
    sql = f"DELETE FROM public.cache_table WHERE cache_key LIKE '%template.cache.{slug}.%';"
    with connection.cursor() as cursor:
        cursor.execute(sql)