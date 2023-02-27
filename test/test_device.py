"""Test all frequencies (except blank)."""
import pytest
from homeassistant.core import HomeAssistant
from homeassistant.helpers import device_registry as dr
from homeassistant.helpers import entity_registry as er
from pytest_homeassistant_custom_component.common import MockConfigEntry

from custom_components.garbage_collection import const


@pytest.mark.asyncio
async def test_device(hass: HomeAssistant) -> None:
    """Test device registry."""

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

@pytest.mark.asyncio
async def test_device_info(hass: HomeAssistant) -> None:
    """Test device info."""

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

@pytest.mark.asyncio
async def test_entity(hass: HomeAssistant) -> None:
    """Test entity registry."""

    config_entry: MockConfigEntry = MockConfigEntry(
        domain=const.DOMAIN,
        options={"frequency": "weekly", "collection_days": ["mon"]},
        title="weekly",
        version=6,
    )
    config_entry.add_to_hass(hass)
    await hass.config_entries.async_setup(config_entry.entry_id)
    await hass.async_block_till_done()
    entity_registry = er.async_get(hass)
    entity = entity_registry.async_get_entity_id(
        platform=const.DOMAIN, domain="sensor", unique_id=config_entry.entry_id
    )
    assert entity == "sensor.weekly"
