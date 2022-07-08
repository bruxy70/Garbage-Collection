"""Test verbose state."""
from homeassistant.core import HomeAssistant
from pytest_homeassistant_custom_component.common import MockConfigEntry

from custom_components.garbage_collection import const

ERROR_STATE = "State should be {}, not {}."


async def test_verbose_state(hass: HomeAssistant) -> None:
    """Start in June."""

    config_entry: MockConfigEntry = MockConfigEntry(
        domain=const.DOMAIN,
        options={
            "frequency": "weekly",
            "collection_days": ["mon"],
            "verbose_state": True,
            "verbose_format": "on {date}, in {days} days",
        },
        title="weekly",
        version=6,
    )
    config_entry.add_to_hass(hass)
    await hass.config_entries.async_setup(config_entry.entry_id)
    await hass.async_block_till_done()
    sensor = hass.states.get("sensor.weekly")
    assert sensor is not None
    state = sensor.state
    assert state == "on 06-Apr-2020, in 5 days", ERROR_STATE.format(
        "on 06-Apr-2020, in 5 days", state
    )
