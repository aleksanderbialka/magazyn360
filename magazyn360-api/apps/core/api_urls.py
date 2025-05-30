from django.urls import include, path
from rest_framework.routers import DefaultRouter

from apps.core.views import AddressViewSet, CompanyViewSet, MeView, UserViewSet

router = DefaultRouter()
router.register(r"companies", CompanyViewSet, basename="company")
router.register(r"addresses", AddressViewSet, basename="address")
router.register(r"users", UserViewSet, basename="user")

urlpatterns = [
    path("me/", MeView.as_view(), name="me"),
    path("", include(router.urls)),
]
