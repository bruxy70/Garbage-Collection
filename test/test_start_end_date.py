"""Test start and end date."""
from datetime import date, datetime

from homeassistant.core import HomeAssistant
from pytest_homeassistant_custom_component.common import MockConfigEntry

from custom_components.garbage_collection import const

ERROR_DATETIME = "Next date shold be datetime, not {}."
ERROR_DAYS = "Next collection should be in {} days, not {}."
ERROR_STATE = "State should be {}, not {}."
ERROR_DATE = "Next collection date should be {}, not {}."


async def test_june_july(hass: HomeAssistant) -> None:
    """Start in June."""

    config_entry: MockConfigEntry = MockConfigEntry(
        domain=const.DOMAIN,
        data={
            "frequency": "weekly",
            "collection_days": ["mon"],
            "first_month": "jun",
            "last_month": "jul",
        },
        title="weekly",
        version=5,
    )
    config_entry.add_to_hass(hass)
    await hass.config_entries.async_setup(config_entry.entry_id)
    await hass.async_block_till_done()
    sensor = hass.states.get("sensor.weekly")
    assert sensor is not None
    state = sensor.state
    days = sensor.attributes["days"]
    next_date = sensor.attributes["next_date"]
    assert isinstance(next_date, datetime), ERROR_DATETIME.format(type(next_date))
    assert state == "2", ERROR_STATE.format(2, state)
    assert days == 61, ERROR_DAYS.format(61, days)
    assert next_date.date() == date(2020, 6, 1), ERROR_DATE.format(
        "June 1, 2020", next_date.date()
    )


async def test_dec_jan(hass: HomeAssistant) -> None:
    """Start in Dec."""

    config_entry: MockConfigEntry = MockConfigEntry(
        domain=const.DOMAIN,
        data={
            "frequency": "weekly",
            "collection_days": ["mon"],
            "first_month": "dec",
            "last_month": "jan",
        },
        title="weekly",
        version=5,
    )
    config_entry.add_to_hass(hass)
    await hass.config_entries.async_setup(config_entry.entry_id)
    await hass.async_block_till_done()
    sensor = hass.states.get("sensor.weekly")
    assert sensor is not None
    state = sensor.state
    days = sensor.attributes["days"]
    next_date = sensor.attributes["next_date"]
    assert isinstance(next_date, datetime), ERROR_DATETIME.format(type(next_date))
    assert state == "2", ERROR_STATE.format(2, state)
    assert days == 250, ERROR_DAYS.format(250, days)
    assert next_date.date() == date(2020, 12, 7), ERROR_DATE.format(
        "Dec 7, 2020", next_date.date()
    )
