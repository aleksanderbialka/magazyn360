from django.core.validators import RegexValidator
from django.utils.translation import gettext_lazy as _


class PolishPhoneNumberValidator(RegexValidator):
    regex = r"^\+?48?\d{9}$"
    message = _("Enter a valid Polish phone number (e.g. +48123456789 or 123456789)")
    code = "invalid_phone_number"


class NIPValidator(RegexValidator):
    regex = r"^\d{10}$"
    message = _("Enter a valid NIP number (10 digits)")
    code = "invalid_nip"


class REGONValidator(RegexValidator):
    regex = r"^\d{9}(\d{5})?$"
    message = _("Enter a valid REGON number (9 or 14 digits)")
    code = "invalid_regon"


class KRSValidator(RegexValidator):
    regex = r"^\d{10}$"
    message = _("Enter a valid KRS number (10 digits)")
    code = "invalid_krs"


class PolishPostalCodeValidator(RegexValidator):
    regex = r"^\d{2}-\d{3}$"
    message = _("Enter a valid postal code (e.g. 00-000)")
    code = "invalid_postal_code"
