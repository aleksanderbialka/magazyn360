from unittest.mock import Mock, patch

from django.contrib.auth import get_user_model
from django.test import RequestFactory, TestCase

from apps.core.admin import CompanyAdmin, CustomUserAdmin
from apps.core.models import Company, CustomUser


class TestCustomUserAdmin(TestCase):
    def setUp(self):
        self.user_admin = CustomUserAdmin(CustomUser, None)
        self.request = RequestFactory().get("/admin")
        self.user = get_user_model().objects.create(
            username="testuser", email="test@example.com"
        )

    @patch("apps.core.models.CustomUser.sync_group_with_role")
    def test_save_related_calls_sync_group_with_role(self, mock_sync):
        form = Mock()
        form.instance = self.user
        formsets = []
        change = True

        self.user_admin.save_related(self.request, form, formsets, change)

        mock_sync.assert_called_once()

    @patch("apps.core.models.CustomUser.save")
    def test_save_related_calls_save(self, mock_save):
        form = Mock()
        form.instance = self.user
        formsets = []
        change = True

        self.user_admin.save_related(self.request, form, formsets, change)

        mock_save.assert_called_once()

    @patch("django.contrib.auth.admin.UserAdmin.save_related")
    def test_save_related_calls_super(self, mock_super):
        form = Mock()
        form.instance = self.user
        formsets = []
        change = True

        self.user_admin.save_related(self.request, form, formsets, change)

        mock_super.assert_called_once_with(self.request, form, formsets, change)


class TestCompanyAdmin(TestCase):
    def setUp(self):
        self.company_admin = CompanyAdmin(Company, None)

    def test_primary_address_city_with_primary_address(self):
        mock_company = Mock()
        mock_address = Mock()
        mock_address.name = "Test City"
        mock_company.primary_address = mock_address

        result = self.company_admin.primary_address_city(mock_company)
        self.assertEqual(result, "Test City")

    def test_primary_address_city_without_primary_address(self):
        mock_company = Mock()
        mock_company.primary_address = None

        result = self.company_admin.primary_address_city(mock_company)
        self.assertIsNone(result)
