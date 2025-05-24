from unittest.mock import Mock


def test_has_object_permission_authenticated_user_same_company(
    permission, mock_request, mock_view
):
    mock_request.user.is_authenticated = True
    mock_request.user.company = "company1"
    obj = Mock()
    obj.company = "company1"

    assert permission.has_object_permission(mock_request, mock_view, obj) is True


def test_has_object_permission_unauthenticated_user(
    permission, mock_request, mock_view
):
    mock_request.user.is_authenticated = False
    mock_request.user.company = "company1"
    obj = Mock()
    obj.company = "company1"

    assert permission.has_object_permission(mock_request, mock_view, obj) is False


def test_has_object_permission_no_company_attribute(
    permission, mock_request, mock_view
):
    mock_request.user.is_authenticated = True
    delattr(mock_request.user, "company")
    obj = Mock()
    obj.company = "company1"

    assert permission.has_object_permission(mock_request, mock_view, obj) is False


def test_has_object_permission_different_company(permission, mock_request, mock_view):
    mock_request.user.is_authenticated = True
    mock_request.user.company = "company1"
    obj = Mock()
    obj.company = "company2"

    assert permission.has_object_permission(mock_request, mock_view, obj) is False
