import logging

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.utils.translation import gettext_lazy as _

from apps.core.models import Address, Company, CustomUser

logger = logging.getLogger(__name__)


@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    """
    Custom admin interface for managing users with role-based access control.
    """

    list_display = (
        "username",
        "email",
        "role",
        "company",
        "position",
        "is_active",
        "last_login",
    )
    list_filter = ("role", "company", "is_active", "is_staff")
    search_fields = ("email", "first_name", "last_name", "phone_number", "position")
    ordering = ("email",)

    fieldsets = (
        (_("Authentication"), {"fields": ("username", "email", "password")}),
        (_("Personal info"), {"fields": ("first_name", "last_name", "phone_number")}),
        (_("Company info"), {"fields": ("company", "department", "position", "role")}),
        (
            _("Permissions"),
            {
                "fields": (
                    "is_active",
                    "is_staff",
                    "is_superuser",
                    "groups",
                    "user_permissions",
                ),
                "classes": ("collapse",),
            },
        ),
        (_("Important dates"), {"fields": ("last_login", "date_joined")}),
    )

    add_fieldsets = (
        (
            None,
            {
                "classes": ("wide",),
                "fields": (
                    "email",
                    "password1",
                    "password2",
                    "role",
                    "company",
                    "position",
                    "is_active",
                ),
            },
        ),
    )

    def save_related(self, request, form, formsets, change):
        super().save_related(request, form, formsets, change)
        form.instance.sync_group_with_role()
        form.instance.save()


@admin.register(Company)
class CompanyAdmin(admin.ModelAdmin):
    """
    Admin interface for managing companies and their addresses.
    """

    list_display = ("name", "tax_id", "email", "phone", "primary_address_city", "owner")
    list_filter = ("addresses__city", "addresses__country")
    search_fields = ("name", "tax_id", "email", "owner__email", "addresses__city")
    ordering = ("name",)
    fieldsets = (
        (_("General"), {"fields": ("name", "email", "phone", "website")}),
        (
            _("Identifiers"),
            {
                "fields": ("tax_id", "statistical_number", "national_court_register"),
                "classes": ("collapse",),
            },
        ),
        (_("Ownership"), {"fields": ("owner",), "classes": ("collapse",)}),
    )

    def primary_address_city(self, obj):
        """
        Returns the city of the primary address for display in the admin list view.
        """
        return obj.primary_address.name if obj.primary_address else None


@admin.register(Address)
class AddressAdmin(admin.ModelAdmin):
    """
    Admin interface for managing company addresses.
    """

    list_display = ("name", "type", "company", "city", "postal_code", "country")
    list_filter = ("type", "city", "country", "company")
    search_fields = ("name", "company__name", "street", "city", "postal_code")
    ordering = ("company", "type")
    fieldsets = (
        (_("General"), {"fields": ("name", "type", "company")}),
        (_("Address"), {"fields": ("street", "city", "postal_code", "country")}),
    )
