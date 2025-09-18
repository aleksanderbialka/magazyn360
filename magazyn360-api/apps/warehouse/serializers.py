import logging
import os

from django.core.files.images import get_image_dimensions
from django.db import transaction
from rest_framework import serializers

from .enums import DocType
from .models import (
    Product,
    ProductImage,
    Stock,
    Warehouse,
    WarehouseDocument,
    WarehouseDocumentItem,
)


logger = logging.getLogger(__name__)


class WarehouseSerializer(serializers.ModelSerializer):
    """Serializer for Warehouse model."""

    class Meta:
        model = Warehouse
        fields = [
            "id",
            "name",
            "company",
            "address",
            "is_active",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]


class ProductImageSerializer(serializers.ModelSerializer):
    """Serializer for ProductImage model."""

    image_url = serializers.SerializerMethodField()
    image_size = serializers.SerializerMethodField()
    file_size = serializers.SerializerMethodField()

    class Meta:
        model = ProductImage
        fields = [
            "id",
            "product",
            "image",
            "image_url",
            "image_size",
            "file_size",
            "alt_text",
            "is_primary",
            "order",
            "created_at",
        ]
        read_only_fields = ["id", "created_at", "image_url", "image_size", "file_size"]

    def get_image_url(self, obj):
        """Get full URL for image."""
        if obj.image:
            try:
                request = self.context.get("request")
                if request:
                    return request.build_absolute_uri(obj.image.url)
                return obj.image.url
            except (ValueError, AttributeError, FileNotFoundError, OSError) as e:
                logger.exception(
                    "Failed to build image URL for ProductImage %s: %s", obj.id, str(e)
                )
                return None
        return None

    def get_image_size(self, obj):
        """Get image dimensions."""
        if obj.image:
            try:
                width, height = get_image_dimensions(obj.image)
                return {"width": width, "height": height}
            except OSError as e:
                logger.exception(
                    "Failed to get image dimensions for ProductImage %s (file access error): %s",
                    obj.id,
                    str(e),
                )
                return None
            except (ValueError, TypeError, AttributeError) as e:
                logger.exception(
                    "Failed to get image dimensions for ProductImage %s: %s",
                    obj.id,
                    str(e),
                )
                return None
        return None

    def get_file_size(self, obj):
        """Get file size in bytes."""
        if obj.image:
            try:
                return obj.image.size
            except (OSError, AttributeError, ValueError) as e:
                logger.exception(
                    "Failed to get file size for ProductImage %s: %s", obj.id, str(e)
                )
                return None
        return None

    def validate_image(self, value):
        """Validate image file."""
        if value:
            # Check file size (5MB limit)
            if value.size > 5 * 1024 * 1024:
                logger.exception(
                    "Image file too large: %s (size: %d bytes)", value.name, value.size
                )
                raise serializers.ValidationError("Image file too large (max 5MB)")

            # Check file extension
            allowed_extensions = [".jpg", ".jpeg", ".png", ".gif", ".webp"]
            ext = os.path.splitext(value.name)[1].lower()
            if ext not in allowed_extensions:
                logger.exception("Invalid file extension: %s", ext)
                raise serializers.ValidationError(
                    f"File type not allowed. Allowed types: {', '.join(allowed_extensions)}"
                )

            # Check dimensions
            try:
                width, height = get_image_dimensions(value)
                if width > 3000 or height > 3000:
                    logger.exception("Image dimensions too large: %dx%d", width, height)
                    raise serializers.ValidationError(
                        "Image dimensions too large (max 3000x3000)"
                    )
            except Exception as e:
                logger.error(
                    "Error validating image dimensions for %s: %s", value.name, e
                )
                raise serializers.ValidationError("Invalid image file") from e

        return value


class ProductImageCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating product images."""

    class Meta:
        model = ProductImage
        fields = ["image", "alt_text", "is_primary", "order"]

    def validate_image(self, value):
        return ProductImageSerializer().validate_image(value)


class ProductImageUploadSerializer(serializers.Serializer):
    """Serializer for uploading multiple images at once."""

    images = serializers.ListField(
        child=serializers.ImageField(),
        max_length=10,
        allow_empty=False,
    )
    alt_texts = serializers.ListField(
        child=serializers.CharField(max_length=255, required=False),
        required=False,
        allow_empty=True,
    )

    def validate_images(self, value):
        """Validate each image in the list."""
        for image in value:
            ProductImageSerializer().validate_image(image)
        return value


class ProductSerializer(serializers.ModelSerializer):
    """Serializer for Product model."""

    main_image = serializers.SerializerMethodField()
    images = ProductImageSerializer(many=True, read_only=True)
    images_count = serializers.SerializerMethodField()

    class Meta:
        model = Product
        fields = [
            "id",
            "company",
            "name",
            "sku",
            "ean",
            "description",
            "unit",
            "min_stock",
            "max_stock",
            "main_image",
            "images",
            "images_count",
            "is_active",
            "created_at",
            "updated_at",
        ]
        read_only_fields = [
            "id",
            "created_at",
            "updated_at",
            "main_image",
            "images",
            "images_count",
        ]

    def get_main_image(self, obj):
        """Get primary image URL."""
        primary_image = obj.images.filter(is_primary=True).first()
        if primary_image:
            request = self.context.get("request")
            if request:
                return request.build_absolute_uri(primary_image.image.url)
            return primary_image.image.url
        return None

    def get_images_count(self, obj):
        """Get count of images."""
        return obj.images.count()


class StockSerializer(serializers.ModelSerializer):
    """Serializer for Stock model."""

    product_name = serializers.CharField(source="product.name", read_only=True)
    product_sku = serializers.CharField(source="product.sku", read_only=True)
    warehouse_name = serializers.CharField(source="warehouse.name", read_only=True)
    product_unit = serializers.CharField(source="product.unit", read_only=True)
    available = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Stock
        fields = [
            "id",
            "warehouse",
            "warehouse_name",
            "product",
            "product_unit",
            "product_name",
            "product_sku",
            "quantity",
            "reserved",
            "available",
            "updated_at",
        ]
        read_only_fields = ["id", "available", "updated_at"]

    def get_available(self, obj):
        """Calculate available stock."""
        return obj.quantity - obj.reserved


class WarehouseDocumentItemSerializer(serializers.ModelSerializer):
    """Serializer for WarehouseDocumentItem model."""

    product_name = serializers.CharField(source="product.name", read_only=True)
    product_sku = serializers.CharField(source="product.sku", read_only=True)
    total_price = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = WarehouseDocumentItem
        fields = [
            "id",
            "document",
            "product",
            "product_name",
            "product_sku",
            "quantity",
            "price",
            "total_price",
        ]
        read_only_fields = ["id", "total_price"]

    def get_total_price(self, obj):
        """Calculate total price for the item."""
        if obj.quantity and obj.price:
            return obj.quantity * obj.price
        return None


class WarehouseDocumentItemCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating document items (without document field)."""

    class Meta:
        model = WarehouseDocumentItem
        fields = [
            "product",
            "quantity",
            "price",
        ]


class WarehouseDocumentSerializer(serializers.ModelSerializer):
    """Serializer for WarehouseDocument model."""

    items = WarehouseDocumentItemSerializer(many=True, read_only=True)
    total_value = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = WarehouseDocument
        fields = [
            "id",
            "company",
            "doc_type",
            "status",
            "number",
            "warehouse",
            "from_warehouse",
            "to_warehouse",
            "date",
            "posted_at",
            "fiscal_year",
            "items",
            "total_value",
            "created_at",
            "updated_at",
        ]
        read_only_fields = [
            "id",
            "number",
            "total_value",
            "posted_at",
            "created_at",
            "updated_at",
        ]

    def get_total_value(self, obj):
        """Calculate total value of all document items."""
        total = sum(
            (item.quantity * item.price)
            for item in obj.items.all()
            if item.quantity and item.price
        )
        return total


class WarehouseDocumentCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating warehouse documents with items."""

    items = WarehouseDocumentItemCreateSerializer(many=True)

    class Meta:
        model = WarehouseDocument
        fields = [
            "company",
            "doc_type",
            "warehouse",
            "from_warehouse",
            "to_warehouse",
            "date",
            "fiscal_year",
            "items",
        ]

    def validate(self, data):
        """Validate document data based on type."""
        doc_type = data.get("doc_type")
        warehouse = data.get("warehouse")
        from_warehouse = data.get("from_warehouse")
        to_warehouse = data.get("to_warehouse")

        if doc_type == DocType.MM:  # Transfer between warehouses
            if not from_warehouse or not to_warehouse:
                raise serializers.ValidationError(
                    "Transfer documents require both from_warehouse and to_warehouse"
                )
            if from_warehouse == to_warehouse:
                raise serializers.ValidationError(
                    "Source and destination warehouses must be different"
                )
        elif doc_type in [DocType.PZ, DocType.WZ, DocType.RW, DocType.PW]:
            if not warehouse:
                raise serializers.ValidationError(
                    f"Document type {doc_type} requires warehouse field"
                )

        return data

    @transaction.atomic
    def create(self, validated_data):
        """Create document with items."""
        items_data = validated_data.pop("items")
        document = WarehouseDocument.objects.create(**validated_data)

        for item_data in items_data:
            WarehouseDocumentItem.objects.create(document=document, **item_data)

        return document


class StockMovementSerializer(serializers.Serializer):
    """Serializer for manual stock adjustments."""

    warehouse = serializers.UUIDField()
    product = serializers.UUIDField()
    quantity = serializers.DecimalField(max_digits=12, decimal_places=2)
    reason = serializers.CharField(max_length=255, required=False)

    def validate_quantity(self, value):
        """Validate quantity is not zero."""
        if value == 0:
            raise serializers.ValidationError("Quantity cannot be zero")
        return value
