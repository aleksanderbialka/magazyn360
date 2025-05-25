from rest_framework.generics import RetrieveAPIView
from rest_framework.permissions import DjangoModelPermissions, IsAuthenticated
from rest_framework.viewsets import ModelViewSet

from apps.core.models import Company
from apps.core.serializers import CompanySerializer, UserSerializer


class MeView(RetrieveAPIView):
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        return self.request.user


class CompanyViewSet(ModelViewSet):
    queryset = Company.objects.all()
    serializer_class = CompanySerializer
    permission_classes = [IsAuthenticated, DjangoModelPermissions]

    def get_queryset(self):
        user = self.request.user
        if user.is_superuser:
            return Company.objects.all()
        if user.company:
            return Company.objects.filter(id=user.company_id)
        return Company.objects.none()

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)
