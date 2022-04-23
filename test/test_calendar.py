"""Test all frequencies (except blank)."""

from custom_components.garbage_collection import const
from homeassistant.core import HomeAssistant
from pytest_homeassistant_custom_component.common import MockConfigEntry


async def test_calendar(hass: HomeAssistant) -> None:
    """Weekly collection."""

    config_entry: MockConfigEntry = MockConfigEntry(
        domain=const.DOMAIN,
        data={"frequency": "weekly", "collection_days": ["mon"]},
        title="calendar",
        version=4.5,
    )
    config_entry.add_to_hass(hass)
    await hass.config_entries.async_setup(config_entry.entry_id)
    await hass.async_block_till_done()
    calendar = hass.states.get("calendar.garbage_collection")
    assert calendar is not None
    assert calendar.attributes["message"] == "calendar"
    assert calendar.state == "off"
    start_time = calendar.attributes["start_time"]
    end_time = calendar.attributes["end_time"]
    assert start_time == "2020-04-06 00:00:00"
    assert end_time == "2020-04-07 00:00:00"
