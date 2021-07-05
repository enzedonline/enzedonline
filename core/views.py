import os

from django.views.generic import TemplateView

env = os.environ.copy()

class RobotsView(TemplateView):

    content_type = 'text/plain'

    def get_template_names(self):
        return 'robots.txt'