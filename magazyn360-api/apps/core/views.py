from rest_framework.generics import RetrieveAPIView
from rest_framework.permissions import DjangoModelPermissions, IsAuthenticated
from rest_framework.viewsets import ModelViewSet

from apps.core.models import Address, Company, CustomUser
from apps.core.permissions import IsInUserCompany
from apps.core.serializers import (
    AddressSerializer,
    CompanySerializer,
    UserCreateUpdateSerializer,
    UserListSerializer,
)


class MeView(RetrieveAPIView):
    serializer_class = UserListSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        return self.request.user


class CompanyViewSet(ModelViewSet):
    queryset = Company.objects.all()
    serializer_class = CompanySerializer
    permission_classes = [IsAuthenticated, DjangoModelPermissions, IsInUserCompany]

    def get_queryset(self):
        user = self.request.user
        if user.is_superuser:
            return Company.objects.all()
        if user.company:
            return Company.objects.filter(id=user.company_id)
        return Company.objects.none()

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)


class AddressViewSet(ModelViewSet):
    queryset = Address.objects.all()
    serializer_class = AddressSerializer
    permission_classes = [IsAuthenticated, DjangoModelPermissions, IsInUserCompany]

    def get_queryset(self):
        user = self.request.user
        if user.is_superuser:
            return Address.objects.all()
        if user.company:
            return Address.objects.filter(company=user.company)
        return Address.objects.none()

    def perform_create(self, serializer):
        serializer.save(company=self.request.user.company)


class UserViewSet(ModelViewSet):
    queryset = CustomUser.objects.all()
    permission_classes = [IsAuthenticated, DjangoModelPermissions, IsInUserCompany]

    def get_queryset(self):
        user = self.request.user
        if user.is_superuser:
            return CustomUser.objects.all()
        return CustomUser.objects.filter(company=user.company)

    def get_serializer_class(self):
        if self.action in ["list", "retrieve"]:
            return UserListSerializer
        return UserCreateUpdateSerializer

    def perform_create(self, serializer):
        serializer.save(company=self.request.user.company)
