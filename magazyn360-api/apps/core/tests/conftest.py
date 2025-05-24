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
