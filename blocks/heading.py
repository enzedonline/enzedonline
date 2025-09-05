import unidecode
import validators
from django import forms
from django.forms.utils import ErrorList
from django.utils.functional import cached_property
from django.utils.text import slugify
from django.utils.translation import gettext_lazy as _
from wagtail.blocks import CharBlock, StructBlock
from wagtail.blocks.struct_block import (StructBlockAdapter,
                                         StructBlockValidationError)
from wagtail.admin.telepath import register

from .choices import HeadingSizeChoiceBlock, TextAlignmentChoiceBlock


class HeadingBlock(StructBlock):
    title = CharBlock(label=_("Heading"), required=True)
    heading_size = HeadingSizeChoiceBlock(label=_("Size"), default='h2')
    alignment = TextAlignmentChoiceBlock(label=_("Alignment"), default='start')
    bookmark = CharBlock(
        required=False,
        label=_("Optional Anchor ID"),
    )
    
    class Meta:
        template = 'blocks/heading_block.html'
        label = _("Heading Block")
        label_format = _("Heading") + ": {title}"
        icon = 'title'
        form_classname = "struct-block flex-block heading-block"

    def clean(self, value):
        errors = {}
        anchor_id = value.get('anchor_id')
        if anchor_id:
            if not validators.slug(anchor_id):
                slug = slugify(unidecode.unidecode(anchor_id)) or slugify(
                    unidecode.unidecode(value.get('title')))
                errors['anchor_id'] = ErrorList([_(f"\
                    '{anchor_id}' is not a valid slug for the anchor identifier. \
                    '{slug}' is the suggested value for this.")])
                raise StructBlockValidationError(block_errors=errors)

        return super().clean(value)

class HeadingBlockAdapter(StructBlockAdapter):        
    @cached_property
    def media(self):
        return forms.Media(
            css={"all": (
                "css/admin/heading-block.css",
            )},
        )

register(HeadingBlockAdapter(), HeadingBlock)