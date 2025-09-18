from django.db import transaction
from rest_framework import serializers

from .enums import DocType
from .models import (
    Product,
    Stock,
    Warehouse,
    WarehouseDocument,
    WarehouseDocumentItem,
)


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


class ProductSerializer(serializers.ModelSerializer):
    """Serializer for Product model."""

    class Meta:
        model = Product
        fields = [
            "id",
            "company",
            "name",
            "sku",
            "ean",
            "unit",
            "is_active",
            "min_stock",
            "max_stock",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]


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
