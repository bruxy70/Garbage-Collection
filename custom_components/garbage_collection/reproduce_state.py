"""Reproduce an Input number state."""
import asyncio
import logging
from datetime import datetime
from typing import Any, Dict, Iterable, Optional

import voluptuous as vol
from homeassistant.const import ATTR_ENTITY_ID
from homeassistant.core import Context, State
from homeassistant.helpers.typing import HomeAssistantType

from .const import ATTR_LAST_COLLECTION, DOMAIN

_LOGGER = logging.getLogger(__name__)


async def _async_reproduce_state(
    hass: HomeAssistantType,
    state: State,
    *,
    context: Optional[Context] = None,
    reproduce_options: Optional[Dict[str, Any]] = None,
) -> None:
    """Reproduce a single state."""
    state_object = hass.states.get(state.entity_id)

    if state_object is None:
        _LOGGER.warning("Unable to find entity %s", state.entity_id)
        return
    
    _LOGGER.debug("Restoring %s state: state:%s, attributes:%s", state.entity_id, state.state, state.attributes)
    
    try:
        datetime(state.attributes.get(ATTR_LAST_COLLECTION))
    except ValueError:
        _LOGGER.warning(
            "Invalid state specified for %s: %s",
            state.entity_id,
            state.attributes.get(ATTR_LAST_COLLECTION),
        )
        return

    # Return if we are already at the right state.
    if state_object.attributes.get(ATTR_LAST_COLLECTION) == state.attributes.get(
        ATTR_LAST_COLLECTION
    ):
        return

    service_data = {
        ATTR_ENTITY_ID: state.entity_id,
        ATTR_LAST_COLLECTION: state.attributes.get(ATTR_LAST_COLLECTION).strftime(
            "%Y-%m-%d %H:%M:%S"
        ),
    }

    try:
        await hass.services.async_call(
            DOMAIN, "collect_garbage", service_data, context=context, blocking=True
        )
    except vol.Invalid as err:
        # If value out of range.
        _LOGGER.warning("Unable to reproduce state for %s: %s", state.entity_id, err)


async def async_reproduce_states(
    hass: HomeAssistantType,
    states: Iterable[State],
    *,
    context: Optional[Context] = None,
    reproduce_options: Optional[Dict[str, Any]] = None,
) -> None:
    """Reproduce garbage collection states."""
    # Reproduce states in parallel.
    await asyncio.gather(
        *(
            _async_reproduce_state(
                hass, state, context=context, reproduce_options=reproduce_options
            )
            for state in states
        )
    )
