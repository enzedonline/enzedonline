from django.http import HttpResponsePermanentRedirect
from wagtail.models import Page


class MapIndexPage(Page):
    max_count = 1
    parent_page_types = ["goneforawander.GFWHomePage"]
    subpage_types = ['goneforawander.TrackPlannerPage']
    search_engine_index = False
    def serve(self, request):
        first_child = self.get_children().live().first()
        if first_child:
            return HttpResponsePermanentRedirect(first_child.url)
        return super().serve(request)