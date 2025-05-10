from django.db.models import TextChoices
from django.utils.translation import gettext_lazy as _


class Role(TextChoices):
    """User roles in the system with hierarchical structure."""

    VIEWER = "viewer", _("Viewer")
    WORKER = "worker", _("Worker")
    MANAGER = "manager", _("Manager")
    ADMIN = "admin", _("Admin")
    OWNER = "owner", _("Owner")


class Countries(TextChoices):
    """Countries supported in the system."""

    POLAND = "poland", _("Poland")
    GERMANY = "germany", _("Germany")
    FRANCE = "france", _("France")
    SPAIN = "spain", _("Spain")
    ITALY = "italy", _("Italy")
    UK = "uk", _("United Kingdom")
    USA = "usa", _("United States")
    AUSTRIA = "austria", _("Austria")
    BELGIUM = "belgium", _("Belgium")
    NETHERLANDS = "netherlands", _("Netherlands")
    SWITZERLAND = "switzerland", _("Switzerland")
    CZECH_REPUBLIC = "czech_republic", _("Czech Republic")
    SLOVAKIA = "slovakia", _("Slovakia")
    HUNGARY = "hungary", _("Hungary")
    SLOVENIA = "slovenia", _("Slovenia")
    CROATIA = "croatia", _("Croatia")
    BULGARIA = "bulgaria", _("Bulgaria")
    ROMANIA = "romania", _("Romania")
    PORTUGAL = "portugal", _("Portugal")
    SWEDEN = "sweden", _("Sweden")
    FINLAND = "finland", _("Finland")
    DENMARK = "denmark", _("Denmark")
    NORWAY = "norway", _("Norway")
    IRELAND = "ireland", _("Ireland")


class AddressTypes(TextChoices):
    """Types of addresses in the system."""

    OFFICE = "office", _("Office")
    BILLING = "billing", _("Billing")
    SHIPPING = "shipping", _("Shipping")
    WAREHOUSE = "warehouse", _("Warehouse")
    FACTORY = "factory", _("Factory")
    HEAD_OFFICE = "head_office", _("Head Office")
    OTHER = "other", _("Other")
