from django.shortcuts import render
from django.views.generic import TemplateView
from core.models import SEOPage
from wagtail.core.models import Page
from wagtail.search.backends import get_search_backend
from wagtail.search.models import Query

class RobotsView(TemplateView):

    content_type = 'text/plain'

    def get_template_names(self):
        return 'robots.txt'

def search(request):
    # Search
    search_query = request.GET.get('query', None)
    if search_query:
        s = get_search_backend()
        search_results = s.search(search_query)


        # Log the query so Wagtail can suggest promoted results
        Query.get(search_query).add_hit()
    else:
        search_results = SEOPage.objects.none()

    # Render template
    return render(request, 'search/search_results.html', {
        'search_query': search_query,
        'search_results': search_results,
    })        
