from core.utils import paginator_range
from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator
from django.template.response import TemplateResponse
from wagtail.models import Locale, Page, Site
from wagtail.search.backends import get_search_backend
from wagtail.contrib.search_promotions.models import Query


def enzed_search(request):
    search_query = request.GET.get('query', None)
    search_order = request.GET.get('order', None)
    try:
        page = int(request.GET.get('page', 1))
    except:
        page = 1
    
    # Search
    # These 2 lines commented until multi-index backend supported - one backend per locale
    # backend = 'default' if Locale.get_active()==Locale.get_default() else Locale.get_active().language_code
    # s = get_search_backend(backend)
    s = get_search_backend()

    # Resolve current site (works with/without SiteMiddleware)
    site = getattr(request, "site", None) or Site.find_for_request(request)
    # Base scope: live pages, deferred streamfields, limited to current site
    base_scope = Page.objects.live().defer_streamfields()
    if site:
        base_scope = base_scope.descendant_of(site.root_page, inclusive=True)
    
    if search_query:
        if search_order=='date':
            scope = base_scope.order_by('-first_published_at')
            search_results = s.search(search_query, scope, order_by_relevance=False)
        else:
            scope = base_scope
            search_results = s.search(search_query, scope, order_by_relevance=True)
            
        # Record hit
        query = Query.get(search_query)
        query.add_hit()

    else:
        search_results = Page.objects.none()

    # Pagination
    paginator = Paginator(search_results, 12)
    try:
        search_results = paginator.page(page)
    except PageNotAnInteger:
        search_results = paginator.page(1)
    except EmptyPage:
        search_results = paginator.page(paginator.num_pages)

    context={}
    context["search_query"] = search_query
    context['search_results'] = search_results
    context['search_order'] = search_order
    context['page_range'] = paginator_range(
        requested_page=page,
        last_page_num=paginator.num_pages,
        wing_size=4
    )
    # Next two are needed as Django templates don't support accessing range properties
    context['page_range_first'] = context['page_range'][0]
    context['page_range_last'] = context['page_range'][-1]

    return TemplateResponse(request, 'search/search_results.html', context)
