"""Test Options flow."""
from homeassistant import data_entry_flow, setup
from homeassistant.core import HomeAssistant
from pytest_homeassistant_custom_component.common import MockConfigEntry

from custom_components.garbage_collection import const


async def test_weekly_options_flow(hass: HomeAssistant) -> None:
    """Test we get the form."""
    config_entry: MockConfigEntry = MockConfigEntry(
        domain=const.DOMAIN,
        data={"name": "test", "frequency": "weekly", "collection_days": ["wed"]},
        title="sensor",
        version=4.5,
    )
    config_entry.add_to_hass(hass)

    # Initialise Options Flow
    result = await hass.config_entries.options.async_init(config_entry.entry_id)

    # Check that the config flow shows the user form as the first step
    assert result["type"] == data_entry_flow.RESULT_TYPE_FORM
    assert result["step_id"] == "init"

    # If a user were to enter `weekly` for frequency
    # it would result in this function call
    result = await hass.config_entries.options.async_configure(
        result["flow_id"],
        user_input={"frequency": "weekly"},
    )

    # Check that the config flow is complete and a new entry is created with
    # the input data
    assert result["type"] == data_entry_flow.RESULT_TYPE_FORM
    assert result["step_id"] == "detail"
    assert result["errors"] == {}

    # ...add Wednesday
    result = await hass.config_entries.options.async_configure(
        result["flow_id"],
        user_input={"collection_days": ["wed"]},
    )
    # Should create entry
    assert result["type"] == data_entry_flow.RESULT_TYPE_CREATE_ENTRY
    assert result["data"] == {"frequency": "weekly", "collection_days": ["wed"]}


async def test_monthly_options_flow(hass: HomeAssistant) -> None:
    """Test we get the form."""
    await setup.async_setup_component(hass, "persistent_notification", {})

    config_entry: MockConfigEntry = MockConfigEntry(
        domain=const.DOMAIN,
        data={
            "name": "test",
            "frequency": "monthly",
            "collection_days": ["wed"],
            "weekday_order_number": ["1"],
            "period": 1,
        },
        title="sensor",
        version=4.5,
    )
    config_entry.add_to_hass(hass)

    # Initialise Options Flow
    result = await hass.config_entries.options.async_init(config_entry.entry_id)
    # Check that the config flow shows the user form as the first step
    assert result["type"] == data_entry_flow.RESULT_TYPE_FORM
    assert result["step_id"] == "init"

    # If a user were to enter `weekly` for frequency
    # it would result in this function call
    result = await hass.config_entries.options.async_configure(
        result["flow_id"],
        user_input={"frequency": "monthly"},
    )

    # Check that the config flow is complete and a new entry is created with
    # the input data
    assert result["type"] == data_entry_flow.RESULT_TYPE_FORM
    assert result["step_id"] == "detail"
    assert result["errors"] == {}

    # ...add Wednesday
    result = await hass.config_entries.options.async_configure(
        result["flow_id"],
        user_input={
            "collection_days": ["wed"],
            "weekday_order_number": ["1"],
            "period": 1,
        },
    )
    # Should create entry
    assert result["type"] == data_entry_flow.RESULT_TYPE_CREATE_ENTRY
    assert result["data"] == {
        "frequency": "monthly",
        "collection_days": ["wed"],
        "weekday_order_number": ["1"],
        "period": 1,
    }


async def test_annual_options_flow(hass: HomeAssistant) -> None:
    """Test we get the form."""
    await setup.async_setup_component(hass, "persistent_notification", {})

    config_entry: MockConfigEntry = MockConfigEntry(
        domain=const.DOMAIN,
        data={
            "name": "test",
            "frequency": "annual",
            "date": "04/01",
        },
        title="sensor",
        version=4.5,
    )
    config_entry.add_to_hass(hass)

    # Initialise Options Flow
    result = await hass.config_entries.options.async_init(config_entry.entry_id)

    # Check that the config flow shows the user form as the first step
    assert result["type"] == data_entry_flow.RESULT_TYPE_FORM
    assert result["step_id"] == "init"

    # If a user were to enter `weekly` for frequency
    # it would result in this function call
    result = await hass.config_entries.options.async_configure(
        result["flow_id"],
        user_input={"frequency": "annual"},
    )

    # Check that the config flow is complete and a new entry is created with
    # the input data
    assert result["type"] == data_entry_flow.RESULT_TYPE_FORM
    assert result["step_id"] == "detail"
    assert result["errors"] == {}

    # ...add Wednesday
    result = await hass.config_entries.options.async_configure(
        result["flow_id"],
        user_input={
            "date": "04/01",
        },
    )
    # Should create entry
    assert result["type"] == data_entry_flow.RESULT_TYPE_CREATE_ENTRY
    assert result["data"] == {"frequency": "annual", "date": "04/01"}
