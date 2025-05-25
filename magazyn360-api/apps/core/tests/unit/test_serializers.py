from unittest.mock import Mock, patch

import pytest

from apps.core.enums import Role
from apps.core.models import CustomUser
from apps.core.serializers import UserCreateUpdateSerializer, UserListSerializer


@pytest.fixture
def user_validated_data():
    return {
        "username": "testuser",
        "email": "test@example.com",
        "password": "testpass123",
        "first_name": "Test",
        "last_name": "User",
        "role": Role.OWNER,
        "position": "Owner",
        "department": "Management",
    }


@pytest.mark.django_db
class TestUserSerializer:
    @pytest.mark.parametrize(
        "company,expected",
        [
            (Mock(name="Test Company"), "Test Company"),
            (None, None),
        ],
    )
    def test_get_company_name(self, company, expected):
        mock_user = Mock(spec=CustomUser)
        mock_user.company = company
        if company:
            company.name = expected
        serializer = UserListSerializer()
        assert serializer.get_company_name(mock_user) == expected

    @pytest.mark.parametrize(
        "update_data,with_password",
        [
            (
                {
                    "username": "updateduser",
                    "email": "updated@example.com",
                    "password": "newpass123",
                    "first_name": "Updated",
                    "last_name": "User",
                    "role": Role.MANAGER,
                    "position": "Manager",
                    "department": "Management",
                },
                True,
            ),
            (
                {
                    "username": "updateduser",
                    "email": "updated@example.com",
                    "first_name": "Updated",
                    "last_name": "User",
                    "role": Role.WORKER,
                    "position": "Worker",
                    "department": "Wearehouse",
                },
                False,
            ),
        ],
    )
    def test_update_user(self, update_data, with_password):
        mock_user = Mock(spec=CustomUser)
        serializer = UserCreateUpdateSerializer()
        updated_user = serializer.update(mock_user, update_data.copy())
        for key in update_data:
            if key != "password":
                assert getattr(updated_user, key) == update_data[key]
        if with_password:
            mock_user.set_password.assert_called_once_with(update_data["password"])
        else:
            mock_user.set_password.assert_not_called()
        mock_user.save.assert_called_once()
        mock_user.sync_group_with_role.assert_called_once()

    def test_create_user(self, user_validated_data):
        serializer = UserCreateUpdateSerializer()
        with patch.object(CustomUser, "sync_group_with_role") as mock_sync:
            user = serializer.create(user_validated_data.copy())
            for key in user_validated_data:
                if key != "password":
                    assert getattr(user, key) == user_validated_data[key]
            assert user.check_password(user_validated_data["password"])
            assert user.pk is not None
            assert mock_sync.called
