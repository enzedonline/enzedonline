from django.utils.translation import gettext_lazy as _
from wagtail.admin.ui.tables import Column, DateColumn
from wagtail.admin.views.generic.chooser import ChooseResultsViewMixin
from wagtail.documents import get_document_model_string
from wagtail.documents.views.chooser import \
    BaseDocumentChooseView as WagtailBaseDocumentChooseView
from wagtail.documents.views.chooser import \
    DocumentChooserViewSet as WagtaillDocumentChooserViewSet
from wagtail.documents.views.chooser import (DocumentChooseViewMixin,
                                             DocumentCreationFormMixin)


class BaseDocumentChooseView(WagtailBaseDocumentChooseView):
    @property
    def columns(self):
        columns = super().columns + [
            Column("filename", label=_("File")),
            DateColumn("created_at", label=_("Created"), width="16%"),
        ]

        if self.collections:
            columns.insert(2, Column("collection", label=_("Collection")))

        return columns

class DocumentChooseView(
    DocumentChooseViewMixin, DocumentCreationFormMixin, BaseDocumentChooseView
):
    pass

class DocumentChooseResultsView(
    ChooseResultsViewMixin, DocumentCreationFormMixin, BaseDocumentChooseView
):
    pass

class DocumentChooserViewSet(WagtaillDocumentChooserViewSet):
    choose_view_class = DocumentChooseView
    choose_results_view_class = DocumentChooseResultsView

viewset = DocumentChooserViewSet(
    "customdocs_chooser", # change the namespace here to avoid warning
    model=get_document_model_string(),
    url_prefix="documents/chooser",
)
