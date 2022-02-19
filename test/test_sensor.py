"""Test calendar for simple integration."""
from datetime import date

from custom_components.garbage_collection import const
from homeassistant.core import HomeAssistant
from pytest_homeassistant_custom_component.common import MockConfigEntry


async def test_weekly(hass: HomeAssistant):
    """Weekly collection."""

    config_entry: MockConfigEntry = MockConfigEntry(
        domain=const.DOMAIN,
        data={"frequency": "weekly", "collection_days": ["mon"]},
        title="sensor",
        version=4.5,
    )
    config_entry.add_to_hass(hass)
    await hass.config_entries.async_setup(config_entry.entry_id)
    await hass.async_block_till_done()
    sensor = hass.states.get("sensor.sensor")
    state = sensor.state
    days = sensor.attributes["days"]
    next_date = sensor.attributes["next_date"]
    assert state == "2", f"State should be 2, not {state}"
    assert days == 5, f"Should be in 5 dats, not {days}"
    assert next_date.date() == date(
        2020, 4, 6
    ), f"Next collection should be April 6, 2020, not {next_date}"


async def test_odd_weeks(hass: HomeAssistant):
    """Odd Weeks collection."""

    config_entry: MockConfigEntry = MockConfigEntry(
        domain=const.DOMAIN,
        data={"frequency": "odd-weeks", "collection_days": ["tue"]},
        title="sensor",
        version=4.5,
    )
    config_entry.add_to_hass(hass)
    await hass.config_entries.async_setup(config_entry.entry_id)
    await hass.async_block_till_done()
    sensor = hass.states.get("sensor.sensor")
    state = sensor.state
    days = sensor.attributes["days"]
    next_date = sensor.attributes["next_date"]
    assert state == "2", f"State should be 2, not {state}"
    assert days == 6, f"Should be in 6 days, not {days}"
    assert next_date.date() == date(2020, 4, 7), f"Should be April 7, not {next_date}"


async def test_even_weeks(hass: HomeAssistant):
    """Even Weeks collection."""

    config_entry: MockConfigEntry = MockConfigEntry(
        domain=const.DOMAIN,
        data={"frequency": "even-weeks", "collection_days": ["wed"]},
        title="sensor",
        version=4.5,
    )
    config_entry.add_to_hass(hass)
    await hass.config_entries.async_setup(config_entry.entry_id)
    await hass.async_block_till_done()
    sensor = hass.states.get("sensor.sensor")
    state = sensor.state
    days = sensor.attributes["days"]
    next_date = sensor.attributes["next_date"]
    assert state == "0", f"State should be 0, not {state}"
    assert days == 0, f"Days should be 0, not {days}"
    assert next_date.date() == date(
        2020, 4, 1
    ), f"Next date should be April 1, not {next_date}"


# async def test_every_n_days(hass: HomeAssistant):
#     """Every n days collection."""

#     config_entry: MockConfigEntry = MockConfigEntry(
#         domain=const.DOMAIN,
#         data={
#             "frequency": "every-n-days",
#             "period": 14,
#             "first-date": "2020-01-01",
#         },
#         title="sensor",
#         version=4.5,
#     )
#     config_entry.add_to_hass(hass)
#     await hass.config_entries.async_setup(config_entry.entry_id)
#     await hass.async_block_till_done()
#     sensor = hass.states.get("sensor.sensor")
#     state = sensor.state
#     days = sensor.attributes["days"]
#     next_date = sensor.attributes["next_date"]
#     assert state == "2", f"State should be 2, not {state}"
#     assert days
#     assert next_date.date()


# async def test_every_n_weeks(hass: HomeAssistant):
#     """Every n weeks collection."""

#     config_entry: MockConfigEntry = MockConfigEntry(
#         domain=const.DOMAIN,
#         data={
#             "frequency": "every-n-weeks",
#             "period": 2,
#             "first-week": 3,
#             "weekday-order-number": ["3"]
#             "collection_days": ["wed"],
#         },
#         title="sensor",
#         version=4.5,
#     )
#     config_entry.add_to_hass(hass)
#     await hass.config_entries.async_setup(config_entry.entry_id)
#     await hass.async_block_till_done()
#     sensor = hass.states.get("sensor.sensor")
#     state = sensor.state
#     days = sensor.attributes["days"]
#     next_date = sensor.attributes["next_date"]
#     assert state == "2", f"State should be 2, not {state}"
#     assert days
#     assert next_date.date()


async def test_monthly(hass: HomeAssistant):
    """Monthly collection."""

    config_entry: MockConfigEntry = MockConfigEntry(
        domain=const.DOMAIN,
        data={
            "frequency": "monthly",
            "weekday_order_number": "2",
            "collection_days": ["fri"],
        },
        title="sensor",
        version=4.5,
    )
    config_entry.add_to_hass(hass)
    await hass.config_entries.async_setup(config_entry.entry_id)
    await hass.async_block_till_done()
    sensor = hass.states.get("sensor.sensor")
    state = sensor.state
    days = sensor.attributes["days"]
    next_date = sensor.attributes["next_date"]
    assert state == "2", f"State should be 2, not {state}"
    assert days == 9, f"Days should be 9, not {days}"
    assert next_date.date() == date(
        2020, 4, 10
    ), f"Next date should be April 10, not {next_date}"


async def test_monthly2(hass: HomeAssistant):
    """Monday in 2nd week, not 2nd monday of month."""

    config_entry: MockConfigEntry = MockConfigEntry(
        domain=const.DOMAIN,
        data={
            "frequency": "monthly",
            "weekday_order_number": "2",
            "force_week_order_numbers": True,
            "collection_days": ["mon"],
        },
        title="sensor",
        version=4.5,
    )
    config_entry.add_to_hass(hass)
    await hass.config_entries.async_setup(config_entry.entry_id)
    await hass.async_block_till_done()
    sensor = hass.states.get("sensor.sensor")
    state = sensor.state
    days = sensor.attributes["days"]
    next_date = sensor.attributes["next_date"]
    assert state == "2", f"State should be 2, not {state}"
    assert days == 5, f"Days should be 5, not {days}"
    assert next_date.date() == date(
        2020, 4, 6
    ), f"Next date should be April 6, not {next_date}"


async def test_annual(hass: HomeAssistant):
    """Annual collection."""

    config_entry: MockConfigEntry = MockConfigEntry(
        domain=const.DOMAIN,
        data={
            "frequency": "annual",
            "date": "05/01",
        },
        title="sensor",
        version=4.5,
    )
    config_entry.add_to_hass(hass)
    await hass.config_entries.async_setup(config_entry.entry_id)
    await hass.async_block_till_done()
    sensor = hass.states.get("sensor.sensor")
    state = sensor.state
    days = sensor.attributes["days"]
    next_date = sensor.attributes["next_date"]
    assert state == "2", f"State should be 2, not {state}"
    assert days == 30, f"Days should be 30, not {days}"
    assert next_date.date() == date(
        2020, 5, 1
    ), f"Next date should be May 1, not {next_date}"
