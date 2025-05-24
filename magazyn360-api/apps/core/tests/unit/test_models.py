import pytest

from apps.core.enums import AddressTypes, Role
from apps.core.models import CustomUser


@pytest.mark.django_db
class TestCustomUser:
    def test_sync_group_with_role_admin(self):
        user = CustomUser.objects.create(
            username="test_admin", email="admin@test.com", role=Role.ADMIN
        )
        user.sync_group_with_role()
        assert user.groups.count() == 1
        assert user.groups.first().name == "Admin"

    def test_sync_group_with_role_multiple_calls(self):
        user = CustomUser.objects.create(
            username="test_user", email="user@test.com", role=Role.MANAGER
        )
        user.sync_group_with_role()
        user.sync_group_with_role()
        assert user.groups.count() == 1
        assert user.groups.first().name == "Manager"

    def test_sync_group_with_role_change(self):
        user = CustomUser.objects.create(
            username="test_user", email="user@test.com", role=Role.VIEWER
        )
        user.sync_group_with_role()
        user.role = Role.WORKER
        user.sync_group_with_role()
        assert user.groups.count() == 1
        assert user.groups.first().name == "Worker"

    @pytest.mark.parametrize(
        "role,expected_group",
        [
            (Role.ADMIN, "Admin"),
            (Role.MANAGER, "Manager"),
            (Role.WORKER, "Worker"),
            (Role.VIEWER, "Viewer"),
            (Role.OWNER, "Owner"),
        ],
    )
    def test_sync_group_with_role_all_roles(self, role, expected_group):
        user = CustomUser.objects.create(
            username=f"test_{role}", email=f"{role}@test.com", role=role
        )
        user.sync_group_with_role()
        assert user.groups.count() == 1
        assert user.groups.first().name == expected_group


@pytest.mark.django_db
class TestCompany:
    def test_get_address_by_type(self, company, billing_address, office_address):
        assert company.get_address_by_type(AddressTypes.BILLING) == billing_address
        assert company.get_address_by_type(AddressTypes.OFFICE) == office_address
        assert company.get_address_by_type(AddressTypes.SHIPPING) is None

    def test_get_address_by_type_no_addresses(self, company):
        assert company.get_address_by_type(AddressTypes.BILLING) is None

    def test_primary_address_exists(self, company, office_address):
        assert company.primary_address == office_address

    def test_primary_address_no_office(self, company):
        assert company.primary_address is None

    def test_shipping_address_exists(self, company, billing_address):
        assert company.shipping_address == billing_address

    def test_shipping_address_no_billing(self, company):
        assert company.shipping_address is None


@pytest.mark.django_db
class TestAddress:
    def test_full_address(self, billing_address):
        expected = "Test Street 1\n00-000 Test City\nPoland"
        assert billing_address.full_address == expected
