from django import template
from django.utils.safestring import mark_safe
from wagtail.models import Locale

from site_settings.models import SocialMedia, CompanyLogo

register = template.Library()

@register.simple_tag()
def get_google_thumbnails(img):
    return {
        'tn1x1': img.get_rendition('thumbnail-500x500|format-png'),
        'tn4x3': img.get_rendition('thumbnail-500x375|format-png'),
        'tn16x9': img.get_rendition('thumbnail-500x281|format-png'),
    }
    
@register.simple_tag()
def get_social_media_sameas():
    same_as = []
    for sm in SocialMedia.objects.all().filter(locale_id=Locale.get_active().id):
        same_as.append(f'"{sm.url}"')
    return mark_safe(','.join(same_as))

@register.simple_tag()
def get_organisation_logo():
    try:
        company_logo_instance = CompanyLogo.objects.filter(name='organisation').first()
        if company_logo_instance and hasattr(company_logo_instance, 'localized'):
            company_logo = getattr(company_logo_instance.localized, 'logo', company_logo_instance.logo)
            if company_logo:
                return company_logo.get_rendition('thumbnail-500x500|format-png').full_url
    except (AttributeError, CompanyLogo.DoesNotExist):
        pass
    return ''