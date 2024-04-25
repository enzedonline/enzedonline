from django.views.generic import TemplateView
from site_settings.models import EmailSignature
from wagtail.images.models import Image
   

class TestContactReceiptView(TemplateView):
    template_name = 'contact/receipt-email.html' 

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['body'] = {'receipt_email_headline': 'Thank you for contacting Enzed Online', 'receipt_email_content': '<p>Your message is important to me, I will endeavour to respond at the first available opportunity.</p><p>Regards,<br>Richard @ Enzed Online</p>'}
        context['heading_image'] = Image.objects.get(id=48)
        context['footer'] = EmailSignature.objects.first()
        context['base_url'] = 'localhost:8000'
        return context