from django import forms
from django.utils.functional import cached_property
from django.utils.translation import gettext_lazy as _
from wagtail.blocks import BooleanBlock, CharBlock, StructBlock
from wagtail.blocks.struct_block import StructBlockAdapter
from wagtail.documents.blocks import DocumentChooserBlock
from wagtail.telepath import register

from .choices import (AlignmentChoiceBlock, ButtonChoiceBlock,
                      DefaultChoiceBlock, TextSizeChoiceBlock)


class DocumentBlock(StructBlock):
    document = DocumentChooserBlock(
        label=_("Document")
    )
    link_label = CharBlock(
        label = _("Link Label"),
    )
    text_size = TextSizeChoiceBlock(
        label = _("Text Size"),
        default = 'p'
    )
    icon = CharBlock(
        label = _("Link Icon F.A. Code"),
        default = "far fa-file",
        required = False,
    )
    appearance = ButtonChoiceBlock(
        max_length=15,
        default='btn-primary',
        label=_("Link Appearance")
    )
    alignment = AlignmentChoiceBlock(
        default = 'center',
        label = _("Text Alignment"),
    )
    outline = BooleanBlock(
        label = _("Outline Button"),
        default = True,
        required = False
    )
    full_width = BooleanBlock(
        label = _("Full Width"),
        default = False,
        required = False
    )

    class Meta:
        template = "blocks/document_block.html"
        icon = "doc-full"
        label = _("Document Block")
        label_format = _("Document") +": {link_label}"
        form_classname = 'struct-block flex-block document-block'

class DocumentBlockAdapter(StructBlockAdapter):
    @cached_property
    def media(self):
        return forms.Media(
            css={"all": (
                "css/admin/document-block.css",
            )},
        )

register(DocumentBlockAdapter(), DocumentBlock)

class DocumentListSortChoiceBlock(DefaultChoiceBlock):
    choices = [
        ('created_at', _('Date (newest first)')), 
        ('title', _('Document Title')), 
    ]
    default = 'created_at'
    label = _("Sort Order")        

class DocumentListBlock(StructBlock):
    tag_list = CharBlock(
        label = _("Tag List"),
        help_text = _("Comma seperated list of tags to filter by. Leave blank to list all documents."),
        required = False,
    )
    text_size = TextSizeChoiceBlock(
        label = _("Text Size"),
        default = 'p'
    )
    icon = CharBlock(
        label = _("Link Icon"),
        help_text = _("Optional FontAwesome icon to appear left of the link (eg fas fa-file)"),
        required = False,
    )
    appearance = ButtonChoiceBlock(
        max_length=15,
        default='btn-link',
        label=_("Link Appearance")
    )
    outline = BooleanBlock(
        label = _("Outline button"),
        help_text = _("Blank for solid fill, checked for outline only"),
        default = False,
        required = False
    )
    full_width = BooleanBlock(
        label = _("Full width button"),
        help_text = _("Link button fills available width"),
        default = False,
        required = False
    )
    alignment = AlignmentChoiceBlock(
        default = 'center',
        label = _("Text Alignment"),
        help_text = _("Only used if full width button")
    )
    sort_by = DocumentListSortChoiceBlock()

    class Meta:
        template = "blocks/document_list_block.html"
        icon = "document-list"
        label = "Document List"
        label_format = label
        form_classname = 'struct-block flex-block document-list-block'
