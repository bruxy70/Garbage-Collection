"""Test all frequencies (except blank)."""
from homeassistant.core import HomeAssistant
from homeassistant.helpers import device_registry as dr
from pytest_homeassistant_custom_component.common import MockConfigEntry

from custom_components.garbage_collection import const


async def test_device(hass: HomeAssistant) -> None:
    """Weekly collection."""

    config_entry: MockConfigEntry = MockConfigEntry(
        domain=const.DOMAIN,
        options={"frequency": "weekly", "collection_days": ["mon"]},
        title="weekly",
        version=6,
    )
    config_entry.add_to_hass(hass)
    await hass.config_entries.async_setup(config_entry.entry_id)
    await hass.async_block_till_done()
    device_registry = dr.async_get(hass)
    device = device_registry.async_get_device(
        identifiers={(const.DOMAIN, config_entry.entry_id)}
    )
    assert device is not None
    assert device.manufacturer == "bruxy70"
    assert device.name == "weekly"


async def test_device_info(hass: HomeAssistant) -> None:
    """Weekly collection."""

    config_entry: MockConfigEntry = MockConfigEntry(
        domain=const.DOMAIN,
        options={"frequency": "weekly", "collection_days": ["mon"]},
        title="weekly",
        version=6,
    )
    config_entry.add_to_hass(hass)
    await hass.config_entries.async_setup(config_entry.entry_id)
    await hass.async_block_till_done()
    sensor = hass.data["garbage_collection"]["sensor"]["sensor.weekly"]
    assert sensor.device_info == {
        "identifiers": {("garbage_collection", sensor.unique_id)},
        "name": None,
        "manufacturer": "bruxy70",
    }
