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
from .calendar import EntitiesCalendarData

from integrationhelper.const import CC_STARTUP_VERSION

from homeassistant.const import CONF_NAME, ATTR_HIDDEN

from .const import (
    CONF_SENSORS,
    CALENDAR_NAME,
    CONF_ENABLED,
    CONF_FREQUENCY,
    DOMAIN,
    ISSUE_URL,
    SENSOR_PLATFORM,
    CALENDAR_PLATFORM,
    VERSION,
    CONFIG_SCHEMA,
)

MIN_TIME_BETWEEN_UPDATES = timedelta(seconds=30)

_LOGGER = logging.getLogger(__name__)


def set_up_calendar(hass, config):
    if config.get(ATTR_HIDDEN, False):
        return
    if CALENDAR_PLATFORM not in hass.data[DOMAIN]:
        hass.data[DOMAIN][CALENDAR_PLATFORM] = EntitiesCalendarData(hass)
        _LOGGER.debug("Creating calendar")
        hass.async_create_task(
            discovery.async_load_platform(
                hass, CALENDAR_PLATFORM, DOMAIN, {"name": CALENDAR_NAME}, config,
            )
        )

async def async_setup(hass, config):
    """Set up this component using YAML."""
    # Create calendar
    if DOMAIN not in hass.data:
        hass.data[DOMAIN] = {}
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
        set_up_calendar(hass, entry)
        _LOGGER.info(
            f"Setting {entry[CONF_NAME]}({entry[CONF_FREQUENCY]}) from YAML configuration"
        )
        # If entry is not enabled, skip.
        # if not entry[CONF_ENABLED]:
        #     continue
        hass.async_create_task(
            discovery.async_load_platform(hass, SENSOR_PLATFORM, DOMAIN, entry, config)
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
    _LOGGER.info(
        f"Setting {config_entry.title}({config_entry.data[CONF_FREQUENCY]}) from ConfigFlow"
    )
    set_up_calendar(hass, config_entry.data)
    # Backward compatibility - clean-up (can be removed later?)
    config_entry.options = {}
    config_entry.add_update_listener(update_listener)
    # Add sensor
    hass.async_add_job(
        hass.config_entries.async_forward_entry_setup(config_entry, SENSOR_PLATFORM)
    )
    return True


async def async_remove_entry(hass, config_entry):
    """Handle removal of an entry."""
    try:
        await hass.config_entries.async_forward_entry_unload(
            config_entry, SENSOR_PLATFORM
        )
        _LOGGER.info(
            "Successfully removed sensor from the garbage_collection integration"
        )
    except ValueError:
        pass


async def update_listener(hass, entry):
    """Update listener."""
    # The OptionsFlow saves data to options. Move them back to data and clean options (dirty, but not sure how else to do that)
    if entry.options != {}:
        entry.data = entry.options
        entry.options = {}
    await hass.config_entries.async_forward_entry_unload(entry, SENSOR_PLATFORM)
    hass.async_add_job(
        hass.config_entries.async_forward_entry_setup(entry, SENSOR_PLATFORM)
    )
