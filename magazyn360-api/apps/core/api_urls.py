from django.urls import include, path
from rest_framework.routers import DefaultRouter

from apps.core.views import CompanyViewSet, MeView

router = DefaultRouter()
router.register(r"companies", CompanyViewSet, basename="company")

urlpatterns = [
    path("me/", MeView.as_view(), name="me"),
    path("", include(router.urls)),
]
