from django.urls import path

from apps.core.views import MeView

urlpatterns = [
    path("me/", MeView.as_view(), name="me"),
]
