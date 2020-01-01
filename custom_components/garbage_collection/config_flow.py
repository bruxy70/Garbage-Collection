"""Adds config flow for GarbageCollection."""
from collections import OrderedDict
import logging
from homeassistant.core import callback
import voluptuous as vol
import homeassistant.helpers.config_validation as cv
from homeassistant import config_entries
from datetime import datetime
import uuid

from .const import (
    DOMAIN,
    FREQUENCY_OPTIONS,
    MONTH_OPTIONS,
    WEEKLY_FREQUENCY,
    WEEKLY_FREQUENCY_X,
    DAILY_FREQUENCY,
    MONTHLY_FREQUENCY,
    ANNUAL_FREQUENCY,
    GROUP_FREQUENCY,
    COUNTRY_CODES,
    DEFAULT_FIRST_MONTH,
    DEFAULT_LAST_MONTH,
    DEFAULT_FREQUENCY,
    DEFAULT_ICON_NORMAL,
    DEFAULT_ICON_TOMORROW,
    DEFAULT_ICON_TODAY,
    DEFAULT_VERBOSE_STATE,
    DEFAULT_VERBOSE_FORMAT,
    DEFAULT_DATE_FORMAT,
    CONF_SENSOR,
    CONF_ENABLED,
    CONF_FREQUENCY,
    CONF_ICON_NORMAL,
    CONF_ICON_TODAY,
    CONF_ICON_TOMORROW,
    CONF_VERBOSE_STATE,
    CONF_VERBOSE_FORMAT,
    CONF_DATE_FORMAT,
    CONF_FIRST_MONTH,
    CONF_LAST_MONTH,
    CONF_COLLECTION_DAYS,
    CONF_FORCE_WEEK_NUMBERS,
    CONF_WEEKDAY_ORDER_NUMBER,
    CONF_WEEK_ORDER_NUMBER,
    CONF_DATE,
    CONF_EXCLUDE_DATES,
    CONF_INCLUDE_DATES,
    CONF_MOVE_COUNTRY_HOLIDAYS,
    CONF_PERIOD,
    CONF_FIRST_WEEK,
    CONF_FIRST_DATE,
    CONF_SENSORS,
    ATTR_NEXT_DATE,
)

from homeassistant.const import CONF_NAME, WEEKDAYS, CONF_ENTITIES

_LOGGER = logging.getLogger(__name__)


def clean_optional(dict, key):
    """Remove optional keys before update"""
    if key in dict:
        del dict[key]


@config_entries.HANDLERS.register(DOMAIN)
class GarbageCollectionFlowHandler(config_entries.ConfigFlow):
    """Config flow for garbage_collection."""

    VERSION = 1
    CONNECTION_CLASS = config_entries.CONN_CLASS_LOCAL_POLL

    def __init__(self):
        """Initialize."""
        self._errors = {}
        self._data = {}
        self._data["unique_id"] = str(uuid.uuid4())

    async def async_step_user(
        self, user_input={}
    ):  # pylint: disable=dangerous-default-value
        """

        C O N F I G U R A T I O N   S T E P   1

        """
        self._errors = {}
        if user_input is not None:
            if user_input[CONF_NAME] != "":
                # Remember Frequency
                self._data.update(user_input)
                # Call next step
                if (
                    user_input[CONF_FREQUENCY] in ANNUAL_FREQUENCY
                    or user_input[CONF_FREQUENCY] in GROUP_FREQUENCY
                ):
                    # Annual and group schedule is different (does not have days)
                    return await self.async_step_annual_group()
                elif user_input[CONF_FREQUENCY] in DAILY_FREQUENCY:
                    return await self.async_step_final()
                else:
                    return await self.async_step_detail()
            else:
                self._errors["base"] = "name"
            return await self._show_user_form(user_input)
        return await self._show_user_form(user_input)

    async def _show_user_form(self, user_input):
        """Configuration STEP 1 - SHOW FORM"""
        # Defaults
        name = ""
        frequency = DEFAULT_FREQUENCY
        icon_normal = DEFAULT_ICON_NORMAL
        icon_tomorrow = DEFAULT_ICON_TOMORROW
        icon_today = DEFAULT_ICON_TODAY
        verbose_state = DEFAULT_VERBOSE_STATE
        verbose_format = DEFAULT_VERBOSE_FORMAT
        date_format = DEFAULT_DATE_FORMAT
        if user_input is not None:
            if CONF_NAME in user_input:
                name = user_input[CONF_NAME]
            if CONF_FREQUENCY in user_input:
                frequency = user_input[CONF_FREQUENCY]
            if CONF_ICON_NORMAL in user_input:
                icon_normal = user_input[CONF_ICON_NORMAL]
            if CONF_ICON_TOMORROW in user_input:
                icon_tomorrow = user_input[CONF_ICON_TOMORROW]
            if CONF_ICON_TODAY in user_input:
                icon_today = user_input[CONF_ICON_TODAY]
            if CONF_VERBOSE_STATE in user_input:
                verbose_state = user_input[CONF_VERBOSE_STATE]
            if CONF_VERBOSE_FORMAT in user_input:
                verbose_format = user_input[CONF_VERBOSE_FORMAT]
            if CONF_DATE_FORMAT in user_input:
                date_format = user_input[CONF_DATE_FORMAT]
        data_schema = OrderedDict()
        data_schema[vol.Required(CONF_NAME, default=name)] = str
        data_schema[vol.Required(CONF_FREQUENCY, default=frequency)] = vol.In(
            FREQUENCY_OPTIONS
        )
        data_schema[vol.Required(CONF_ICON_NORMAL, default=icon_normal)] = str
        data_schema[vol.Required(CONF_ICON_TOMORROW, default=icon_tomorrow)] = str
        data_schema[vol.Required(CONF_ICON_TODAY, default=icon_today)] = str
        data_schema[vol.Required(CONF_VERBOSE_STATE, default=verbose_state)] = bool
        data_schema[vol.Required(CONF_VERBOSE_FORMAT, default=verbose_format)] = str
        data_schema[vol.Required(CONF_DATE_FORMAT, default=date_format)] = str
        return self.async_show_form(
            step_id="user", data_schema=vol.Schema(data_schema), errors=self._errors
        )

    async def async_step_annual_group(
        self, user_input={}
    ):  # pylint: disable=dangerous-default-value
        """

        C O N F I G U R A T I O N   S T E P   A N N U A L   O R   G R O U P

        """
        self._errors = {}
        updates = {}
        if user_input is not None and user_input != {}:
            if self._data[CONF_FREQUENCY] in ANNUAL_FREQUENCY:
                updates[CONF_DATE] = user_input[CONF_DATE]
                if not is_month_day(user_input[CONF_DATE]):
                    self._errors["base"] = "month_day"
            else:
                updates[CONF_ENTITIES] = string_to_list(user_input[CONF_ENTITIES])
                checked = True
                for entity in updates[CONF_ENTITIES]:
                    try:
                        self.hass.states.get(entity).attributes.get(ATTR_NEXT_DATE)
                    except:
                        checked = False
                if not checked:
                    self._errors["base"] = "entities"
            if self._errors == {}:
                # Remember Frequency
                self._data.update(updates)
                # Call last step
                return self.async_create_entry(
                    title=self._data["name"], data=self._data
                )
        return await self._show_annual_group_form(user_input)

    async def _show_annual_group_form(self, user_input):
        """Configuration STEP 2 - Annual or Group (no days) - SHOW FORM"""
        # Defaults
        date = ""
        entities = ""
        if user_input is not None:
            if CONF_DATE in user_input:
                date = user_input[CONF_DATE]
            if CONF_ENTITIES in user_input:
                entities = user_input[CONF_ENTITIES]
        data_schema = OrderedDict()
        if self._data[CONF_FREQUENCY] in ANNUAL_FREQUENCY:
            data_schema[vol.Required(CONF_DATE, default=date)] = str
        else:
            data_schema[vol.Required(CONF_ENTITIES, default=entities)] = str
        return self.async_show_form(
            step_id="annual_group",
            data_schema=vol.Schema(data_schema),
            errors=self._errors,
        )

    async def async_step_detail(
        self, user_input={}
    ):  # pylint: disable=dangerous-default-value
        """

        C O N F I G U R A T I O N   S T E P   2

        """
        self._errors = {}
        if user_input is not None and user_input != {}:
            day_selected = False
            detail_info = {}
            if self._data[CONF_FREQUENCY] in MONTHLY_FREQUENCY:
                detail_info[CONF_FORCE_WEEK_NUMBERS] = user_input[
                    CONF_FORCE_WEEK_NUMBERS
                ]
            detail_info[CONF_COLLECTION_DAYS] = []
            for day in WEEKDAYS:
                if user_input[f"collection_days_{day.lower()}"]:
                    day_selected = True
                    detail_info[CONF_COLLECTION_DAYS].append(day)
            if day_selected:
                # Remember Detail
                self._data.update(detail_info)
                # Call last step
                return await self.async_step_final()
            else:
                self._errors["base"] = "days"
        return await self._show_detail_form(user_input)

    async def _show_detail_form(self, user_input):
        """Configuration STEP 2 - SHOW FORM"""
        data_schema = OrderedDict()
        for day in WEEKDAYS:
            data_schema[
                vol.Required(
                    f"collection_days_{day.lower()}",
                    default=bool(
                        user_input is not None
                        and user_input != {}
                        and user_input[f"collection_days_{day.lower()}"]
                    ),
                )
            ] = bool
        if self._data[CONF_FREQUENCY] in MONTHLY_FREQUENCY:
            data_schema[
                vol.Required(
                    CONF_FORCE_WEEK_NUMBERS,
                    default=bool(
                        user_input is not None
                        and user_input != {}
                        and user_input[CONF_FORCE_WEEK_NUMBERS]
                    ),
                )
            ] = bool
        return self.async_show_form(
            step_id="detail", data_schema=vol.Schema(data_schema), errors=self._errors
        )

    async def async_step_final(
        self, user_input={}
    ):  # pylint: disable=dangerous-default-value
        """

        C O N F I G U R A T I O N   S T E P   3

        """
        self._errors = {}
        if user_input is not None and user_input != {}:
            final_info = {}
            final_info[CONF_FIRST_MONTH] = user_input[CONF_FIRST_MONTH]
            final_info[CONF_LAST_MONTH] = user_input[CONF_LAST_MONTH]
            if self._data[CONF_FREQUENCY] in MONTHLY_FREQUENCY:
                day_selected = False
                final_info[CONF_WEEKDAY_ORDER_NUMBER] = []
                final_info[CONF_WEEK_ORDER_NUMBER] = []
                for i in range(5):
                    if self._data[CONF_FORCE_WEEK_NUMBERS]:
                        if user_input[f"week_order_number_{i+1}"]:
                            day_selected = True
                            final_info[CONF_WEEK_ORDER_NUMBER].append(i + 1)
                    else:
                        if user_input[f"weekday_order_number_{i+1}"]:
                            day_selected = True
                            final_info[CONF_WEEKDAY_ORDER_NUMBER].append(i + 1)
                if not day_selected:
                    self._errors["base"] = CONF_WEEKDAY_ORDER_NUMBER
            if self._data[CONF_FREQUENCY] in DAILY_FREQUENCY:
                if is_date(user_input[CONF_FIRST_DATE]):
                    final_info[CONF_FIRST_DATE] = user_input[CONF_FIRST_DATE]
                else:
                    self._errors["base"] = "date"
                final_info[CONF_PERIOD] = user_input[CONF_PERIOD]
            if self._data[CONF_FREQUENCY] in WEEKLY_FREQUENCY_X:
                final_info[CONF_PERIOD] = user_input[CONF_PERIOD]
                final_info[CONF_FIRST_WEEK] = user_input[CONF_FIRST_WEEK]
            final_info[CONF_INCLUDE_DATES] = string_to_list(
                user_input[CONF_INCLUDE_DATES]
            )
            final_info[CONF_EXCLUDE_DATES] = string_to_list(
                user_input[CONF_EXCLUDE_DATES]
            )
            final_info[CONF_MOVE_COUNTRY_HOLIDAYS] = user_input[
                CONF_MOVE_COUNTRY_HOLIDAYS
            ]
            if not is_dates(final_info[CONF_INCLUDE_DATES]) or not is_dates(
                final_info[CONF_EXCLUDE_DATES]
            ):
                self._errors["base"] = "date"
            if self._errors == {}:
                self._data.update(final_info)
                return self.async_create_entry(
                    title=self._data["name"], data=self._data
                )
        return await self._show_final_form(user_input)

    async def _show_final_form(self, user_input):
        """Configuration STEP 3 - SHOW FORM"""
        # Defaults
        first_month = DEFAULT_FIRST_MONTH
        last_month = DEFAULT_LAST_MONTH
        first_date = ""
        include_dates = ""
        exclude_dates = ""
        include_country_holidays = ""

        period = 1
        first_week = 1
        if user_input is not None:
            if CONF_FIRST_MONTH in user_input:
                first_month = user_input[CONF_FIRST_MONTH]
            if CONF_LAST_MONTH in user_input:
                last_month = user_input[CONF_LAST_MONTH]
            if CONF_FIRST_DATE in user_input:
                first_date = user_input[CONF_FIRST_DATE]
            if CONF_PERIOD in user_input:
                period = user_input[CONF_PERIOD]
            if CONF_FIRST_WEEK in user_input:
                first_week = user_input[CONF_FIRST_WEEK]
            if CONF_INCLUDE_DATES in user_input:
                include_dates = user_input[CONF_INCLUDE_DATES]
            if CONF_EXCLUDE_DATES in user_input:
                exclude_dates = user_input[CONF_EXCLUDE_DATES]
            if CONF_MOVE_COUNTRY_HOLIDAYS in user_input:
                include_country_holidays = user_input[CONF_MOVE_COUNTRY_HOLIDAYS]
        data_schema = OrderedDict()
        data_schema[vol.Optional(CONF_FIRST_MONTH, default=first_month)] = vol.In(
            MONTH_OPTIONS
        )
        data_schema[vol.Optional(CONF_LAST_MONTH, default=last_month)] = vol.In(
            MONTH_OPTIONS
        )
        if self._data[CONF_FREQUENCY] in DAILY_FREQUENCY:
            data_schema[vol.Required(CONF_PERIOD, default=period)] = vol.All(
                vol.Coerce(int), vol.Range(min=1, max=52)
            )
            data_schema[vol.Required(CONF_FIRST_DATE, default=first_date)] = str
        if self._data[CONF_FREQUENCY] in WEEKLY_FREQUENCY_X:
            data_schema[vol.Required(CONF_PERIOD, default=period)] = vol.All(
                vol.Coerce(int), vol.Range(min=1, max=52)
            )
            data_schema[vol.Required(CONF_FIRST_WEEK, default=first_week)] = vol.All(
                vol.Coerce(int), vol.Range(min=1, max=52)
            )
        if self._data[CONF_FREQUENCY] in MONTHLY_FREQUENCY:
            for i in range(5):
                if self._data[CONF_FORCE_WEEK_NUMBERS]:
                    data_schema[
                        vol.Required(
                            f"week_order_number_{i+1}",
                            default=bool(
                                user_input is not None
                                and user_input != {}
                                and user_input[f"week_order_number_{i+1}"]
                            ),
                        )
                    ] = bool
                else:
                    data_schema[
                        vol.Required(
                            f"weekday_order_number_{i+1}",
                            default=bool(
                                user_input is not None
                                and user_input != {}
                                and user_input[f"weekday_order_number_{i+1}"]
                            ),
                        )
                    ] = bool
        data_schema[vol.Optional(CONF_INCLUDE_DATES, default=include_dates)] = str
        data_schema[vol.Optional(CONF_EXCLUDE_DATES, default=exclude_dates)] = str
        data_schema[
            vol.Optional(CONF_MOVE_COUNTRY_HOLIDAYS, default=include_country_holidays)
        ] = vol.In(COUNTRY_CODES)
        return self.async_show_form(
            step_id="final", data_schema=vol.Schema(data_schema), errors=self._errors
        )

    async def async_step_import(self, user_input):  # pylint: disable=unused-argument
        """Import a config entry.
        Special type of import, we're not actually going to store any data.
        Instead, we're going to rely on the values that are in config file.
        """
        if self._async_current_entries():
            return self.async_abort(reason="single_instance_allowed")

        return self.async_create_entry(title="configuration.yaml", data={})

    @staticmethod
    @callback
    def async_get_options_flow(config_entry):
        if config_entry.options.get("unique_id", None) is not None:
            return OptionsFlowHandler(config_entry)
        else:
            return EmptyOptions(config_entry)


def is_month_day(date):
    """Validates mm/dd format"""
    try:
        date = datetime.strptime(date, "%m/%d")
        return True
    except ValueError:
        return False


def is_date(date):
    """Validates yyyy-mm-dd format"""
    if date == "":
        return True
    try:
        datetime.strptime(date, "%Y-%m-%d")
        return True
    except ValueError:
        return False


def string_to_list(string):
    if string is None or string == "":
        return []
    return list(map(lambda x: x.strip(), string.split(",")))


def is_dates(dates):
    """Validates list of dates (yyyy-mm-dd, yyyy-mm-dd)"""
    if dates == []:
        return True
    check = True
    for date in dates:
        if not is_date(date):
            check = False
    return check


"""

O P T I O N S   F L O W

"""


class OptionsFlowHandler(config_entries.OptionsFlow):
    def __init__(self, config_entry):
        self.config_entry = config_entry
        self._data = config_entry.options

    async def async_step_init(self, user_input=None):
        """

        O P T I O N S   S T E P   1

        """
        self._errors = {}
        if user_input is not None:
            # Remember Frequency
            self._data.update(user_input)
            # Call next step
            if (
                user_input[CONF_FREQUENCY] in ANNUAL_FREQUENCY
                or user_input[CONF_FREQUENCY] in GROUP_FREQUENCY
            ):
                return await self.async_step_annual_group()
            elif user_input[CONF_FREQUENCY] in DAILY_FREQUENCY:
                return await self.async_step_final()
            else:
                return await self.async_step_detail()
            return await self._show_init_form(user_input)
        return await self._show_init_form(user_input)

    async def _show_init_form(self, user_input):
        """Options STEP 1 - SHOW FORM"""
        # Defaults
        data_schema = OrderedDict()
        data_schema[
            vol.Required(
                CONF_FREQUENCY, default=self.config_entry.options.get(CONF_FREQUENCY)
            )
        ] = vol.In(FREQUENCY_OPTIONS)
        data_schema[
            vol.Required(
                CONF_ICON_NORMAL,
                default=self.config_entry.options.get(
                    CONF_ICON_NORMAL, DEFAULT_ICON_NORMAL
                ),
            )
        ] = str
        data_schema[
            vol.Required(
                CONF_ICON_TOMORROW,
                default=self.config_entry.options.get(
                    CONF_ICON_TOMORROW, DEFAULT_ICON_TOMORROW
                ),
            )
        ] = str
        data_schema[
            vol.Required(
                CONF_ICON_TODAY,
                default=self.config_entry.options.get(
                    CONF_ICON_TODAY, DEFAULT_ICON_TODAY
                ),
            )
        ] = str
        data_schema[
            vol.Required(
                CONF_VERBOSE_STATE,
                default=self.config_entry.options.get(CONF_VERBOSE_STATE, False),
            )
        ] = bool
        data_schema[
            vol.Required(
                CONF_VERBOSE_FORMAT,
                default=self.config_entry.options.get(
                    CONF_VERBOSE_FORMAT, DEFAULT_VERBOSE_FORMAT
                ),
            )
        ] = str
        data_schema[
            vol.Required(
                CONF_DATE_FORMAT,
                default=self.config_entry.options.get(
                    CONF_DATE_FORMAT, DEFAULT_DATE_FORMAT
                ),
            )
        ] = str
        return self.async_show_form(
            step_id="init", data_schema=vol.Schema(data_schema), errors=self._errors
        )

    async def async_step_annual_group(
        self, user_input={}
    ):  # pylint: disable=dangerous-default-value
        """

        O P T I O N S   S T E P   2   F O R   A N N U A L   O R   G R O U P

        """
        self._errors = {}
        updates = {}
        if user_input is not None and user_input != {}:
            if self._data[CONF_FREQUENCY] in ANNUAL_FREQUENCY:
                updates[CONF_DATE] = user_input[CONF_DATE]
                if not is_month_day(user_input[CONF_DATE]):
                    self._errors["base"] = "month_day"
            else:
                updates[CONF_ENTITIES] = string_to_list(user_input[CONF_ENTITIES])
                checked = True
                for entity in updates[CONF_ENTITIES]:
                    try:
                        self.hass.states.get(entity).attributes.get(ATTR_NEXT_DATE)
                    except:
                        checked = False
                if not checked:
                    self._errors["base"] = "entities"
            if self._errors == {}:
                # Remember Frequency
                clean_optional(self._data, CONF_DATE)
                self._data.update(updates)
                # Call last step
                return self.async_create_entry(title="", data=self._data)
        return await self._show_annual_group_form(user_input)

    async def _show_annual_group_form(self, user_input):
        """Configuration STEP 2 for Annual or Group - SHOW FORM"""
        # Defaults
        data_schema = OrderedDict()
        if self._data[CONF_FREQUENCY] in ANNUAL_FREQUENCY:
            data_schema[
                vol.Optional(
                    CONF_DATE, default=self.config_entry.options.get(CONF_DATE)
                )
            ] = str
        else:
            data_schema[
                vol.Required(
                    CONF_ENTITIES,
                    default=",".join(self.config_entry.options.get(CONF_ENTITIES)),
                )
            ] = str
        return self.async_show_form(
            step_id="annual_group",
            data_schema=vol.Schema(data_schema),
            errors=self._errors,
        )

    async def async_step_detail(
        self, user_input={}
    ):  # pylint: disable=dangerous-default-value
        """

        O P T I O N S   S T E P   2

        """
        self._errors = {}
        if user_input is not None and user_input != {}:
            day_selected = False
            detail_info = {}
            if self._data[CONF_FREQUENCY] in MONTHLY_FREQUENCY:
                detail_info[CONF_FORCE_WEEK_NUMBERS] = user_input[
                    CONF_FORCE_WEEK_NUMBERS
                ]
            detail_info[CONF_COLLECTION_DAYS] = []
            for day in WEEKDAYS:
                if user_input[f"collection_days_{day.lower()}"]:
                    day_selected = True
                    detail_info[CONF_COLLECTION_DAYS].append(day)
            if day_selected:
                # Remember Detail
                self._data.update(detail_info)
                # Call last step
                return await self.async_step_final()
            else:
                self._errors["base"] = "days"
        return await self._show_detail_form(user_input)

    async def _show_detail_form(self, user_input):
        """Configuration STEP 2 - SHOW FORM"""
        data_schema = OrderedDict()
        for day in WEEKDAYS:
            data_schema[
                vol.Required(
                    f"collection_days_{day.lower()}",
                    default=bool(
                        day.lower()
                        in self.config_entry.options.get(CONF_COLLECTION_DAYS)
                    ),
                )
            ] = bool
        if self._data[CONF_FREQUENCY] in MONTHLY_FREQUENCY:
            data_schema[
                vol.Required(
                    CONF_FORCE_WEEK_NUMBERS,
                    default=bool(
                        self.config_entry.options.get(CONF_FORCE_WEEK_NUMBERS, False)
                    ),
                )
            ] = bool
        return self.async_show_form(
            step_id="detail", data_schema=vol.Schema(data_schema), errors=self._errors
        )

    async def async_step_final(
        self, user_input={}
    ):  # pylint: disable=dangerous-default-value
        """

        C O N F I G U R A T I O N   S T E P   3

        """
        self._errors = {}
        if user_input is not None and user_input != {}:
            final_info = {}
            final_info[CONF_FIRST_MONTH] = user_input[CONF_FIRST_MONTH]
            final_info[CONF_LAST_MONTH] = user_input[CONF_LAST_MONTH]
            if self._data[CONF_FREQUENCY] in MONTHLY_FREQUENCY:
                day_selected = False
                final_info[CONF_WEEKDAY_ORDER_NUMBER] = []
                final_info[CONF_WEEK_ORDER_NUMBER] = []
                for i in range(5):
                    if self._data[CONF_FORCE_WEEK_NUMBERS]:
                        if user_input[f"week_order_number_{i+1}"]:
                            day_selected = True
                            final_info[CONF_WEEK_ORDER_NUMBER].append(i + 1)
                    else:
                        if user_input[f"weekday_order_number_{i+1}"]:
                            day_selected = True
                            final_info[CONF_WEEKDAY_ORDER_NUMBER].append(i + 1)
                if not day_selected:
                    self._errors["base"] = CONF_WEEKDAY_ORDER_NUMBER
            final_info[CONF_INCLUDE_DATES] = string_to_list(
                user_input[CONF_INCLUDE_DATES]
            )
            final_info[CONF_EXCLUDE_DATES] = string_to_list(
                user_input[CONF_EXCLUDE_DATES]
            )
            if not is_dates(final_info[CONF_INCLUDE_DATES]) or not is_dates(
                final_info[CONF_EXCLUDE_DATES]
            ):
                self._errors["base"] = "date"
            final_info[CONF_MOVE_COUNTRY_HOLIDAYS] = user_input[
                CONF_MOVE_COUNTRY_HOLIDAYS
            ]
            if self._data[CONF_FREQUENCY] in DAILY_FREQUENCY:
                if is_date(user_input[CONF_FIRST_DATE]):
                    final_info[CONF_FIRST_DATE] = user_input[CONF_FIRST_DATE]
                else:
                    self._errors["base"] = "date"
                final_info[CONF_PERIOD] = user_input[CONF_PERIOD]
            if self._data[CONF_FREQUENCY] in WEEKLY_FREQUENCY_X:
                final_info[CONF_PERIOD] = user_input[CONF_PERIOD]
                final_info[CONF_FIRST_WEEK] = user_input[CONF_FIRST_WEEK]
            if self._errors == {}:
                clean_optional(self._data, CONF_FIRST_MONTH)
                clean_optional(self._data, CONF_LAST_MONTH)
                clean_optional(self._data, CONF_INCLUDE_DATES)
                clean_optional(self._data, CONF_EXCLUDE_DATES)
                clean_optional(self._data, CONF_MOVE_COUNTRY_HOLIDAYS)
                # _LOGGER.debug("final_info %s",final_info)
                self._data.update(final_info)
                return self.async_create_entry(title="", data=self._data)
        return await self._show_final_form(user_input)

    async def _show_final_form(self, user_input):
        """Configuration STEP 3 - SHOW FORM"""
        data_schema = OrderedDict()
        data_schema[
            vol.Optional(
                CONF_FIRST_MONTH,
                default=self.config_entry.options.get(CONF_FIRST_MONTH),
            )
        ] = vol.In(MONTH_OPTIONS)
        data_schema[
            vol.Optional(
                CONF_LAST_MONTH, default=self.config_entry.options.get(CONF_LAST_MONTH)
            )
        ] = vol.In(MONTH_OPTIONS)
        if self._data[CONF_FREQUENCY] in WEEKLY_FREQUENCY_X:
            data_schema[
                vol.Required(
                    CONF_PERIOD, default=self.config_entry.options.get(CONF_PERIOD)
                )
            ] = vol.All(vol.Coerce(int), vol.Range(min=1, max=52))
            data_schema[
                vol.Required(
                    CONF_FIRST_WEEK,
                    default=self.config_entry.options.get(CONF_FIRST_WEEK),
                )
            ] = vol.All(vol.Coerce(int), vol.Range(min=1, max=52))
        if self._data[CONF_FREQUENCY] in MONTHLY_FREQUENCY:
            for i in range(5):
                if self._data[CONF_FORCE_WEEK_NUMBERS]:
                    data_schema[
                        vol.Required(
                            f"week_order_number_{i+1}",
                            default=bool(
                                (i + 1)
                                in self.config_entry.options.get(CONF_WEEK_ORDER_NUMBER)
                            ),
                        )
                    ] = bool
                else:
                    data_schema[
                        vol.Required(
                            f"weekday_order_number_{i+1}",
                            default=bool(
                                (i + 1)
                                in self.config_entry.options.get(
                                    CONF_WEEKDAY_ORDER_NUMBER
                                )
                            ),
                        )
                    ] = bool
        if self._data[CONF_FREQUENCY] in DAILY_FREQUENCY:
            data_schema[
                vol.Required(
                    CONF_PERIOD, default=self.config_entry.options.get(CONF_PERIOD)
                )
            ] = vol.All(vol.Coerce(int), vol.Range(min=1, max=52))
            data_schema[
                vol.Required(
                    CONF_FIRST_DATE,
                    default=self.config_entry.options.get(CONF_FIRST_DATE),
                )
            ] = str
        data_schema[
            vol.Optional(
                CONF_INCLUDE_DATES,
                default=",".join(self.config_entry.options.get(CONF_INCLUDE_DATES)),
            )
        ] = str
        data_schema[
            vol.Optional(
                CONF_EXCLUDE_DATES,
                default=",".join(self.config_entry.options.get(CONF_EXCLUDE_DATES)),
            )
        ] = str
        data_schema[
            vol.Optional(
                CONF_MOVE_COUNTRY_HOLIDAYS,
                default=self.config_entry.options.get(CONF_MOVE_COUNTRY_HOLIDAYS, ""),
            )
        ] = vol.In(COUNTRY_CODES)
        return self.async_show_form(
            step_id="final", data_schema=vol.Schema(data_schema), errors=self._errors
        )


class EmptyOptions(config_entries.OptionsFlow):
    def __init__(self, config_entry):
        self.config_entry = config_entry
