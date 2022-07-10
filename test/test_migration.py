"""Test migration from older version."""
from homeassistant import config_entries
from homeassistant.core import HomeAssistant
from pytest_homeassistant_custom_component.common import MockConfigEntry

from custom_components.garbage_collection import const


async def test_version1(hass: HomeAssistant) -> None:
    """Migration from version 1."""

    config_entry: MockConfigEntry = MockConfigEntry(
        domain=const.DOMAIN,
        data={"frequency": "weekly", "collection_days": ["mon"], "offset": 1},
        title="weekly",
        version=1,
    )
    config_entry.add_to_hass(hass)
    await hass.config_entries.async_setup(config_entry.entry_id)
    await hass.async_block_till_done()
    assert config_entry.options == {"frequency": "weekly", "collection_days": ["mon"]}
    assert config_entry.data == {}
    assert config_entry.state == config_entries.ConfigEntryState.LOADED


async def test_version4(hass: HomeAssistant) -> None:
    """Migration from version 4."""

    config_entry: MockConfigEntry = MockConfigEntry(
        domain=const.DOMAIN,
        data={
            "frequency": "monthly",
            "weekday_order_number": "2,3",
            "collection_days": ["fri"],
        },
        title="monthly",
        version=4,
    )
    config_entry.add_to_hass(hass)
    await hass.config_entries.async_setup(config_entry.entry_id)
    await hass.async_block_till_done()
    assert config_entry.options == {
        "frequency": "monthly",
        "weekday_order_number": ["2", ",", "3"],
        "collection_days": ["fri"],
    }
    assert config_entry.data == {}
    assert config_entry.state == config_entries.ConfigEntryState.LOADED


async def test_version5(hass: HomeAssistant) -> None:
    """Migration from version 5."""

    config_entry: MockConfigEntry = MockConfigEntry(
        domain=const.DOMAIN,
        data={"frequency": "weekly", "collection_days": ["mon"]},
        title="weekly",
        version=5,
    )
    config_entry.add_to_hass(hass)
    await hass.config_entries.async_setup(config_entry.entry_id)
    await hass.async_block_till_done()
    assert config_entry.options == {"frequency": "weekly", "collection_days": ["mon"]}
    assert config_entry.data == {}
    assert config_entry.state == config_entries.ConfigEntryState.LOADED
