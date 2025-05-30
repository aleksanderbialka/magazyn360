from rest_framework import serializers

from apps.core.models import Address, Company, CustomUser


class UserListSerializer(serializers.ModelSerializer):
    company_name = serializers.SerializerMethodField()

    class Meta:
        model = CustomUser
        fields = (
            "id",
            "username",
            "email",
            "first_name",
            "last_name",
            "role",
            "company_name",
            "position",
            "department",
        )

    def get_company_name(self, obj):
        return obj.company.name if obj.company else None


class UserCreateUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = (
            "username",
            "email",
            "first_name",
            "last_name",
            "role",
            "position",
            "department",
            "password",
        )
        extra_kwargs = {"password": {"write_only": True}}

    def create(self, validated_data):
        password = validated_data.pop("password")
        user = CustomUser(**validated_data)
        user.set_password(password)
        user.save()
        user.sync_group_with_role()
        return user

    def update(self, instance, validated_data):
        password = validated_data.pop("password", None)
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        if password:
            instance.set_password(password)
        instance.save()
        instance.sync_group_with_role()
        return instance


class CompanySerializer(serializers.ModelSerializer):
    class Meta:
        model = Company
        fields = [
            "id",
            "name",
            "tax_id",
            "statistical_number",
            "national_court_register",
            "email",
            "phone",
            "website",
            "owner",
        ]
        read_only_fields = ["id", "owner"]


class AddressSerializer(serializers.ModelSerializer):
    class Meta:
        model = Address
        fields = [
            "id",
            "type",
            "company",
            "name",
            "street",
            "city",
            "postal_code",
            "country",
        ]
        read_only_fields = ["id", "company"]
