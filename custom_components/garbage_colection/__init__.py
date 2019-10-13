import logging
from homeassistant import config_entries
from homeassistant.helpers import discovery
from .const import (
    DOMAIN, 
    PLATFORM,
)
from .sensor import CONFIG_SCHEMA, CONF_SENSORS

_LOGGER = logging.getLogger(__name__)


async def async_setup(hass, config):
    """Set up this component using YAML."""
    if config.get(DOMAIN) is None:
        # We get here if the integration is set up using config flow
        return True
    schema_config = CONFIG_SCHEMA(config)
    platform_config = schema_config[DOMAIN].get(CONF_SENSORS, {})
    if not platform_config:
        return False
    for entry in platform_config:
        hass.async_create_task(
            discovery.async_load_platform(
                hass, PLATFORM, DOMAIN, entry, config
            )
        )
    hass.async_create_task(
        hass.config_entries.flow.async_init(
            DOMAIN, context={"source": config_entries.SOURCE_IMPORT}, data={}
        )
    )
    return True


async def async_setup_entry(hass, config_entry):
    """Set up this integration using UI."""
    config_entry.add_update_listener(update_listener)
    config_entry.options = config_entry.data
    # Add sensor
    hass.async_add_job(
        hass.config_entries.async_forward_entry_setup(config_entry, PLATFORM)
    )
    return True


async def update_listener(hass, entry):
    """Update listener."""
    entry.data = entry.options
    await hass.config_entries.async_forward_entry_unload(entry, PLATFORM)
    hass.async_add_job(hass.config_entries.async_forward_entry_setup(entry, PLATFORM))


async def async_remove_entry(hass, config_entry):
    """Handle removal of an entry."""
    try:
        await hass.config_entries.async_forward_entry_unload(config_entry, PLATFORM)
        _LOGGER.info("Successfully removed sensor")
    except ValueError:
        pass
