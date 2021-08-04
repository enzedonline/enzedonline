from django.shortcuts import render
from django.views.generic import TemplateView
from core.models import SEOPage
from wagtail.core.models import Page
from wagtail.search.backends import get_search_backend
from wagtail.search.models import Query
from django.contrib import messages
from django.shortcuts import redirect
from django.contrib.auth.decorators import login_required
from .utils import clear_page_cache

@login_required()
def refresh_page_cache(r):
    try:
        clear_page_cache()
        messages.success(r, 'Page Cache has been refreshed!')
    except:
        messages.error(r, 'There was a problem refreshing the Page Cache' )
    return redirect('/admin/')
    
class RobotsView(TemplateView):

    content_type = 'text/plain'

    def get_template_names(self):
        return 'robots.txt'

def search(request):
    # Search
    search_query = request.GET.get('query', None)
    if search_query:
        s = get_search_backend(backend='default')
        search_results = s.search(search_query, Page.objects.live().specific().reverse())


        # Log the query so Wagtail can suggest promoted results
        Query.get(search_query).add_hit()
    else:
        search_results = Page.objects.none()

    # Render template
    return render(request, 'search/search_results.html', {
        'search_query': search_query,
        'search_results': search_results,
    })        
