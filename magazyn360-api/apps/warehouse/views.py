from django.db import transaction
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.filters import OrderingFilter, SearchFilter
from rest_framework.parsers import FormParser, MultiPartParser
from rest_framework.response import Response

from .enums import DocStatus
from .models import (
    Product,
    ProductImage,
    Stock,
    Warehouse,
    WarehouseDocument,
    WarehouseDocumentItem,
)
from .serializers import (
    ProductImageCreateSerializer,
    ProductImageSerializer,
    ProductImageUploadSerializer,
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

    queryset = Product.objects.prefetch_related("images")
    serializer_class = ProductSerializer
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ["company", "unit", "is_active"]
    search_fields = ["name", "sku", "ean"]
    ordering_fields = ["name", "sku", "created_at"]
    ordering = ["name"]

    def get_queryset(self):
        """Filter products by user's company."""
        user = self.request.user
        if user.is_superuser:
            return Product.objects.prefetch_related("images")
        if user.company:
            return Product.objects.filter(company=user.company).prefetch_related(
                "images"
            )
        return Product.objects.none()

    def perform_create(self, serializer):
        """Set company when creating product."""
        if not self.request.user.is_superuser:
            serializer.save(company=self.request.user.company)
        else:
            serializer.save()

    @action(detail=True, methods=["get"])
    def stock_levels(self, request, pk=None):
        """Get stock levels for this product across all warehouses."""
        product = self.get_object()

        if request.user.is_superuser:
            stocks = Stock.objects.filter(product=product).select_related("warehouse")
        else:
            stocks = Stock.objects.filter(
                product=product, warehouse__company=request.user.company
            ).select_related("warehouse")

        serializer = StockSerializer(stocks, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=["get"], url_path="images")
    def get_images(self, request, pk=None):
        """Get all images for a product."""
        product = self.get_object()
        images = product.images.all().order_by("order", "created_at")

        serializer = ProductImageSerializer(
            images, many=True, context={"request": request}
        )

        return Response({"count": images.count(), "images": serializer.data})

    @action(
        detail=True,
        methods=["post"],
        parser_classes=[MultiPartParser, FormParser],
        url_path="images/upload",
    )
    def upload_images(self, request, pk=None):
        """Upload multiple images for a product."""
        product = self.get_object()

        serializer = ProductImageUploadSerializer(data=request.data)
        if serializer.is_valid():
            images = serializer.validated_data["images"]
            alt_texts = serializer.validated_data.get("alt_texts", [])

            created_images = []

            with transaction.atomic():
                for i, image in enumerate(images):
                    product_image = ProductImage.objects.create(
                        product=product,
                        image=image,
                        alt_text=alt_texts[i]
                        if i < len(alt_texts)
                        else f"Image {i + 1}",
                    )
                    created_images.append(product_image)

            response_serializer = ProductImageSerializer(
                created_images, many=True, context={"request": request}
            )

            return Response(
                {
                    "message": f"Successfully uploaded {len(created_images)} images",
                    "images": response_serializer.data,
                },
                status=status.HTTP_201_CREATED,
            )

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(
        detail=True,
        methods=["post"],
        parser_classes=[MultiPartParser, FormParser],
        url_path="images/single",
    )
    def upload_single_image(self, request, pk=None):
        """Upload a single image."""
        product = self.get_object()

        serializer = ProductImageCreateSerializer(data=request.data)
        if serializer.is_valid():
            product_image = serializer.save(product=product)

            response_serializer = ProductImageSerializer(
                product_image, context={"request": request}
            )

            return Response(
                {
                    "message": "Image uploaded successfully",
                    "image": response_serializer.data,
                },
                status=status.HTTP_201_CREATED,
            )

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=["delete"], url_path="images/clear")
    def clear_images(self, request, pk=None):
        """Delete all images for a product."""
        product = self.get_object()

        deleted_count = 0
        for image in product.images.all():
            image.delete()
            deleted_count += 1

        return Response({"message": f"Successfully deleted {deleted_count} images"})


class ProductImageViewSet(viewsets.ModelViewSet):
    """ViewSet for managing individual product images."""

    queryset = ProductImage.objects.select_related("product")
    serializer_class = ProductImageSerializer
    parser_classes = [MultiPartParser, FormParser]

    def get_queryset(self):
        """Filter images by user's company."""
        user = self.request.user
        if user.is_superuser:
            return ProductImage.objects.select_related("product")
        if user.company:
            return ProductImage.objects.filter(
                product__company=user.company
            ).select_related("product")
        return ProductImage.objects.none()

    @action(detail=True, methods=["post"])
    def set_primary(self, request, pk=None):
        """Set this image as primary for the product."""
        image = self.get_object()

        with transaction.atomic():
            ProductImage.objects.filter(product=image.product).update(is_primary=False)

            image.is_primary = True
            image.save()

        serializer = self.get_serializer(image)
        return Response({"message": "Image set as primary", "image": serializer.data})

    @action(detail=True, methods=["patch"])
    def reorder(self, request, pk=None):
        """Change image order."""
        image = self.get_object()
        new_order = request.data.get("order")

        if new_order is None:
            return Response(
                {"error": "Order parameter is required"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            new_order = int(new_order)
            if new_order < 0:
                raise ValueError()
        except (ValueError, TypeError):
            return Response(
                {"error": "Order must be a non-negative integer"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        with transaction.atomic():
            image.order = new_order
            image.save()

        serializer = self.get_serializer(image)
        return Response({"message": "Image order updated", "image": serializer.data})

    def destroy(self, request, *args, **kwargs):
        """Delete image with proper file cleanup."""
        instance = self.get_object()

        self.perform_destroy(instance)

        return Response(
            {"message": "Image deleted successfully"}, status=status.HTTP_204_NO_CONTENT
        )


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
