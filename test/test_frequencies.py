"""Test all frequencies (except blank)."""
from datetime import date, datetime

from homeassistant.core import HomeAssistant
from pytest_homeassistant_custom_component.common import MockConfigEntry

from custom_components.garbage_collection import const

ERROR_DATETIME = "Next date shold be datetime, not {}."
ERROR_DAYS = "Next collection should be in {} days, not {}."
ERROR_STATE = "State should be {}, not {}."
ERROR_DATE = "Next collection date should be {}, not {}."


async def test_annual(hass: HomeAssistant) -> None:
    """Annual collection."""

    config_entry: MockConfigEntry = MockConfigEntry(
        domain=const.DOMAIN,
        data={
            "frequency": "annual",
            "date": "05/01",
        },
        title="annual",
        version=4.5,
    )
    config_entry.add_to_hass(hass)
    await hass.config_entries.async_setup(config_entry.entry_id)
    await hass.async_block_till_done()
    sensor = hass.states.get("sensor.annual")
    state = sensor.state
    days = sensor.attributes["days"]
    next_date = sensor.attributes["next_date"]
    assert isinstance(next_date, datetime), ERROR_DATETIME.format(type(next_date))
    assert state == "2", ERROR_STATE.format(2, state)
    assert days == 30, ERROR_DAYS.format(30, days)
    assert next_date.date() == date(2020, 5, 1), ERROR_DATE.format(
        "May 1, 2020", next_date.date()
    )


async def test_even_weeks(hass: HomeAssistant) -> None:
    """Even Weeks collection."""

    config_entry: MockConfigEntry = MockConfigEntry(
        domain=const.DOMAIN,
        data={"frequency": "even-weeks", "collection_days": ["wed"]},
        title="even weeks",
        version=4.5,
    )
    config_entry.add_to_hass(hass)
    await hass.config_entries.async_setup(config_entry.entry_id)
    await hass.async_block_till_done()
    sensor = hass.states.get("sensor.even_weeks")
    state = sensor.state
    days = sensor.attributes["days"]
    next_date = sensor.attributes["next_date"]
    assert isinstance(next_date, datetime), ERROR_DATETIME.format(type(next_date))
    assert state == "0", ERROR_STATE.format(0, state)
    assert days == 0, ERROR_DAYS.format(0, days)
    assert next_date.date() == date(2020, 4, 1), ERROR_DATE.format(
        "April 1, 2020", next_date.date()
    )


async def test_every_n_days(hass: HomeAssistant) -> None:
    """Every n days collection."""

    config_entry: MockConfigEntry = MockConfigEntry(
        domain=const.DOMAIN,
        data={
            "frequency": "every-n-days",
            "period": 14,
            "first_date": "2020-01-01",
        },
        title="every n days",
        version=4.5,
    )
    config_entry.add_to_hass(hass)
    await hass.config_entries.async_setup(config_entry.entry_id)
    await hass.async_block_till_done()
    sensor = hass.states.get("sensor.every_n_days")
    state = sensor.state
    days = sensor.attributes["days"]
    next_date = sensor.attributes["next_date"]
    assert isinstance(next_date, datetime), ERROR_DATETIME.format(type(next_date))
    assert state == "2", ERROR_STATE.format(2, state)
    assert days == 7, ERROR_DAYS.format(7, days)
    assert next_date.date() == date(2020, 4, 8), ERROR_DATE.format(
        "April 8, 2020", next_date.date()
    )


async def test_every_n_weeks(hass: HomeAssistant) -> None:
    """Every n weeks collection."""

    config_entry: MockConfigEntry = MockConfigEntry(
        domain=const.DOMAIN,
        data={
            "frequency": "every-n-weeks",
            "period": 2,
            "first_week": 3,
            "collection_days": ["wed"],
        },
        title="every n weeks",
        version=4.5,
    )
    config_entry.add_to_hass(hass)
    await hass.config_entries.async_setup(config_entry.entry_id)
    await hass.async_block_till_done()
    sensor = hass.states.get("sensor.every_n_weeks")
    state = sensor.state
    days = sensor.attributes["days"]
    next_date = sensor.attributes["next_date"]
    assert isinstance(next_date, datetime), ERROR_DATETIME.format(type(next_date))
    assert state == "2", ERROR_STATE.format(2, state)
    assert days == 7, ERROR_DAYS.format(7, days)
    assert next_date.date() == date(2020, 4, 8), ERROR_DATE.format(
        "April 8, 2020", next_date.date()
    )


async def test_monthly(hass: HomeAssistant) -> None:
    """Monthly collection."""

    config_entry: MockConfigEntry = MockConfigEntry(
        domain=const.DOMAIN,
        data={
            "frequency": "monthly",
            "weekday_order_number": ["2"],
            "collection_days": ["fri"],
        },
        title="monthly",
        version=4.5,
    )
    config_entry.add_to_hass(hass)
    await hass.config_entries.async_setup(config_entry.entry_id)
    await hass.async_block_till_done()
    sensor = hass.states.get("sensor.monthly")
    state = sensor.state
    days = sensor.attributes["days"]
    next_date = sensor.attributes["next_date"]
    assert isinstance(next_date, datetime), ERROR_DATETIME.format(type(next_date))
    assert state == "2", ERROR_STATE.format(2, state)
    assert days == 9, ERROR_DAYS.format(9, days)
    assert next_date.date() == date(2020, 4, 10), ERROR_DATE.format(
        "April 10, 2020", next_date.date()
    )


async def test_monthly2(hass: HomeAssistant) -> None:
    """Monday in 2nd week, not 2nd monday of month."""

    config_entry: MockConfigEntry = MockConfigEntry(
        domain=const.DOMAIN,
        data={
            "frequency": "monthly",
            "weekday_order_number": ["2"],
            "force_week_order_numbers": True,
            "collection_days": ["mon"],
        },
        title="monthly 2",
        version=4.5,
    )
    config_entry.add_to_hass(hass)
    await hass.config_entries.async_setup(config_entry.entry_id)
    await hass.async_block_till_done()
    sensor = hass.states.get("sensor.monthly_2")
    state = sensor.state
    days = sensor.attributes["days"]
    next_date = sensor.attributes["next_date"]
    assert isinstance(next_date, datetime), ERROR_DATETIME.format(type(next_date))
    assert state == "2", ERROR_STATE.format(2, state)
    assert days == 5, ERROR_DAYS.format(5, days)
    assert next_date.date() == date(2020, 4, 6), ERROR_DATE.format(
        "April 6, 2020", next_date.date()
    )


async def test_odd_weeks(hass: HomeAssistant) -> None:
    """Odd Weeks collection."""

    config_entry: MockConfigEntry = MockConfigEntry(
        domain=const.DOMAIN,
        data={"frequency": "odd-weeks", "collection_days": ["tue"]},
        title="odd weeks",
        version=4.5,
    )
    config_entry.add_to_hass(hass)
    await hass.config_entries.async_setup(config_entry.entry_id)
    await hass.async_block_till_done()
    sensor = hass.states.get("sensor.odd_weeks")
    state = sensor.state
    days = sensor.attributes["days"]
    next_date = sensor.attributes["next_date"]
    assert isinstance(next_date, datetime), ERROR_DATETIME.format(type(next_date))
    assert state == "2", ERROR_STATE.format(2, state)
    assert days == 6, ERROR_DAYS.format(5, days)
    assert next_date.date() == date(2020, 4, 7), ERROR_DATE.format(
        "April 7, 2020", next_date.date()
    )


async def test_weekly(hass: HomeAssistant) -> None:
    """Weekly collection."""

    config_entry: MockConfigEntry = MockConfigEntry(
        domain=const.DOMAIN,
        data={"frequency": "weekly", "collection_days": ["mon"]},
        title="weekly",
        version=4.5,
    )
    config_entry.add_to_hass(hass)
    await hass.config_entries.async_setup(config_entry.entry_id)
    await hass.async_block_till_done()
    sensor = hass.states.get("sensor.weekly")
    state = sensor.state
    days = sensor.attributes["days"]
    next_date = sensor.attributes["next_date"]
    assert isinstance(next_date, datetime), ERROR_DATETIME.format(type(next_date))
    assert state == "2", ERROR_STATE.format(2, state)
    assert days == 5, ERROR_DAYS.format(5, days)
    assert next_date.date() == date(2020, 4, 6), ERROR_DATE.format(
        "April 6, 2020", next_date.date()
    )
