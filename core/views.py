from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render
from django.utils.translation import gettext_lazy as _
from django.views.generic import TemplateView
from wagtail.models import Page
from wagtail.search.backends import get_search_backend
from wagtail.search.models import Query
from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator

from .utils import clear_page_cache, paginator_range


@login_required()
def refresh_page_cache(r):
    try:
        clear_page_cache()
        messages.success(r, _('Page Cache has been refreshed!'))
    except:
        messages.error(r, _('There was a problem refreshing the Page Cache'))
    return redirect('/admin/')
    
class RobotsView(TemplateView):

    content_type = 'text/plain'

    def get_template_names(self):
        return 'robots.txt'

def search(request):
    # Search
    search_query = request.GET.get('query', None)
    order_by = request.GET.get('order', None)
    if search_query:
        s = get_search_backend(backend='default')

        if order_by == 'date':
            search_results = s.search(search_query, Page.objects.live().order_by('last_published_at').reverse().specific(), order_by_relevance=False) 
        else:            
            search_results = s.search(search_query, Page.objects.live().specific())
            order_by = None
        
        # Log the query so Wagtail can suggest promoted results
        Query.get(search_query).add_hit()

        paginator = Paginator(search_results, 8)
        requested_page = request.GET.get("page")

        try:
            search_results = paginator.page(requested_page)
        except PageNotAnInteger:
            search_results = paginator.page(1)
        except EmptyPage:
            search_results = paginator.page(paginator.num_pages)
        
        page_range = paginator_range(
            requested_page=search_results.number,
            last_page_num=paginator.num_pages,
            wing_size=4
        )
        # Next two are needed as Django templates don't support accessing range properties
        page_range_first = page_range[0]
        page_range_last = page_range[-1]
        
        # Render template
        return render(request, 'search/search_results.html', {
            'search_query': search_query,
            'query_string': '?query=' + search_query,
            'search_results': search_results,
            'order': order_by,
            'page_range': page_range,
            'page_range_first': page_range_first,
            'page_range_last': page_range_last,
        })        
    else:
        # Render template
        return render(request, 'search/search_results.html', {
            'search_query': '',
            'query_string': '',
            'search_results': Page.objects.none(),
        })        


