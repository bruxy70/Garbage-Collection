"""
Component to integrate with garbage_colection.
"""
import os
from datetime import timedelta
import logging
from homeassistant import config_entries
import voluptuous as vol
import homeassistant.helpers.config_validation as cv
from homeassistant.helpers import discovery
from homeassistant.util import Throttle
from .sensor import GarbageCollection

from integrationhelper.const import CC_STARTUP_VERSION

from homeassistant.const import CONF_NAME

from .const import (
    CONF_SENSORS,
    CONF_ENABLED,
    CONF_FREQUENCY,
    DEFAULT_NAME,
    DOMAIN_DATA,
    DOMAIN,
    ISSUE_URL,
    PLATFORM,
    VERSION,
    CONFIG_SCHEMA,
)

MIN_TIME_BETWEEN_UPDATES = timedelta(seconds=30)

_LOGGER = logging.getLogger(__name__)


async def async_setup(hass, config):
    """Set up this component using YAML."""
    if config.get(DOMAIN) is None:
        # We get here if the integration is set up using config flow
        return True

    # Print startup message
    _LOGGER.info(
        CC_STARTUP_VERSION.format(name=DOMAIN, version=VERSION, issue_link=ISSUE_URL)
    )
    platform_config = config[DOMAIN].get(CONF_SENSORS, {})

    # If platform is not enabled, skip.
    if not platform_config:
        return False

    for entry in platform_config:
        # If entry is not enabled, skip.
        # if not entry[CONF_ENABLED]:
        #     continue
        hass.async_create_task(
            discovery.async_load_platform(hass, PLATFORM, DOMAIN, entry, config)
        )
    hass.async_create_task(
        hass.config_entries.flow.async_init(
            DOMAIN, context={"source": config_entries.SOURCE_IMPORT}, data={}
        )
    )
    return True


async def async_setup_entry(hass, config_entry):
    """Set up this integration using UI."""
    if config_entry.source == config_entries.SOURCE_IMPORT:
        # We get here if the integration is set up using YAML
        hass.async_create_task(hass.config_entries.async_remove(config_entry.entry_id))
        return False
    # Print startup message
    _LOGGER.info(
        CC_STARTUP_VERSION.format(name=DOMAIN, version=VERSION, issue_link=ISSUE_URL)
    )
    config_entry.options = config_entry.data
    config_entry.add_update_listener(update_listener)
    # Add sensor
    hass.async_add_job(
        hass.config_entries.async_forward_entry_setup(config_entry, PLATFORM)
    )
    return True


async def async_remove_entry(hass, config_entry):
    """Handle removal of an entry."""
    try:
        await hass.config_entries.async_forward_entry_unload(config_entry, PLATFORM)
        _LOGGER.info(
            "Successfully removed sensor from the garbage_collection integration"
        )
    except ValueError:
        pass


async def update_listener(hass, entry):
    """Update listener."""
    entry.data = entry.options
    await hass.config_entries.async_forward_entry_unload(entry, PLATFORM)
    hass.async_add_job(hass.config_entries.async_forward_entry_setup(entry, PLATFORM))
