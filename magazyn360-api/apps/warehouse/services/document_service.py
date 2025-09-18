from decimal import Decimal

from django.db import transaction
from django.utils import timezone

from ..enums import DocStatus, DocType
from ..models import WarehouseDocument
from .stock_service import StockService


class DocumentService:
    """Service for warehouse document operations."""

    @staticmethod
    @transaction.atomic
    def post_document(document: WarehouseDocument, posted_by=None) -> WarehouseDocument:
        """Post (finalize) document and update stock levels."""
        DocumentService._validate_document_for_posting(document)

        for item in document.items.select_related("product"):
            DocumentService._process_document_item(document, item)

        document.status = DocStatus.POSTED
        document.posted_at = timezone.now()
        if posted_by:
            document.posted_by = posted_by
        document.save()

        return document

    @staticmethod
    def _validate_document_for_posting(document: WarehouseDocument):
        """Validate document before posting."""
        if document.status == DocStatus.POSTED:
            raise ValueError("Document is already posted")

        if not document.items.exists():
            raise ValueError("Cannot post document without items")

    @staticmethod
    def _process_document_item(document: WarehouseDocument, item):
        """Process single document item based on document type."""
        if document.doc_type == DocType.MM:
            DocumentService._handle_transfer(document, item)
        else:
            DocumentService._handle_single_warehouse_operation(document, item)

    @staticmethod
    def _handle_single_warehouse_operation(document: WarehouseDocument, item):
        """Handle operations within single warehouse."""
        warehouse = document.warehouse
        quantity_change = DocumentService._get_quantity_change(
            document.doc_type, item.quantity
        )

        StockService.adjust_stock(
            warehouse=warehouse,
            product=item.product,
            quantity_change=quantity_change,
            reason=f"Document {document.number}",
        )

    @staticmethod
    def _handle_transfer(document: WarehouseDocument, item):
        """Handle stock transfer between warehouses."""
        StockService.adjust_stock(
            warehouse=document.from_warehouse,
            product=item.product,
            quantity_change=-item.quantity,
            reason=f"Transfer out - {document.number}",
        )

        StockService.adjust_stock(
            warehouse=document.to_warehouse,
            product=item.product,
            quantity_change=item.quantity,
            reason=f"Transfer in - {document.number}",
        )

    @staticmethod
    def _get_quantity_change(doc_type: DocType, quantity: Decimal) -> Decimal:
        """Get quantity change based on document type."""
        if doc_type in [DocType.PZ, DocType.PW]:
            return quantity
        elif doc_type in [DocType.WZ, DocType.RW]:
            return -quantity
        else:
            return Decimal("0")

    @staticmethod
    def get_document_summary(company_id: str | None = None) -> dict:
        """Get document summary statistics."""
        queryset = WarehouseDocument.objects.all()

        if company_id:
            queryset = queryset.filter(company_id=company_id)

        summary = {
            "total_documents": queryset.count(),
            "draft_documents": queryset.filter(status=DocStatus.DRAFT).count(),
            "posted_documents": queryset.filter(status=DocStatus.POSTED).count(),
            "by_type": {},
        }

        for doc_type, _ in DocType.choices:
            summary["by_type"][doc_type] = queryset.filter(doc_type=doc_type).count()

        return summary
