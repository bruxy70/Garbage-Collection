"""Test calendar for simple integration."""
from datetime import date, datetime

from homeassistant.core import HomeAssistant
from pytest_homeassistant_custom_component.common import MockConfigEntry

from custom_components.garbage_collection import const


async def test_weekly(hass: HomeAssistant):
    """Weekly collection."""

    config_entry: MockConfigEntry = MockConfigEntry(
        domain=const.DOMAIN,
        data={"frequency": "weekly", "collection_days": ["mon"]},
        title="Weekly",
    )
    config_entry.add_to_hass(hass)
    await hass.config_entries.async_setup(config_entry.entry_id)
    await hass.async_block_till_done()
    weekly = hass.states.get("sensor.weekly")
    state = weekly.state
    next_date = weekly.attributes["next_date"]
    assert state == "2", f"Next holiday should be in 9 days, not {state}"
    assert next_date.date() == date(
        2020, 4, 6
    ), f"Next collection should be April 6, 2020, not {next_date}"
