from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator
from django.template.response import TemplateResponse

from wagtail.models import Page, Locale
from wagtail.search.models import Query


def enzed_search(request):
    search_query = request.GET.get('query', None)
    search_order = request.GET.get('order', None)
    page = request.GET.get('page', 1)
    
    # Search
    if search_query:
        if search_order=='date':
            search_results = Page.objects.live().filter(locale=Locale.get_active()).reverse().search(search_query, order_by_relevance=False)
        else:
            search_results = Page.objects.live().filter(locale=Locale.get_active()).search(search_query)
            
        # Record hit
        query = Query.get(search_query)
        query.add_hit()

    else:
        search_results = Page.objects.none()

    # Pagination
    paginator = Paginator(search_results, 10)
    try:
        search_results = paginator.page(page)
    except PageNotAnInteger:
        search_results = paginator.page(1)
    except EmptyPage:
        search_results = paginator.page(paginator.num_pages)

    return TemplateResponse(request, 'search/search_results.html', {
        'search_query': search_query,
        'search_results': search_results,
        'search_order': search_order
    })
