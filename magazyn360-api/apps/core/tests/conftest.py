from unittest.mock import Mock

import pytest

from apps.core.enums import AddressTypes, Countries
from apps.core.models import Address, Company, CustomUser
from apps.core.permissions import IsInUserCompany


@pytest.fixture
def permission():
    return IsInUserCompany()


@pytest.fixture
def mock_request():
    request = Mock()
    request.user = Mock()
    return request


@pytest.fixture
def mock_view():
    return Mock()


@pytest.fixture
def owner():
    return CustomUser.objects.create(username="owner", email="owner@test.com")


@pytest.fixture
def company(owner):
    return Company.objects.create(
        name="Test Company",
        tax_id="1234567890",
        statistical_number="123456789",
        national_court_register="0000123456",
        email="test@company.com",
        phone="123456789",
        owner=owner,
    )


@pytest.fixture
def billing_address(company):
    return Address.objects.create(
        company=company,
        type=AddressTypes.BILLING,
        name="Billing Address",
        street="Test Street 1",
        city="Test City",
        postal_code="00-000",
        country=Countries.POLAND,
    )


@pytest.fixture
def office_address(company):
    return Address.objects.create(
        company=company,
        type=AddressTypes.OFFICE,
        name="Office Address",
        street="Test Street 2",
        city="Test City",
        postal_code="00-000",
        country=Countries.POLAND,
    )
