"""Diagnostics support for Garbage Collection."""
from __future__ import annotations

from typing import Any

from homeassistant.components.diagnostics import async_redact_data
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant

from . import const


async def async_get_config_entry_diagnostics(
    hass: HomeAssistant,
    entry: ConfigEntry,
) -> dict[str, Any]:
    """Return diagnostics for a config entry."""
    entities = hass.data[const.DOMAIN][const.SENSOR_PLATFORM]
    entity_data = [
        entities[entity]
        for entity in entities
        if entities[entity].unique_id == entry.data["unique_id"]
    ][0]
    data = {
        "entry": entry.as_dict(),
        "entity": entity_data,
    }
    return async_redact_data(data, (const.TOKEN,))
