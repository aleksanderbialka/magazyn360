from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import (
    ProductImageViewSet,
    ProductViewSet,
    StockViewSet,
    WarehouseDocumentItemViewSet,
    WarehouseDocumentViewSet,
    WarehouseViewSet,
)


router = DefaultRouter()
router.register(r"warehouses", WarehouseViewSet)
router.register(r"products", ProductViewSet)
router.register(r"stocks", StockViewSet)
router.register(r"documents", WarehouseDocumentViewSet)
router.register(r"document-items", WarehouseDocumentItemViewSet)
router.register(r"product-images", ProductImageViewSet)

urlpatterns = [
    path("", include(router.urls)),
]
