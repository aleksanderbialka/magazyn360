from unittest.mock import Mock

import pytest

from apps.core.models import CustomUser
from apps.core.serializers import UserSerializer


@pytest.mark.django_db
class TestUserSerializer:
    def test_get_company_name_with_company(self):
        mock_company = Mock()
        mock_company.name = "Test Company"

        mock_user = Mock(spec=CustomUser)
        mock_user.company = mock_company

        serializer = UserSerializer()

        result = serializer.get_company_name(mock_user)

        assert result == "Test Company"

    def test_get_company_name_without_company(self):
        mock_user = Mock(spec=CustomUser)
        mock_user.company = None

        serializer = UserSerializer()

        result = serializer.get_company_name(mock_user)

        assert result is None
