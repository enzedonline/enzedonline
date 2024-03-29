from django.utils.translation import gettext_lazy as _
from wagtail.blocks import RawHTMLBlock, StructBlock

class DjangoTemplateFragmentBlock(StructBlock):
    code = RawHTMLBlock(
        label=_("Enter Django Template Fragment Code")
    )
    class Meta:
        template='blocks/django_code_block.html'
        icon = 'laptop-code'
        label = _("Raw Django HTML")
        label_format = label

class SocialMediaEmbedBlock(StructBlock):
    embed_code = RawHTMLBlock(
        label=_("Paste Embed code block from Provider"),
        help_text=_("Paste in only embed code. For Facebook, only Step 2 on the JavaScript SDK tab")
    )
    class Meta:
        template='blocks/social_media_embed.html'
        icon = 'social-media'
        label = _("Social Media Post")
        label_format = label
