from django.views.generic import TemplateView
from wagtail.images.models import Image
from wagtail.models import Site

from site_settings.models import Brand, EmailSignature


class TestContactReceiptView(TemplateView):
    template_name = 'contact/receipt-email.html' 

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        site = Site.find_for_request(self.request)
        context['body'] = {'receipt_email_headline': f'Thank you for contacting {site.hostname}', 'receipt_email_content': '<p>Your message is important to me, I will endeavour to respond at the first available opportunity.</p><p>Regards,<br>Richard @ Enzed Online</p>'}
        brand = Brand.for_request(self.request)
        context['heading_image'] = brand.banner
        context['footer'] = EmailSignature.objects.first()
        context['base_url'] = f'{site.root_url}/'
        return context