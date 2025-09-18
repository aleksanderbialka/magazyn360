import uuid
from decimal import Decimal

from django.db import models
from django.db.models import F, Q
from django.utils.translation import gettext_lazy as _

from .enums import DocStatus, DocType, Unit


class Warehouse(models.Model):
    """Model representing a warehouse in the system.

    Attributes:
        id: UUID primary key
        name: Name of the warehouse
        address: Address of the warehouse
        capacity: Maximum storage capacity in cubic meters
        is_active: Whether the warehouse is currently active
    """

    id: models.UUIDField = models.UUIDField(
        primary_key=True, default=uuid.uuid4, editable=False
    )
    name: models.CharField = models.CharField(max_length=255)
    company: models.ForeignKey = models.ForeignKey(
        "core.Company",
        on_delete=models.CASCADE,
        related_name="warehouses",
        verbose_name=_("Company"),
    )
    address: models.ForeignKey = models.ForeignKey(
        "core.Address",
        on_delete=models.PROTECT,
        related_name="warehouses",
        verbose_name=_("Address"),
    )
    is_active: models.BooleanField = models.BooleanField(default=True)
    created_at: models.DateTimeField = models.DateTimeField(auto_now_add=True)
    updated_at: models.DateTimeField = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name: str = _("Warehouse")
        verbose_name_plural: str = _("Warehouses")
        indexes: list[models.Index] = [
            models.Index(fields=["company", "name"]),
            models.Index(fields=["is_active"]),
        ]
        ordering: list[str] = ["name"]

    def __str__(self) -> str:
        return self.name


class Product(models.Model):
    """Model representing a product or good."""

    id: models.UUIDField = models.UUIDField(
        primary_key=True, default=uuid.uuid4, editable=False
    )
    company: models.ForeignKey = models.ForeignKey(
        "core.Company",
        on_delete=models.CASCADE,
        related_name="products",
        verbose_name=_("Company"),
    )
    name: models.CharField = models.CharField(max_length=255)
    sku: models.CharField = models.CharField(max_length=64)
    ean: models.CharField = models.CharField(
        max_length=13, blank=True, default="", db_index=True
    )
    unit = models.CharField(max_length=16, choices=Unit.choices, default=Unit.PCS)
    is_active: models.BooleanField = models.BooleanField(default=True)
    min_stock: models.DecimalField = models.DecimalField(
        max_digits=12, decimal_places=2, default=Decimal("0.00")
    )
    max_stock: models.DecimalField = models.DecimalField(
        max_digits=12, decimal_places=2, default=Decimal("0.00")
    )
    created_at: models.DateTimeField = models.DateTimeField(auto_now_add=True)
    updated_at: models.DateTimeField = models.DateTimeField(auto_now=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["company", "sku"], name="uniq_product_sku_per_company"
            ),
            models.CheckConstraint(
                check=Q(min_stock__gte=0), name="product_min_stock_non_negative"
            ),
            models.CheckConstraint(
                check=Q(max_stock__gte=0), name="product_max_stock_non_negative"
            ),
        ]
        indexes: list[models.Index] = [
            models.Index(fields=["company", "name"]),
            models.Index(fields=["company", "sku"]),
            models.Index(fields=["is_active"]),
        ]
        ordering: list[str] = ["company_id", "name"]

    def __str__(self) -> str:
        return f"{self.name} [{self.sku}]"


class Stock(models.Model):
    """Stock level of a product in a warehouse."""

    id: models.UUIDField = models.UUIDField(
        primary_key=True, default=uuid.uuid4, editable=False
    )
    warehouse: models.ForeignKey = models.ForeignKey(
        Warehouse, on_delete=models.CASCADE, related_name="stocks"
    )
    product: models.ForeignKey = models.ForeignKey(
        Product, on_delete=models.CASCADE, related_name="stocks"
    )
    quantity: models.DecimalField = models.DecimalField(
        max_digits=12, decimal_places=2, default=Decimal("0.00")
    )
    reserved: models.DecimalField = models.DecimalField(
        max_digits=12, decimal_places=2, default=Decimal("0.00")
    )
    updated_at: models.DateTimeField = models.DateTimeField(auto_now=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["warehouse", "product"], name="uniq_stock_per_warehouse_product"
            ),
            models.CheckConstraint(
                check=Q(quantity__gte=0), name="stock_quantity_non_negative"
            ),
            models.CheckConstraint(
                check=Q(reserved__gte=0), name="stock_reserved_non_negative"
            ),
        ]
        indexes = [
            models.Index(fields=["warehouse", "product"]),
        ]

    def __str__(self) -> str:
        return f"{self.product} @ {self.warehouse}: {self.quantity}"

    @property
    def available(self) -> Decimal:
        return (self.quantity or Decimal("0")) - (self.reserved or Decimal("0"))


class WarehouseDocument(models.Model):
    """Warehouse document (PZ, WZ, MM, RW, PW, etc.).
    For MM we track the source and destination warehouses."""

    id: models.UUIDField = models.UUIDField(
        primary_key=True, default=uuid.uuid4, editable=False
    )
    company: models.ForeignKey = models.ForeignKey(
        "core.Company", on_delete=models.PROTECT, related_name="warehouse_documents"
    )
    doc_type: models.CharField = models.CharField(max_length=2, choices=DocType.choices)
    status: models.CharField = models.CharField(
        max_length=16, choices=DocStatus.choices, default=DocStatus.DRAFT
    )
    number: models.CharField = models.CharField(max_length=64)
    warehouse: models.ForeignKey = models.ForeignKey(
        Warehouse,
        on_delete=models.PROTECT,
        related_name="documents",
        null=True,
        blank=True,
    )
    from_warehouse: models.ForeignKey = models.ForeignKey(
        Warehouse,
        on_delete=models.PROTECT,
        related_name="outgoing_transfers",
        null=True,
        blank=True,
    )
    to_warehouse: models.ForeignKey = models.ForeignKey(
        Warehouse,
        on_delete=models.PROTECT,
        related_name="incoming_transfers",
        null=True,
        blank=True,
    )
    date: models.DateField = models.DateField(db_index=True)
    posted_at: models.DateTimeField = models.DateTimeField(null=True, blank=True)
    created_at: models.DateTimeField = models.DateTimeField(auto_now_add=True)
    updated_at: models.DateTimeField = models.DateTimeField(auto_now=True)

    fiscal_year = models.PositiveIntegerField()  # simple key for numbering

    posted_by = models.ForeignKey(
        "core.CustomUser",
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name="posted_documents",
    )

    class Meta:
        constraints = [
            # numbering e.g. unique within company, type and year
            models.UniqueConstraint(
                fields=["company", "doc_type", "fiscal_year", "number"],
                name="uniq_document_number_per_company_type_year",
            ),
            # MM consistency: both warehouses must be set and different
            models.CheckConstraint(
                check=Q(
                    doc_type=DocType.MM,
                    from_warehouse__isnull=False,
                    to_warehouse__isnull=False,
                )
                | ~Q(doc_type=DocType.MM),
                name="doc_mm_requires_from_and_to",
            ),
            models.CheckConstraint(
                check=Q(doc_type=DocType.MM, from_warehouse__isnull=False)
                & ~Q(from_warehouse=F("to_warehouse"))
                | ~Q(doc_type=DocType.MM),
                name="doc_mm_from_to_must_differ",
            ),
        ]
        indexes = [
            models.Index(fields=["company", "doc_type", "date"]),
            models.Index(fields=["status"]),
        ]
        ordering = ["-date", "-created_at"]

    def __str__(self) -> str:
        return f"{self.doc_type} {self.number} ({self.date})"


class WarehouseDocumentItem(models.Model):
    """Item/position in a warehouse document."""

    id: models.UUIDField = models.UUIDField(
        primary_key=True, default=uuid.uuid4, editable=False
    )
    document: models.ForeignKey = models.ForeignKey(
        WarehouseDocument, on_delete=models.CASCADE, related_name="items"
    )
    product: models.ForeignKey = models.ForeignKey(Product, on_delete=models.PROTECT)
    quantity: models.DecimalField = models.DecimalField(max_digits=16, decimal_places=2)
    unit: models.CharField = models.CharField(
        max_length=16, choices=Unit.choices, default=Unit.PCS
    )
    price: models.DecimalField = models.DecimalField(
        max_digits=16, decimal_places=2, null=True, blank=True
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["document", "product"], name="uniq_item_per_document_product"
            ),
            models.CheckConstraint(
                check=Q(quantity__gt=0), name="doc_item_quantity_positive"
            ),
            models.CheckConstraint(
                check=Q(price__isnull=True) | Q(price__gte=0),
                name="doc_item_price_non_negative",
            ),
        ]
        indexes = [
            models.Index(fields=["document"]),
            models.Index(fields=["product"]),
        ]

    def __str__(self) -> str:
        return f"{self.product} x {self.quantity} {self.unit}"
