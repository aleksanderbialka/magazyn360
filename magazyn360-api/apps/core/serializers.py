from rest_framework import serializers

from apps.core.models import CustomUser


class UserSerializer(serializers.ModelSerializer):
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
