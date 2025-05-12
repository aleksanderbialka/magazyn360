import logging
import uuid

from django.contrib.auth.models import AbstractUser, Group
from django.db import models
from django.utils.translation import gettext_lazy as _

from . import validators
from .enums import AddressTypes, Countries, Role

logger = logging.getLogger(__name__)


class TimeStampedModel(models.Model):
    """Base model providing automatic timestamps.

    Attributes:
        created_at: When the object was created
        updated_at: When the object was last modified
    """

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class CustomUser(AbstractUser, TimeStampedModel):
    """Enhanced user model with role-based access control.

    Attributes:
        id: UUID primary key
        username: Unique username for authentication
        first_name: User's first name
        last_name: User's last name
        email: User's email address
        phone_number: Optional Polish phone number
        role: User's role in the system
        company: Associated company
        position: Job position
        department: Department name
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    email = models.EmailField(_("Email address"), unique=True)
    phone_number = models.CharField(
        _("Phone Number"),
        max_length=20,
        blank=True,
        help_text=_("Optional Polish phone number"),
        validators=[validators.PolishPhoneNumberValidator()],
    )
    role = models.CharField(
        _("Role"),
        help_text=_("User role in the system"),
        choices=Role.choices,
        default=Role.VIEWER,
    )
    company = models.ForeignKey(
        "core.Company",
        on_delete=models.PROTECT,
        related_name="users",
        help_text=_("Associated company"),
        null=True,
        blank=True,
    )
    position = models.CharField(
        _("Position"), max_length=50, blank=True, help_text=_("Job position")
    )
    department = models.CharField(_("Department"), max_length=50, blank=True)

    USERNAME_FIELD = "username"
    REQUIRED_FIELDS = ["email"]

    class Meta:
        verbose_name = _("User")
        verbose_name_plural = _("Users")
        indexes = [
            models.Index(fields=["email"]),
            models.Index(fields=["role"]),
        ]

    def __str__(self):
        return f"{self.email} ({Role(self.role).name.lower()})"

    def sync_group_with_role(self):
        """Synchronize user group with role.
        This method assigns the user to a group based on their role.
        """
        role_to_group = {
            Role.ADMIN: "Admin",
            Role.MANAGER: "Manager",
            Role.WORKER: "Worker",
            Role.VIEWER: "Viewer",
            Role.OWNER: "Owner",
        }

        group_name = role_to_group.get(Role(self.role))
        if not group_name:
            return

        group, _ = Group.objects.get_or_create(name=group_name)
        self.groups.set([group])

    @property
    def company_name(self):
        return self.company.name if self.company else None


class Company(TimeStampedModel):
    """Company model with business details.

    Attributes:
        id: UUID primary key
        name: Company name
        tax_id: NIP number
        statistical_number: REGON number
        national_court_register: KRS number
        email: Company email
        phone: Company phone
        website: Company website
        owner: Company owner (CustomUser)
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(_("Company Name"), max_length=255)
    tax_id = models.CharField(
        _("Tax ID (NIP)"),
        help_text=_("Tax Identification Number 10 digits"),
        max_length=20,
        validators=[validators.NIPValidator()],
    )
    statistical_number = models.CharField(
        _("Statistical Number (REGON)"),
        help_text=_("Statistical Number 9 or 14 digits"),
        max_length=20,
        validators=[validators.REGONValidator()],
    )
    national_court_register = models.CharField(
        _("National Court Register (KRS)"),
        help_text=_("National Court Register 10 digits"),
        max_length=20,
        validators=[validators.KRSValidator()],
    )
    email = models.EmailField(_("Email"), help_text=_("Company email"), unique=True)
    phone = models.CharField(
        _("Phone Number"),
        help_text=_("Company phone number"),
        max_length=20,
        validators=[validators.PolishPhoneNumberValidator()],
    )
    website = models.URLField(
        _("Website"), help_text=_("Company website"), blank=True, default=""
    )
    owner = models.ForeignKey(
        "core.CustomUser",
        on_delete=models.PROTECT,
        related_name="owned_companies",
        verbose_name=_("Owner"),
        help_text=_("Company owner"),
    )

    class Meta:
        verbose_name = _("Company")
        verbose_name_plural = _("Companies")
        indexes = [
            models.Index(fields=["tax_id"]),
            models.Index(fields=["email"]),
            models.Index(fields=["national_court_register"]),
        ]
        constraints = [
            models.UniqueConstraint(fields=["tax_id"], name="unique_tax_id"),
            models.UniqueConstraint(fields=["email"], name="unique_company_email"),
            models.UniqueConstraint(
                fields=["national_court_register"], name="unique_krs"
            ),
        ]

    def __str__(self):
        return self.name

    @property
    def primary_address(self) -> "Address":
        """Returns the primary billing address."""
        return self.addresses.filter(type=AddressTypes.OFFICE).first()

    @property
    def shipping_address(self) -> "Address":
        """Returns the primary billing address."""
        return self.addresses.filter(type=AddressTypes.BILLING).first()

    def get_address_by_type(self, address_type: AddressTypes) -> "Address":
        """Returns address by type."""
        return self.addresses.filter(type=address_type).first()


class Address(TimeStampedModel):
    """Model for company addresses.

    Attributes:
        id: UUID primary key
        type: Address type (billing, shipping, etc.)
        company: Associated company
        name: Address identifier
        street: Street address
        city: City name
        postal_code: Postal code
        country: Country code
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    type = models.CharField(
        _("Address Type"),
        help_text=_("Type of address (billing, shipping, etc.)"),
        max_length=50,
        choices=AddressTypes.choices,
        default=AddressTypes.BILLING,
    )
    company = models.ForeignKey(
        "core.Company",
        on_delete=models.CASCADE,
        related_name="addresses",
        verbose_name=_("Company"),
    )
    name = models.CharField(
        _("Address Name"), help_text=_("Identifier for the address"), max_length=255
    )
    street = models.CharField(_("Street"), max_length=255)
    city = models.CharField(_("City"), max_length=100)
    postal_code = models.CharField(_("Postal Code"), max_length=20)
    country = models.CharField(
        _("Country"),
        choices=Countries.choices,
        default=Countries.POLAND,
    )

    class Meta:
        verbose_name = _("Address")
        verbose_name_plural = _("Addresses")
        indexes = [
            models.Index(fields=["type"]),
            models.Index(fields=["company", "type"]),
        ]
        constraints = [
            models.UniqueConstraint(
                fields=["company", "type"],
                name="unique_billing_address",
                condition=models.Q(type=AddressTypes.BILLING),
            )
        ]

    def __str__(self):
        return f"{self.name} ({self.company.name})"

    @property
    def full_address(self) -> str:
        """Get formatted address string."""
        country_name = Countries(self.country).label
        return _("{street}\n{postal_code} {city}\n{country}").format(
            street=self.street,
            postal_code=self.postal_code,
            city=self.city,
            country=country_name,
        )
