from django.db import models
from django.utils.translation import gettext_lazy as _


class Unit(models.TextChoices):
    PCS = "szt", _("Sztuka")
    KG = "kg", _("Kilogram")
    M3 = "m3", _("Metr sześcienny")
    M = "m", _("Metr")


class DocStatus(models.TextChoices):
    DRAFT = "draft", _("Wersja robocza")
    POSTED = "posted", _("Zaksięgowany")
    CANCELLED = "cancelled", _("Anulowany")


class DocType(models.TextChoices):
    PZ = "PZ", _("Przyjęcie zewnętrzne")
    WZ = "WZ", _("Wydanie zewnętrzne")
    MM = "MM", _("Przesunięcie międzymagazynowe")
    RW = "RW", _("Rozchód wewnętrzny")
    PW = "PW", _("Przyjęcie wewnętrzne")
