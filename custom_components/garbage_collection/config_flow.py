"""Adds config flow for GarbageCollection."""
from __future__ import annotations

import logging

# import uuid
from collections.abc import Mapping
from typing import Any, Dict, cast

import homeassistant.helpers.config_validation as cv
import voluptuous as vol
from homeassistant.const import ATTR_HIDDEN, CONF_ENTITIES, CONF_NAME, WEEKDAYS
from homeassistant.core import callback
from homeassistant.helpers import selector
from homeassistant.helpers.schema_config_entry_flow import (
    SchemaConfigFlowHandler,
    SchemaFlowError,
    SchemaFlowFormStep,
    SchemaFlowMenuStep,
    SchemaOptionsFlowHandler,
)

from . import const, helpers

_LOGGER = logging.getLogger(__name__)


async def _validate_config(
    handler: SchemaConfigFlowHandler | SchemaOptionsFlowHandler, data: Any
) -> Any:
    """Validate config."""
    if const.CONF_DATE in data:
        try:
            helpers.month_day_text(data[const.CONF_DATE])
        except vol.Invalid as exc:
            raise SchemaFlowError("month_day") from exc
    return data


def required(
    key: str, options: Dict[str, Any], default: Any | None = None
) -> vol.Required:
    """Return vol.Required."""
    if isinstance(options, dict) and key in options:
        suggested_value = options[key]
    elif default is not None:
        suggested_value = default
    else:
        return vol.Required(key)
    return vol.Required(key, description={"suggested_value": suggested_value})


def optional(
    key: str, options: Dict[str, Any], default: Any | None = None
) -> vol.Optional:
    """Return vol.Optional."""
    if isinstance(options, dict) and key in options:
        suggested_value = options[key]
    elif default is not None:
        suggested_value = default
    else:
        return vol.Optional(key)
    return vol.Optional(key, description={"suggested_value": suggested_value})


async def general_options_schema(
    handler: SchemaConfigFlowHandler | SchemaOptionsFlowHandler,
) -> vol.Schema:
    """Generate options schema."""
    return vol.Schema(
        {
            required(
                const.CONF_FREQUENCY, handler.options, const.DEFAULT_FREQUENCY
            ): vol.In(const.FREQUENCY_OPTIONS),
            optional(
                const.CONF_ICON_NORMAL, handler.options, const.DEFAULT_ICON_NORMAL
            ): selector.IconSelector(),
            optional(
                const.CONF_ICON_TODAY, handler.options, const.DEFAULT_ICON_TODAY
            ): selector.IconSelector(),
            optional(
                const.CONF_ICON_TOMORROW, handler.options, const.DEFAULT_ICON_TOMORROW
            ): selector.IconSelector(),
            optional(const.CONF_EXPIRE_AFTER, handler.options): selector.TimeSelector(),
            optional(
                const.CONF_VERBOSE_STATE, handler.options, const.DEFAULT_VERBOSE_STATE
            ): bool,
            optional(ATTR_HIDDEN, handler.options, False): bool,
            optional(const.CONF_MANUAL, handler.options, False): bool,
        }
    )


async def general_config_schema(
    handler: SchemaConfigFlowHandler | SchemaOptionsFlowHandler,
) -> vol.Schema:
    """Generate config schema."""
    return vol.Schema(
        {
            optional(CONF_NAME, handler.options): selector.TextSelector(),
            required(
                const.CONF_FREQUENCY, handler.options, const.DEFAULT_FREQUENCY
            ): vol.In(const.FREQUENCY_OPTIONS),
            optional(
                const.CONF_ICON_NORMAL, handler.options, const.DEFAULT_ICON_NORMAL
            ): selector.IconSelector(),
            optional(
                const.CONF_ICON_TODAY, handler.options, const.DEFAULT_ICON_TODAY
            ): selector.IconSelector(),
            optional(
                const.CONF_ICON_TOMORROW, handler.options, const.DEFAULT_ICON_TOMORROW
            ): selector.IconSelector(),
            optional(const.CONF_EXPIRE_AFTER, handler.options): selector.TimeSelector(),
            optional(
                const.CONF_VERBOSE_STATE, handler.options, const.DEFAULT_VERBOSE_STATE
            ): bool,
            optional(ATTR_HIDDEN, handler.options, False): bool,
            optional(const.CONF_MANUAL, handler.options, False): bool,
        }
    )


async def detail_config_schema(
    handler: SchemaConfigFlowHandler | SchemaOptionsFlowHandler,
) -> vol.Schema:
    """Generate options schema."""
    options_schema: Dict[vol.Optional | vol.Required, Any] = {}
    if handler.options[const.CONF_FREQUENCY] in const.ANNUAL_FREQUENCY:
        # "annual"
        options_schema[required(const.CONF_DATE, handler.options)] = str
    elif handler.options[const.CONF_FREQUENCY] in const.GROUP_FREQUENCY:
        # "group"
        options_schema[
            required(CONF_ENTITIES, handler.options)
        ] = selector.EntitySelector(
            selector.EntitySelectorConfig(
                domain="sensor", integration=const.DOMAIN, multiple=True
            ),
        )
    elif handler.options[const.CONF_FREQUENCY] not in const.BLANK_FREQUENCY:
        # everything else except "blank" and every-n-days
        if handler.options[const.CONF_FREQUENCY] not in const.DAILY_FREQUENCY:
            weekdays_dict = {weekday: weekday for weekday in WEEKDAYS}
            options_schema[
                required(const.CONF_COLLECTION_DAYS, handler.options)
            ] = cv.multi_select(weekdays_dict)
        # everything else except "blank"
        options_schema[
            optional(const.CONF_FIRST_MONTH, handler.options, const.DEFAULT_FIRST_MONTH)
        ] = vol.In(const.MONTH_OPTIONS)
        options_schema[
            optional(const.CONF_LAST_MONTH, handler.options, const.DEFAULT_LAST_MONTH)
        ] = vol.In(const.MONTH_OPTIONS)
        if handler.options[const.CONF_FREQUENCY] in const.MONTHLY_FREQUENCY:
            # "monthly"
            options_schema[
                optional(const.CONF_WEEKDAY_ORDER_NUMBER, handler.options)
            ] = vol.All(
                cv.multi_select(
                    {"1": "1st", "2": "2nd", "3": "3rd", "4": "4th", "5": "5th"}
                ),
            )
            options_schema[
                optional(const.CONF_FORCE_WEEK_NUMBERS, handler.options)
            ] = bool
        if handler.options[const.CONF_FREQUENCY] in const.WEEKLY_DAILY_MONTHLY:
            # "every-n-weeks", "every-n-days", "monthly"
            options_schema[required(const.CONF_PERIOD, handler.options)] = vol.All(
                vol.Coerce(int), vol.Range(min=1, max=1000)
            )
        if handler.options[const.CONF_FREQUENCY] in const.WEEKLY_FREQUENCY_X:
            # every-n-weeks
            options_schema[
                required(
                    const.CONF_FIRST_WEEK, handler.options, const.DEFAULT_FIRST_WEEK
                )
            ] = vol.All(vol.Coerce(int), vol.Range(min=1, max=52))
        if handler.options[const.CONF_FREQUENCY] in const.DAILY_FREQUENCY:
            # every-n-days
            options_schema[
                required(const.CONF_FIRST_DATE, handler.options)
            ] = selector.DateSelector()
    if handler.options.get(const.CONF_VERBOSE_STATE, False):
        # "verbose_state"
        options_schema[
            required(
                const.CONF_VERBOSE_FORMAT, handler.options, const.DEFAULT_VERBOSE_FORMAT
            )
        ] = cv.string
        options_schema[
            required(const.CONF_DATE_FORMAT, handler.options, const.DEFAULT_DATE_FORMAT)
        ] = cv.string
    return vol.Schema(options_schema)


async def choose_details_step(options: dict[str, Any]) -> str:
    """Return next step_id for options flow."""
    return "detail"


CONFIG_FLOW: Dict[str, SchemaFlowFormStep | SchemaFlowMenuStep] = {
    "user": SchemaFlowFormStep(general_config_schema, next_step=choose_details_step),
    "detail": SchemaFlowFormStep(
        detail_config_schema, validate_user_input=_validate_config
    ),
}
OPTIONS_FLOW: Dict[str, SchemaFlowFormStep | SchemaFlowMenuStep] = {
    "init": SchemaFlowFormStep(general_options_schema, next_step=choose_details_step),
    "detail": SchemaFlowFormStep(
        detail_config_schema, validate_user_input=_validate_config
    ),
}


# mypy: ignore-errors
class GarbageCollectionConfigFlowHandler(SchemaConfigFlowHandler, domain=const.DOMAIN):
    """Handle a config or options flow for GarbageCollection."""

    config_flow = CONFIG_FLOW
    options_flow = OPTIONS_FLOW
    VERSION = const.CONFIG_VERSION

    @callback
    def async_config_entry_title(self, options: Mapping[str, Any]) -> str:
        """Return config entry title.

        The options parameter contains config entry options, which is the union of user
        input from the config flow steps.
        """
        return cast(str, options["name"]) if "name" in options else ""
