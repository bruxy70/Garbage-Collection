"""Test the Simple Integration config flow."""
from unittest.mock import patch

import pytest
from homeassistant import config_entries, data_entry_flow, setup
from homeassistant.core import HomeAssistant

from custom_components.garbage_collection.const import DOMAIN


# This fixture bypasses the actual setup of the integration
# since we only want to test the config flow. We test the
# actual functionality of the integration in other test modules.
@pytest.fixture(autouse=True)
def bypass_setup_fixture():
    """Prevent setup."""
    with patch(
        "custom_components.garbage_collection.async_setup_entry",
        return_value=True,
    ), patch(
        "custom_components.garbage_collection.async_setup",
        return_value=True,
    ):
        yield


async def test_form(hass: HomeAssistant):
    """Test we get the form."""
    await setup.async_setup_component(hass, "persistent_notification", {})

    result = await hass.config_entries.flow.async_init(
        DOMAIN, context={"source": config_entries.SOURCE_USER}
    )
    # Check that the config flow shows the user form as the first step
    assert result["type"] == data_entry_flow.RESULT_TYPE_FORM
    assert result["step_id"] == "user"

    # If a user were to enter `weekly` for frequency
    # it would result in this function call
    result = await hass.config_entries.flow.async_configure(
        result["flow_id"],
        user_input={"name": "test", "frequency": "weekly"},
    )

    # Check that the config flow is complete and a new entry is created with
    # the input data
    assert result["type"] == data_entry_flow.RESULT_TYPE_FORM
    assert result["step_id"] == "detail"
    assert result["errors"] == {}
