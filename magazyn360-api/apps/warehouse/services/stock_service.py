from decimal import Decimal

from django.db import transaction
from django.db.models import F, Q

from ..models import Product, Stock, Warehouse


class StockService:
    """Service for stock operations."""

    @staticmethod
    @transaction.atomic
    def adjust_stock(
        warehouse: Warehouse,
        product: Product,
        quantity_change: Decimal,
        reason: str = "",
    ) -> Stock:
        """Adjust stock level for product in warehouse."""
        stock, created = Stock.objects.get_or_create(
            warehouse=warehouse, product=product, defaults={"quantity": Decimal("0")}
        )

        new_quantity = stock.quantity + quantity_change

        if new_quantity < 0:
            raise ValueError(
                f"Insufficient stock for {product.name} in {warehouse.name}. "
                f"Current: {stock.quantity}, Required: {abs(quantity_change)}"
            )

        stock.quantity = new_quantity
        stock.save()

        return stock

    @staticmethod
    def get_low_stock_items(company_id: str | None = None) -> list[Stock]:
        """Get products with stock below minimum level."""
        queryset = Stock.objects.filter(
            Q(quantity__lt=F("product__min_stock")) & Q(product__min_stock__gt=0)
        ).select_related("warehouse", "product")

        if company_id:
            queryset = queryset.filter(warehouse__company_id=company_id)

        return list(queryset)
