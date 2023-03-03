"""Test Options flow."""
import pytest
from homeassistant import data_entry_flow, setup
from homeassistant.core import HomeAssistant
from pytest_homeassistant_custom_component.common import MockConfigEntry

from custom_components.garbage_collection import const


@pytest.mark.asyncio
async def test_annual_options_flow(hass: HomeAssistant) -> None:
    """Test we get the form."""
    await setup.async_setup_component(hass, "persistent_notification", {})

    config_entry: MockConfigEntry = MockConfigEntry(
        domain=const.DOMAIN,
        options={
            "frequency": "annual",
            "date": "04/01",
        },
        title="sensor",
        version=6,
    )
    config_entry.add_to_hass(hass)
    await hass.config_entries.async_setup(config_entry.entry_id)
    await hass.async_block_till_done()

    # Initialise Options Flow
    result = await hass.config_entries.options.async_init(config_entry.entry_id)
    assert "type" in result and "step_id" in result and "flow_id" in result

    # Check that the config flow shows the user form as the first step
    assert result["type"] == data_entry_flow.RESULT_TYPE_FORM
    assert result["step_id"] == "init"

    # If a user were to enter `weekly` for frequency
    # it would result in this function call
    result = await hass.config_entries.options.async_configure(
        result["flow_id"],
        user_input={"frequency": "annual"},
    )
    assert (
        "type" in result
        and "step_id" in result
        and "flow_id" in result
        and "errors" in result
    )

    # Check that the config flow is complete and a new entry is created with
    # the input data
    assert result["type"] == data_entry_flow.RESULT_TYPE_FORM
    assert result["step_id"] == "detail"
    assert not result["errors"]

    # ...add Wednesday
    result = await hass.config_entries.options.async_configure(
        result["flow_id"],
        user_input={
            "date": "04/01",
        },
    )
    assert "type" in result and "data" in result

    # Should create entry
    assert result["type"] == data_entry_flow.RESULT_TYPE_CREATE_ENTRY
    assert result["data"] == {"frequency": "annual", "date": "04/01"}


@pytest.mark.asyncio
async def test_blank_options_flow(hass: HomeAssistant) -> None:
    """Test we get the form."""
    await setup.async_setup_component(hass, "persistent_notification", {})

    config_entry: MockConfigEntry = MockConfigEntry(
        domain=const.DOMAIN,
        options={
            "frequency": "blank",
            "verbose_state": True,
            "date_format": "%d-%b-%Y",
            "verbose_format": "on {date}, in {days} days",
        },
        title="sensor",
        version=6,
    )
    config_entry.add_to_hass(hass)
    await hass.config_entries.async_setup(config_entry.entry_id)
    await hass.async_block_till_done()

    # Initialise Options Flow
    result = await hass.config_entries.options.async_init(config_entry.entry_id)
    assert "type" in result and "step_id" in result and "flow_id" in result

    # Check that the config flow shows the user form as the first step
    assert result["type"] == data_entry_flow.RESULT_TYPE_FORM
    assert result["step_id"] == "init"

    # If a user were to enter `weekly` for frequency
    # it would result in this function call
    result = await hass.config_entries.options.async_configure(
        result["flow_id"],
        user_input={
            "frequency": "blank",
            "verbose_state": True,
        },
    )
    assert (
        "type" in result
        and "step_id" in result
        and "flow_id" in result
        and "errors" in result
    )

    # Check that the config flow is complete and a new entry is created with
    # the input data
    assert result["type"] == data_entry_flow.RESULT_TYPE_FORM
    assert result["step_id"] == "detail"
    assert not result["errors"]

    # ...add Wednesday
    result = await hass.config_entries.options.async_configure(
        result["flow_id"],
        user_input={
            "date_format": "%d-%b-%Y",
            "verbose_format": "on {date}, in {days} days",
        },
    )
    assert "type" in result and "data" in result
    # Should create entry
    assert result["type"] == data_entry_flow.RESULT_TYPE_CREATE_ENTRY
    assert result["data"] == {
        "frequency": "blank",
        "verbose_state": True,
        "date_format": "%d-%b-%Y",
        "verbose_format": "on {date}, in {days} days",
    }


@pytest.mark.asyncio
async def test_every_n_days_options_flow(hass: HomeAssistant) -> None:
    """Test we get the form."""
    await setup.async_setup_component(hass, "persistent_notification", {})

    config_entry: MockConfigEntry = MockConfigEntry(
        domain=const.DOMAIN,
        options={
            "frequency": "every-n-days",
            "period": 14,
            "first_date": "2020-01-01",
        },
        title="sensor",
        version=6,
    )
    config_entry.add_to_hass(hass)
    await hass.config_entries.async_setup(config_entry.entry_id)
    await hass.async_block_till_done()

    # Initialise Options Flow
    result = await hass.config_entries.options.async_init(config_entry.entry_id)
    assert "type" in result and "step_id" in result and "flow_id" in result

    # Check that the config flow shows the user form as the first step
    assert result["type"] == data_entry_flow.RESULT_TYPE_FORM
    assert result["step_id"] == "init"

    # If a user were to enter `weekly` for frequency
    # it would result in this function call
    result = await hass.config_entries.options.async_configure(
        result["flow_id"],
        user_input={"frequency": "every-n-days"},
    )
    assert (
        "type" in result
        and "step_id" in result
        and "flow_id" in result
        and "errors" in result
    )

    # Check that the config flow is complete and a new entry is created with
    # the input data
    assert result["type"] == data_entry_flow.RESULT_TYPE_FORM
    assert result["step_id"] == "detail"
    assert not result["errors"]

    # ...add Wednesday
    result = await hass.config_entries.options.async_configure(
        result["flow_id"],
        user_input={
            "period": 14,
            "first_date": "2020-01-01",
        },
    )
    assert "type" in result and "data" in result
    # Should create entry
    assert result["type"] == data_entry_flow.RESULT_TYPE_CREATE_ENTRY
    assert result["data"] == {
        "frequency": "every-n-days",
        "period": 14,
        "first_date": "2020-01-01",
    }


@pytest.mark.asyncio
async def test_every_n_weeks_options_flow(hass: HomeAssistant) -> None:
    """Test we get the form."""
    await setup.async_setup_component(hass, "persistent_notification", {})

    config_entry: MockConfigEntry = MockConfigEntry(
        domain=const.DOMAIN,
        options={
            "frequency": "every-n-weeks",
            "period": 2,
            "first_week": 3,
            "collection_days": ["wed"],
        },
        title="sensor",
        version=6,
    )
    config_entry.add_to_hass(hass)
    await hass.config_entries.async_setup(config_entry.entry_id)
    await hass.async_block_till_done()

    # Initialise Options Flow
    result = await hass.config_entries.options.async_init(config_entry.entry_id)
    assert "type" in result and "step_id" in result and "flow_id" in result
    # Check that the config flow shows the user form as the first step
    assert result["type"] == data_entry_flow.RESULT_TYPE_FORM
    assert result["step_id"] == "init"

    # If a user were to enter `weekly` for frequency
    # it would result in this function call
    result = await hass.config_entries.options.async_configure(
        result["flow_id"],
        user_input={"frequency": "every-n-weeks"},
    )
    assert (
        "type" in result
        and "step_id" in result
        and "flow_id" in result
        and "errors" in result
    )

    # Check that the config flow is complete and a new entry is created with
    # the input data
    assert result["type"] == data_entry_flow.RESULT_TYPE_FORM
    assert result["step_id"] == "detail"
    assert not result["errors"]

    # ...add Wednesday
    result = await hass.config_entries.options.async_configure(
        result["flow_id"],
        user_input={
            "period": 2,
            "first_week": 3,
            "collection_days": ["wed"],
        },
    )
    assert "type" in result and "data" in result
    # Should create entry
    assert result["type"] == data_entry_flow.RESULT_TYPE_CREATE_ENTRY
    assert result["data"] == {
        "frequency": "every-n-weeks",
        "period": 2,
        "first_week": 3,
        "collection_days": ["wed"],
    }


@pytest.mark.asyncio
async def test_monthly_options_flow(hass: HomeAssistant) -> None:
    """Test we get the form."""
    await setup.async_setup_component(hass, "persistent_notification", {})

    config_entry: MockConfigEntry = MockConfigEntry(
        domain=const.DOMAIN,
        options={
            "frequency": "monthly",
            "collection_days": ["wed"],
            "weekday_order_number": ["1"],
            "period": 1,
        },
        title="sensor",
        version=6,
    )
    config_entry.add_to_hass(hass)
    await hass.config_entries.async_setup(config_entry.entry_id)
    await hass.async_block_till_done()

    # Initialise Options Flow
    result = await hass.config_entries.options.async_init(config_entry.entry_id)
    assert "type" in result and "step_id" in result and "flow_id" in result
    # Check that the config flow shows the user form as the first step
    assert result["type"] == data_entry_flow.RESULT_TYPE_FORM
    assert result["step_id"] == "init"

    # If a user were to enter `weekly` for frequency
    # it would result in this function call
    result = await hass.config_entries.options.async_configure(
        result["flow_id"],
        user_input={"frequency": "monthly"},
    )
    assert (
        "type" in result
        and "step_id" in result
        and "flow_id" in result
        and "errors" in result
    )

    # Check that the config flow is complete and a new entry is created with
    # the input data
    assert result["type"] == data_entry_flow.RESULT_TYPE_FORM
    assert result["step_id"] == "detail"
    assert not result["errors"]

    # ...add Wednesday
    result = await hass.config_entries.options.async_configure(
        result["flow_id"],
        user_input={
            "collection_days": ["wed"],
            "weekday_order_number": ["1"],
            "period": 1,
        },
    )
    assert "type" in result and "data" in result
    # Should create entry
    assert result["type"] == data_entry_flow.RESULT_TYPE_CREATE_ENTRY
    assert result["data"] == {
        "frequency": "monthly",
        "collection_days": ["wed"],
        "weekday_order_number": ["1"],
        "period": 1,
    }


@pytest.mark.asyncio
async def test_weekly_options_flow(hass: HomeAssistant) -> None:
    """Test we get the form."""
    config_entry: MockConfigEntry = MockConfigEntry(
        domain=const.DOMAIN,
        options={"frequency": "weekly", "collection_days": ["wed"]},
        title="sensor",
        version=6,
    )
    config_entry.add_to_hass(hass)
    await hass.config_entries.async_setup(config_entry.entry_id)
    await hass.async_block_till_done()

    # Initialise Options Flow
    result = await hass.config_entries.options.async_init(config_entry.entry_id)
    assert "type" in result and "step_id" in result and "flow_id" in result

    # Check that the config flow shows the user form as the first step
    assert result["type"] == data_entry_flow.RESULT_TYPE_FORM
    assert result["step_id"] == "init"

    # If a user were to enter `weekly` for frequency
    # it would result in this function call
    result = await hass.config_entries.options.async_configure(
        result["flow_id"],
        user_input={"frequency": "weekly"},
    )
    assert (
        "type" in result
        and "step_id" in result
        and "flow_id" in result
        and "errors" in result
    )

    # Check that the config flow is complete and a new entry is created with
    # the input data
    assert result["type"] == data_entry_flow.RESULT_TYPE_FORM
    assert result["step_id"] == "detail"
    assert not result["errors"]

    # ...add Wednesday
    result = await hass.config_entries.options.async_configure(
        result["flow_id"],
        user_input={"collection_days": ["wed"]},
    )
    assert "type" in result and "data" in result
    # Should create entry
    assert result["type"] == data_entry_flow.RESULT_TYPE_CREATE_ENTRY
    assert result["data"] == {"frequency": "weekly", "collection_days": ["wed"]}
