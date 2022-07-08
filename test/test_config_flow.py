"""Test config flow."""
from unittest.mock import patch

from homeassistant import config_entries, data_entry_flow, setup
from homeassistant.core import HomeAssistant

from custom_components.garbage_collection.const import DOMAIN


async def test_annual_config_flow(hass: HomeAssistant) -> None:
    """Test we get the form."""
    await setup.async_setup_component(hass, "persistent_notification", {})

    # Initialise Config Flow
    result = await hass.config_entries.flow.async_init(
        DOMAIN, context={"source": config_entries.SOURCE_USER}
    )
    assert "type" in result and "step_id" in result and "flow_id" in result

    # Check that the config flow shows the user form as the first step
    assert result["type"] == data_entry_flow.RESULT_TYPE_FORM
    assert result["step_id"] == "user"

    # If a user were to enter `weekly` for frequency
    # it would result in this function call
    result = await hass.config_entries.flow.async_configure(
        result["flow_id"],
        user_input={"name": "test", "frequency": "annual"},
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
    with patch(
        "custom_components.garbage_collection.async_setup_entry", return_value=True
    ) as mock_setup_entry, patch(
        "custom_components.garbage_collection.async_setup",
        return_value=True,
    ) as mock_setup:
        result = await hass.config_entries.flow.async_configure(
            result["flow_id"],
            user_input={
                "date": "04/01",
            },
        )
    assert "type" in result and "options" in result
    # Should create entry
    assert result["type"] == data_entry_flow.RESULT_TYPE_CREATE_ENTRY
    assert result["options"] == {"name": "test", "frequency": "annual", "date": "04/01"}
    assert len(mock_setup.mock_calls) == 1
    assert len(mock_setup_entry.mock_calls) == 1


async def test_blank_config_flow(hass: HomeAssistant) -> None:
    """Test we get the form."""
    await setup.async_setup_component(hass, "persistent_notification", {})

    # Initialise Config Flow
    result = await hass.config_entries.flow.async_init(
        DOMAIN, context={"source": config_entries.SOURCE_USER}
    )
    assert "type" in result and "step_id" in result and "flow_id" in result
    # Check that the config flow shows the user form as the first step
    assert result["type"] == data_entry_flow.RESULT_TYPE_FORM
    assert result["step_id"] == "user"

    # If a user were to enter `weekly` for frequency
    # it would result in this function call
    result = await hass.config_entries.flow.async_configure(
        result["flow_id"],
        user_input={"name": "test", "frequency": "blank", "verbose_state": True},
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
    with patch(
        "custom_components.garbage_collection.async_setup_entry", return_value=True
    ) as mock_setup_entry, patch(
        "custom_components.garbage_collection.async_setup",
        return_value=True,
    ) as mock_setup:
        result = await hass.config_entries.flow.async_configure(
            result["flow_id"],
            user_input={
                "date_format": "%d-%b-%Y",
                "verbose_format": "on {date}, in {days} days",
            },
        )
    assert "type" in result and "options" in result
    # Should create entry
    assert result["type"] == data_entry_flow.RESULT_TYPE_CREATE_ENTRY
    assert result["options"] == {
        "name": "test",
        "frequency": "blank",
        "verbose_state": True,
        "date_format": "%d-%b-%Y",
        "verbose_format": "on {date}, in {days} days",
    }
    assert len(mock_setup.mock_calls) == 1
    assert len(mock_setup_entry.mock_calls) == 1


async def test_every_n_days_config_flow(hass: HomeAssistant) -> None:
    """Test we get the form."""
    await setup.async_setup_component(hass, "persistent_notification", {})

    # Initialise Config Flow
    result = await hass.config_entries.flow.async_init(
        DOMAIN, context={"source": config_entries.SOURCE_USER}
    )
    assert "type" in result and "step_id" in result and "flow_id" in result
    # Check that the config flow shows the user form as the first step
    assert result["type"] == data_entry_flow.RESULT_TYPE_FORM
    assert result["step_id"] == "user"

    # If a user were to enter `weekly` for frequency
    # it would result in this function call
    result = await hass.config_entries.flow.async_configure(
        result["flow_id"],
        user_input={"name": "test", "frequency": "every-n-days"},
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
    with patch(
        "custom_components.garbage_collection.async_setup_entry", return_value=True
    ) as mock_setup_entry, patch(
        "custom_components.garbage_collection.async_setup",
        return_value=True,
    ) as mock_setup:
        result = await hass.config_entries.flow.async_configure(
            result["flow_id"],
            user_input={
                "period": 14,
                "first_date": "2020-01-01",
            },
        )
    assert "type" in result and "options" in result
    # Should create entry
    assert result["type"] == data_entry_flow.RESULT_TYPE_CREATE_ENTRY
    assert result["options"] == {
        "name": "test",
        "frequency": "every-n-days",
        "period": 14,
        "first_date": "2020-01-01",
    }
    assert len(mock_setup.mock_calls) == 1
    assert len(mock_setup_entry.mock_calls) == 1


async def test_every_n_weeks_config_flow(hass: HomeAssistant) -> None:
    """Test we get the form."""
    await setup.async_setup_component(hass, "persistent_notification", {})

    # Initialise Config Flow
    result = await hass.config_entries.flow.async_init(
        DOMAIN, context={"source": config_entries.SOURCE_USER}
    )
    assert "type" in result and "step_id" in result and "flow_id" in result
    # Check that the config flow shows the user form as the first step
    assert result["type"] == data_entry_flow.RESULT_TYPE_FORM
    assert result["step_id"] == "user"

    # If a user were to enter `weekly` for frequency
    # it would result in this function call
    result = await hass.config_entries.flow.async_configure(
        result["flow_id"],
        user_input={"name": "test", "frequency": "every-n-weeks"},
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
    with patch(
        "custom_components.garbage_collection.async_setup_entry", return_value=True
    ) as mock_setup_entry, patch(
        "custom_components.garbage_collection.async_setup",
        return_value=True,
    ) as mock_setup:
        result = await hass.config_entries.flow.async_configure(
            result["flow_id"],
            user_input={
                "period": 2,
                "first_week": 3,
                "collection_days": ["wed"],
            },
        )
    assert "type" in result and "options" in result
    # Should create entry
    assert result["type"] == data_entry_flow.RESULT_TYPE_CREATE_ENTRY
    assert result["options"] == {
        "name": "test",
        "frequency": "every-n-weeks",
        "period": 2,
        "first_week": 3,
        "collection_days": ["wed"],
    }
    assert len(mock_setup.mock_calls) == 1
    assert len(mock_setup_entry.mock_calls) == 1


async def test_monthly_config_flow(hass: HomeAssistant) -> None:
    """Test we get the form."""
    await setup.async_setup_component(hass, "persistent_notification", {})

    # Initialise Config Flow
    result = await hass.config_entries.flow.async_init(
        DOMAIN, context={"source": config_entries.SOURCE_USER}
    )
    assert "type" in result and "step_id" in result and "flow_id" in result
    # Check that the config flow shows the user form as the first step
    assert result["type"] == data_entry_flow.RESULT_TYPE_FORM
    assert result["step_id"] == "user"

    # If a user were to enter `weekly` for frequency
    # it would result in this function call
    result = await hass.config_entries.flow.async_configure(
        result["flow_id"],
        user_input={"name": "test", "frequency": "monthly"},
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
    with patch(
        "custom_components.garbage_collection.async_setup_entry", return_value=True
    ) as mock_setup_entry, patch(
        "custom_components.garbage_collection.async_setup",
        return_value=True,
    ) as mock_setup:
        result = await hass.config_entries.flow.async_configure(
            result["flow_id"],
            user_input={
                "collection_days": ["wed"],
                "weekday_order_number": ["1"],
                "period": 1,
            },
        )
    assert "type" in result and "options" in result
    # Should create entry
    assert result["type"] == data_entry_flow.RESULT_TYPE_CREATE_ENTRY
    assert result["options"] == {
        "name": "test",
        "frequency": "monthly",
        "collection_days": ["wed"],
        "weekday_order_number": ["1"],
        "period": 1,
    }
    assert len(mock_setup.mock_calls) == 1
    assert len(mock_setup_entry.mock_calls) == 1


async def test_weekly_config_flow(hass: HomeAssistant) -> None:
    """Test we get the form."""
    await setup.async_setup_component(hass, "persistent_notification", {})

    # Initialise Config Flow
    result = await hass.config_entries.flow.async_init(
        DOMAIN, context={"source": config_entries.SOURCE_USER}
    )
    assert "type" in result and "step_id" in result and "flow_id" in result
    # Check that the config flow shows the user form as the first step
    assert result["type"] == data_entry_flow.RESULT_TYPE_FORM
    assert result["step_id"] == "user"

    # If a user were to enter `weekly` for frequency
    # it would result in this function call
    result = await hass.config_entries.flow.async_configure(
        result["flow_id"],
        user_input={"name": "test", "frequency": "weekly"},
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
    with patch(
        "custom_components.garbage_collection.async_setup_entry", return_value=True
    ) as mock_setup_entry, patch(
        "custom_components.garbage_collection.async_setup",
        return_value=True,
    ) as mock_setup:
        result = await hass.config_entries.flow.async_configure(
            result["flow_id"],
            user_input={"collection_days": ["wed"]},
        )
    assert "type" in result and "options" in result
    # Should create entry
    assert result["type"] == data_entry_flow.RESULT_TYPE_CREATE_ENTRY
    assert result["options"] == {
        "name": "test",
        "frequency": "weekly",
        "collection_days": ["wed"],
    }
    await hass.async_block_till_done()
    assert len(mock_setup.mock_calls) == 1
    assert len(mock_setup_entry.mock_calls) == 1
