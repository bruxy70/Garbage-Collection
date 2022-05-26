"""Fixtures for trsting."""
from datetime import datetime
from unittest.mock import patch

import pytest

TEST_PLUGINS = "pytest_homeassistant_custom_component"  # pylint: disable=invalid-name
FUNCTION_PATH = "custom_components.garbage_collection.helpers.now"


# Fix current date to June 1st, 2020
@pytest.fixture(autouse=True)
def now_fixed():
    """Return fixed date."""
    with patch(
        FUNCTION_PATH,
        return_value=datetime(2020, 4, 1, 12, 0, 0, 0),
    ):
        yield


# This fixture enables loading custom integrations in all tests.
# Remove to enable selective use of this fixture
@pytest.fixture(autouse=True)
def auto_enable_custom_integrations(enable_custom_integrations):
    """Enable custom integrations."""
    # pylint: disable=unused-argument
    yield


# This fixture is used to prevent HomeAssistant from attempting
# to create and dismiss persistent notifications.
# These calls would fail without this fixture since the persistent_notification
# integration is never loaded during a test.
@pytest.fixture(name="skip_notifications", autouse=True)
def skip_notifications_fixture():
    """Skip notification calls."""
    with patch("homeassistant.components.persistent_notification.async_create"), patch(
        "homeassistant.components.persistent_notification.async_dismiss"
    ):
        yield
