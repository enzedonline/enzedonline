from django.shortcuts import render
from wagtail.models import Site
import logging

logger = logging.getLogger(__name__)

def error_500_view(request):
    """
    Custom 500 error handler that injects the current site into the template context.
    Works for both DEBUG test pages and real server errors.
    """
    # Try to find the Wagtail Site
    site = Site.find_for_request(request)

    # Optional: log the error details for debugging
    if hasattr(request, 'exc_info'):
        logger.exception("500 error at site %s", site)
    else:
        logger.error("500 error at site %s", site)

    site_name = site.site_name if site else "enzedonline"

    context = {
        "current_site": site,
        "site_name": site_name,
        "request": request,
    }

    return render(request, "500.html", context, status=500)


def error_429_view(request, exception):
    return render(request, '429.html', status=429)