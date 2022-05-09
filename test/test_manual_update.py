"""Test manual update services."""
import logging
from datetime import date, datetime
from unittest.mock import patch

from custom_components.garbage_collection import const
from custom_components.garbage_collection.sensor import GarbageCollection
from homeassistant.core import HomeAssistant
from pytest_homeassistant_custom_component.common import MockConfigEntry

ERROR_DATETIME = "Next date shold be datetime, not {}."
ERROR_DAYS = "Next collection should be in {} days, not {}."
ERROR_STATE = "State should be {}, not {}."
ERROR_DATE = "Next collection date should be {}, not {}."


async def test_manual_update(hass: HomeAssistant) -> None:
    """Blank collection."""

    config_entry: MockConfigEntry = MockConfigEntry(
        domain=const.DOMAIN,
        data={
            "name": "test",
            "frequency": "blank",
            "manual_update": True,
        },
        title="blank",
        version=4.5,
    )
    config_entry.add_to_hass(hass)
    await hass.config_entries.async_setup(config_entry.entry_id)
    await hass.async_block_till_done()
    sensor = hass.states.get("sensor.blank")
    assert sensor is not None
    assert sensor.state == "2"
    assert sensor.attributes["days"] is None
    assert sensor.attributes["next_date"] is None

    logger = logging.getLogger("custom_components.garbage_collection.sensor")
    with patch.object(logger, "error") as mock_error_log:
        await hass.services.async_call(
            const.DOMAIN,
            "add_date",
            service_data={"entity_id": "sensor.blank", "date": date(2020, 4, 1)},
            blocking=True,
        )
        assert mock_error_log.call_count == 0
        await hass.services.async_call(
            const.DOMAIN,
            "add_date",
            service_data={"entity_id": "sensor.blank", "date": date(2020, 4, 2)},
            blocking=True,
        )
        assert mock_error_log.call_count == 0
        await hass.services.async_call(
            const.DOMAIN,
            "add_date",
            service_data={"entity_id": "sensor.blank", "date": date(2020, 4, 2)},
            blocking=True,
        )
        assert mock_error_log.call_count == 1
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
    await hass.services.async_call(
        const.DOMAIN,
        "remove_date",
        service_data={"entity_id": "sensor.blank", "date": date(2020, 4, 1)},
        blocking=True,
    )
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
