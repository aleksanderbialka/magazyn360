from unittest.mock import Mock

import pytest

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


def test_has_object_permission_authenticated_user_same_company(
    permission, mock_request, mock_view
):
    mock_request.user.is_authenticated = True
    mock_request.user.company = "test_company"
    mock_obj = Mock()
    mock_obj.company = "test_company"

    result = permission.has_object_permission(mock_request, mock_view, mock_obj)

    assert result is True


def test_has_object_permission_authenticated_user_different_company(
    permission, mock_request, mock_view
):
    mock_request.user.is_authenticated = True
    mock_request.user.company = "test_company"
    mock_obj = Mock()
    mock_obj.company = "different_company"

    result = permission.has_object_permission(mock_request, mock_view, mock_obj)

    assert result is False


def test_has_object_permission_unauthenticated_user(
    permission, mock_request, mock_view
):
    mock_request.user.is_authenticated = False
    mock_obj = Mock()

    result = permission.has_object_permission(mock_request, mock_view, mock_obj)

    assert result is False


def test_has_object_permission_user_without_company(
    permission, mock_request, mock_view
):
    mock_request.user.is_authenticated = True
    delattr(mock_request.user, "company")
    mock_obj = Mock()

    result = permission.has_object_permission(mock_request, mock_view, mock_obj)

    assert result is False


def test_has_object_permission_obj_without_company(permission, mock_request, mock_view):
    mock_request.user.is_authenticated = True
    mock_request.user.company = "test_company"
    mock_obj = Mock()
    mock_obj.company = None

    result = permission.has_object_permission(mock_request, mock_view, mock_obj)

    assert result is False
