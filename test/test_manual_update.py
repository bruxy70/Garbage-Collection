"""Test manual update services."""
import logging
from datetime import date, datetime
from unittest.mock import patch

import pytest
from homeassistant.core import HomeAssistant
from pytest_homeassistant_custom_component.common import MockConfigEntry

from custom_components.garbage_collection import const
from custom_components.garbage_collection.sensor import GarbageCollection

ERROR_DATETIME = "Next date shold be datetime, not {}."
ERROR_DAYS = "Next collection should be in {} days, not {}."
ERROR_STATE = "State should be {}, not {}."
ERROR_DATE = "Next collection date should be {}, not {}."

@pytest.mark.asyncio
async def test_manual_update(hass: HomeAssistant) -> None:
    """Blank collection."""

    config_entry: MockConfigEntry = MockConfigEntry(
        domain=const.DOMAIN,
        options={
            "name": "test",
            "frequency": "blank",
            "manual_update": True,
        },
        title="blank",
        version=6,
    )
    config_entry.add_to_hass(hass)
    await hass.config_entries.async_setup(config_entry.entry_id)
    await hass.async_block_till_done()
    sensor = hass.states.get("sensor.blank")
    assert sensor is not None
    assert sensor.state == "2"
    assert sensor.attributes["days"] is None
    assert sensor.attributes["next_date"] is None

    logger_sensor = logging.getLogger("custom_components.garbage_collection.sensor")
    # test adding a date
    with patch.object(logger_sensor, "warning") as mock_warning_log:
        await hass.services.async_call(
            const.DOMAIN,
            "add_date",
            service_data={"entity_id": "sensor.blank", "date": date(2020, 4, 1)},
            blocking=True,
        )
        assert (
            mock_warning_log.call_count == 0
        ), "Adding a date should not trigger a warning."
        await hass.services.async_call(
            const.DOMAIN,
            "add_date",
            service_data={"entity_id": "sensor.blank", "date": date(2020, 4, 2)},
            blocking=True,
        )
        assert (
            mock_warning_log.call_count == 0
        ), "Adding a date should not trigger a warning."
        # Trying to add date again. Should trigger a warning
        await hass.services.async_call(
            const.DOMAIN,
            "add_date",
            service_data={"entity_id": "sensor.blank", "date": date(2020, 4, 2)},
            blocking=True,
        )
        assert (
            mock_warning_log.call_count == 1
        ), "Adding same date twice should trigger a warning."

    await hass.services.async_call(
        const.DOMAIN,
        "update_state",
        service_data={"entity_id": "sensor.blank"},
        blocking=True,
    )
    entity: GarbageCollection = hass.data["garbage_collection"]["sensor"][
        "sensor.blank"
    ]
    assert entity.state == 0
    assert entity.extra_state_attributes["days"] == 0
    assert isinstance(entity.extra_state_attributes["next_date"], datetime)
    assert entity.extra_state_attributes["next_date"].date() == date(2020, 4, 1)

    # Test removing a date
    with patch.object(logger_sensor, "warning") as mock_warning_log:
        await hass.services.async_call(
            const.DOMAIN,
            "remove_date",
            service_data={"entity_id": "sensor.blank", "date": date(2020, 4, 1)},
            blocking=True,
        )
        assert (
            mock_warning_log.call_count == 0
        ), "Removing date should not trigger error."
        # Try removing the same date again. Shoudl trigger a warning
        await hass.services.async_call(
            const.DOMAIN,
            "remove_date",
            service_data={"entity_id": "sensor.blank", "date": date(2020, 4, 1)},
            blocking=True,
        )
        assert (
            mock_warning_log.call_count == 1
        ), "Removing date that does not exist should trigger error."
    await hass.services.async_call(
        const.DOMAIN,
        "update_state",
        service_data={"entity_id": "sensor.blank"},
        blocking=True,
    )
    assert entity.state == 1
    assert entity.extra_state_attributes["days"] == 1
    assert isinstance(entity.extra_state_attributes["next_date"], datetime)
    assert entity.extra_state_attributes["next_date"].date() == date(2020, 4, 2)

    # Test ofsetting a date by one day
    await hass.services.async_call(
        const.DOMAIN,
        "offset_date",
        service_data={
            "entity_id": "sensor.blank",
            "date": date(2020, 4, 2),
            "offset": 1,
        },
        blocking=True,
    )
    await hass.services.async_call(
        const.DOMAIN,
        "update_state",
        service_data={"entity_id": "sensor.blank"},
        blocking=True,
    )
    assert entity.state == 2
    assert entity.extra_state_attributes["days"] == 2
    assert isinstance(entity.extra_state_attributes["next_date"], datetime)
    assert entity.extra_state_attributes["next_date"].date() == date(2020, 4, 3)

    # Test calling wih wrong entity_id
    logger_init = logging.getLogger("custom_components.garbage_collection")
    with patch.object(logger_init, "error") as mock_error_log:
        await hass.services.async_call(
            const.DOMAIN,
            "add_date",
            service_data={"entity_id": "sensor.bad", "date": date(2020, 4, 4)},
            blocking=True,
        )
        assert (
            mock_error_log.call_count == 1
        ), "Adding a date with wrong entity_id should trigger an error."
        await hass.services.async_call(
            const.DOMAIN,
            "remove_date",
            service_data={"entity_id": "sensor.bad", "date": date(2020, 4, 3)},
            blocking=True,
        )
        assert (
            mock_error_log.call_count == 2
        ), "Removing a date with wrong entity_id should trigger an error."
        await hass.services.async_call(
            const.DOMAIN,
            "offset_date",
            service_data={
                "entity_id": "sensor.bad",
                "date": date(2020, 4, 3),
                "offset": 1,
            },
            blocking=True,
        )
        assert (
            mock_error_log.call_count == 3
        ), "Offsetting a date with wrong entity_id should trigger an error."
        await hass.services.async_call(
            const.DOMAIN,
            "update_state",
            service_data={"entity_id": "sensor.bad"},
            blocking=True,
        )
        assert (
            mock_error_log.call_count == 4
        ), "Updating state with wrong entity_id should trigger an error."

@pytest.mark.asyncio
async def test_collect_garbage(hass: HomeAssistant) -> None:
    """Test Calling Collect Garbage Service."""

    config_entry: MockConfigEntry = MockConfigEntry(
        domain=const.DOMAIN,
        options={"frequency": "weekly", "collection_days": ["wed"]},
        title="weekly",
        version=6,
    )
    config_entry.add_to_hass(hass)
    await hass.config_entries.async_setup(config_entry.entry_id)
    await hass.async_block_till_done()
    sensor = hass.states.get("sensor.weekly")
    assert sensor is not None
    days = sensor.attributes["days"]
    assert days == 0
    await hass.services.async_call(
        const.DOMAIN,
        "collect_garbage",
        service_data={"entity_id": "sensor.weekly"},
        blocking=True,
    )
    entity: GarbageCollection = hass.data["garbage_collection"]["sensor"][
        "sensor.weekly"
    ]
    assert entity.extra_state_attributes["days"] == 7

    # Test with wrong entity_id
    logger_init = logging.getLogger("custom_components.garbage_collection")
    with patch.object(logger_init, "error") as mock_error_log:
        await hass.services.async_call(
            const.DOMAIN,
            "collect_garbage",
            service_data={"entity_id": "sensor.bad"},
            blocking=True,
        )
        assert (
            mock_error_log.call_count == 1
        ), "Collecting garbage with wrong entity_id should trigger an error."
