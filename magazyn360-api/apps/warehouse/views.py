from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.filters import OrderingFilter, SearchFilter
from rest_framework.response import Response

from .enums import DocStatus
from .models import (
    Product,
    Stock,
    Warehouse,
    WarehouseDocument,
    WarehouseDocumentItem,
)
from .serializers import (
    ProductSerializer,
    StockMovementSerializer,
    StockSerializer,
    WarehouseDocumentCreateSerializer,
    WarehouseDocumentItemSerializer,
    WarehouseDocumentSerializer,
    WarehouseSerializer,
)
from .services.document_service import DocumentService
from .services.stock_service import StockService


class WarehouseViewSet(viewsets.ModelViewSet):
    """ViewSet for managing warehouses."""

    queryset = Warehouse.objects.all()
    serializer_class = WarehouseSerializer
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ["company", "is_active"]
    search_fields = ["name", "address__street"]
    ordering_fields = ["name", "created_at"]
    ordering = ["name"]


class ProductViewSet(viewsets.ModelViewSet):
    """ViewSet for managing products."""

    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ["company", "unit", "is_active"]
    search_fields = ["name", "sku", "ean"]
    ordering_fields = ["name", "sku", "created_at"]
    ordering = ["name"]

    @action(detail=True, methods=["get"])
    def stock_levels(self, request, pk=None):
        """Get stock levels for this product across all warehouses."""
        product = self.get_object()
        stocks = Stock.objects.filter(product=product).select_related("warehouse")
        serializer = StockSerializer(stocks, many=True)
        return Response(serializer.data)


class StockViewSet(viewsets.ModelViewSet):
    """ViewSet for managing stock levels."""

    queryset = Stock.objects.select_related("warehouse", "product")
    serializer_class = StockSerializer
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ["warehouse", "product"]
    search_fields = ["product__name", "product__sku", "warehouse__name"]
    ordering_fields = ["quantity", "updated_at"]
    ordering = ["warehouse__name", "product__name"]

    @action(detail=False, methods=["get"])
    def low_stock(self, request):
        """Get products with stock below minimum level."""
        company_id = request.query_params.get("company")
        low_stock_items = StockService.get_low_stock_items(company_id)
        serializer = self.get_serializer(low_stock_items, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=["post"])
    def adjust_stock(self, request):
        """Manual stock adjustment."""
        serializer = StockMovementSerializer(data=request.data)
        if serializer.is_valid():
            try:
                warehouse = Warehouse.objects.get(
                    id=serializer.validated_data["warehouse"]
                )
                product = Product.objects.get(id=serializer.validated_data["product"])
                quantity = serializer.validated_data["quantity"]
                reason = serializer.validated_data.get("reason", "Manual adjustment")

                stock = StockService.adjust_stock(
                    warehouse=warehouse,
                    product=product,
                    quantity_change=quantity,
                    reason=reason,
                )

                response_serializer = StockSerializer(stock)
                return Response(response_serializer.data)

            except (Warehouse.DoesNotExist, Product.DoesNotExist):
                return Response(
                    {"error": "Warehouse or Product not found"},
                    status=status.HTTP_404_NOT_FOUND,
                )
            except ValueError as e:
                return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class WarehouseDocumentViewSet(viewsets.ModelViewSet):
    """ViewSet for managing warehouse documents."""

    queryset = WarehouseDocument.objects.prefetch_related("items__product")
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ["company", "doc_type", "status", "warehouse"]
    search_fields = ["number"]
    ordering_fields = ["date", "created_at"]
    ordering = ["-date", "-created_at"]

    def get_serializer_class(self):
        """Return appropriate serializer based on action."""
        if self.action == "create":
            return WarehouseDocumentCreateSerializer
        return WarehouseDocumentSerializer

    @action(detail=True, methods=["post"])
    def post_document(self, request, pk=None):
        """Post (finalize) the document and update stock levels."""
        document = self.get_object()

        if document.status == DocStatus.POSTED:
            return Response(
                {"error": "Document is already posted"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            DocumentService.post_document(document, posted_by=request.user)
            serializer = self.get_serializer(document)
            return Response(serializer.data)
        except ValueError as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=["get"])
    def summary(self, request):
        """Get summary statistics for documents."""
        company_id = request.query_params.get("company")
        summary = DocumentService.get_document_summary(company_id)
        return Response(summary)


class WarehouseDocumentItemViewSet(viewsets.ModelViewSet):
    """ViewSet for managing document items."""

    queryset = WarehouseDocumentItem.objects.select_related("document", "product")
    serializer_class = WarehouseDocumentItemSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ["document", "product"]
