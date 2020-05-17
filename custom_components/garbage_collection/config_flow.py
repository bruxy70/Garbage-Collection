"""Adds config flow for GarbageCollection."""
from collections import OrderedDict
import logging
from homeassistant.core import callback
import voluptuous as vol
import homeassistant.helpers.config_validation as cv
from homeassistant import config_entries
from datetime import datetime
import uuid

from .const import *  # pylint: disable=W0614
from homeassistant.const import CONF_NAME, WEEKDAYS, CONF_ENTITIES

_LOGGER = logging.getLogger(__name__)


def clean_optional(dict, key):
    """Remove optional keys before update"""
    if key in dict:
        del dict[key]


class garbage_collection_options:
    def __init__(self, unique_id):
        self._data = {}
        self._data["unique_id"] = unique_id
        self.errors = {}
        self.data_schema = {}

    def step1_user_init(self, user_input, defaults=None):
        """

        C O N F I G U R A T I O N   S T E P   1

        """
        self.errors = {}
        if user_input is not None:
            validation = vol.Schema(CONFIGURATION.compile_schema(step=1))
            try:
                config = validation(user_input)  # pylint: disable=W0612
            except vol.Invalid as exception:
                e = str(exception)
                if (
                    CONF_ICON_NORMAL in e
                    or CONF_ICON_TODAY in e
                    or CONF_ICON_TOMORROW in e
                ):
                    self.errors["base"] = "icon"
                elif CONF_EXPIRE_AFTER in e:
                    self.errors["base"] = "time"
                else:
                    _LOGGER.error(f"Unknown exception: {exception}")
                    self.errors["base"] = "value"
                CONFIGURATION.set_defaults(1, user_input)
            if self.errors == {}:
                # Valid input - go to the next step!
                self._data.update(user_input)
                return True
        elif defaults is not None:
            CONFIGURATION.set_defaults(1, defaults)
        self.data_schema = CONFIGURATION.compile_config_flow(step=1)
        return False

    def step2_annual_group(self, user_input, defaults=None):
        """

        C O N F I G U R A T I O N   S T E P   2   (  A N N U A L   O R   G R O U P  )
        (no week days)

        """
        self.errors = {}
        self.data_schema = {}
        updates = {}
        if user_input is not None and user_input != {}:
            validation = vol.Schema(
                CONFIGURATION.compile_schema(
                    step=2, valid_for=self._data[CONF_FREQUENCY]
                )
            )
            try:
                updates = validation(user_input)
            except vol.Invalid as exception:  # pylint: disable=W0612
                # _LOGGER.debug(exception)
                if self._data[CONF_FREQUENCY] in ANNUAL_FREQUENCY:
                    self.errors["base"] = "month_day"
                else:
                    self.errors["base"] = "entities"
                CONFIGURATION.set_defaults(2, user_input)
            if self.errors == {}:
                # Remember step2 values
                if self._data[CONF_FREQUENCY] in GROUP_FREQUENCY:
                    updates[CONF_ENTITIES] = string_to_list(user_input[CONF_ENTITIES])
                self._data.update(updates)
                return True
        elif defaults is not None:
            CONFIGURATION.set_defaults(2, defaults)
        self.data_schema = CONFIGURATION.compile_config_flow(
            step=2, valid_for=self._data[CONF_FREQUENCY]
        )
        return False

    def step3_detail(self, user_input, defaults=None):
        """

        C O N F I G U R A T I O N   S T E P   2   ( O T H E R   T H A N   A N N U A L   O R   G R O U P )

        """
        self.errors = {}
        self.data_schema = {}
        if user_input is not None and user_input != {}:
            updates = user_input.copy()
            days_to_list(updates)
            validation_schema = CONFIGURATION.compile_schema(
                step=3, valid_for=self._data[CONF_FREQUENCY]
            )
            if self._data[CONF_FREQUENCY] in MONTHLY_FREQUENCY:
                validation_schema[
                    vol.Optional(
                        CONF_FORCE_WEEK_NUMBERS,
                        default=bool(
                            user_input is not None
                            and user_input != {}
                            and user_input[CONF_FORCE_WEEK_NUMBERS]
                        ),
                    )
                ] = cv.boolean
            validation = vol.Schema(validation_schema)
            try:
                updates = validation(updates)
            except vol.Invalid as exception:  # pylint: disable=W0612
                _LOGGER.error(f"Unknown exception: {exception}")
                self.errors["base"] = "value"

            if len(updates[CONF_COLLECTION_DAYS]) == 0:
                self.errors["base"] = "days"
            if self.errors == {}:
                # Remember values
                self._data.update(updates)
                return True
        elif defaults is not None:
            CONFIGURATION.set_defaults(3, defaults)
        self.data_schema = CONFIGURATION.compile_config_flow(
            step=3, valid_for=self._data[CONF_FREQUENCY]
        )
        list_to_days(self.data_schema)
        if self._data[CONF_FREQUENCY] in MONTHLY_FREQUENCY:
            self.data_schema[
                vol.Optional(
                    CONF_FORCE_WEEK_NUMBERS,
                    default=bool(
                        user_input is not None
                        and user_input != {}
                        and user_input[CONF_FORCE_WEEK_NUMBERS]
                    ),
                )
            ] = bool
        return False

    def step4_final(self, user_input, defaults=None):
        """

        C O N F I G U R A T I O N   S T E P   3

        """
        self.errors = {}
        self.data_schema = {}
        if user_input is not None and user_input != {}:
            updates = user_input.copy()
            if self._data[CONF_FREQUENCY] in MONTHLY_FREQUENCY:
                if self._data[CONF_FORCE_WEEK_NUMBERS]:
                    weekdays_to_list(updates, CONF_WEEK_ORDER_NUMBER)
                else:
                    weekdays_to_list(updates, CONF_WEEKDAY_ORDER_NUMBER)
            validation = vol.Schema(
                CONFIGURATION.compile_schema(
                    step=4, valid_for=self._data[CONF_FREQUENCY]
                )
            )
            if CONF_INCLUDE_DATES in updates:
                updates[CONF_INCLUDE_DATES] = string_to_list(
                    updates[CONF_INCLUDE_DATES]
                )
            if CONF_EXCLUDE_DATES in updates:
                updates[CONF_EXCLUDE_DATES] = string_to_list(
                    updates[CONF_EXCLUDE_DATES]
                )
            try:
                updates = validation(updates)
            except vol.Invalid as exception:  # pylint: disable=W0612
                e = str(exception)
                if (
                    CONF_INCLUDE_DATES in e
                    or CONF_EXCLUDE_DATES in e
                    or CONF_FIRST_DATE in e
                ):
                    self.errors["base"] = "date"
                else:
                    self.errors["base"] = "value"
                    _LOGGER.error(f"Unknown exception: {exception}")
            if self._data[CONF_FREQUENCY] in MONTHLY_FREQUENCY:
                if self._data[CONF_FORCE_WEEK_NUMBERS]:
                    if len(updates[CONF_WEEK_ORDER_NUMBER]) == 0:
                        self.errors["base"] = CONF_WEEK_ORDER_NUMBER
                else:
                    if len(updates[CONF_WEEKDAY_ORDER_NUMBER]) == 0:
                        self.errors["base"] = CONF_WEEKDAY_ORDER_NUMBER
            if self.errors == {}:
                self._data.update(updates)
                if CONF_FORCE_WEEK_NUMBERS in self._data:
                    if self._data[CONF_FORCE_WEEK_NUMBERS]:
                        if CONF_WEEKDAY_ORDER_NUMBER in self._data:
                            del self._data[CONF_WEEKDAY_ORDER_NUMBER]
                    else:
                        if CONF_WEEK_ORDER_NUMBER in self._data:
                            del self._data[CONF_WEEK_ORDER_NUMBER]
                    del self._data[CONF_FORCE_WEEK_NUMBERS]
                return True
        elif defaults is not None:
            CONFIGURATION.set_defaults(4, defaults)
        self.data_schema = CONFIGURATION.compile_config_flow(
            step=4, valid_for=self._data[CONF_FREQUENCY]
        )
        if self._data[CONF_FREQUENCY] in MONTHLY_FREQUENCY:
            if self._data[CONF_FORCE_WEEK_NUMBERS]:
                list_to_weekdays(self.data_schema, CONF_WEEK_ORDER_NUMBER)
            else:
                list_to_weekdays(self.data_schema, CONF_WEEKDAY_ORDER_NUMBER)
        return False

    @property
    def name(self):
        if CONF_NAME in self._data:
            return self._data[CONF_NAME]
        else:
            return None
        pass

    @property
    def frequency(self):
        if CONF_FREQUENCY in self._data:
            return self._data[CONF_FREQUENCY]
        else:
            return None

    @property
    def data(self):
        return self._data


@config_entries.HANDLERS.register(DOMAIN)
class GarbageCollectionFlowHandler(config_entries.ConfigFlow):
    """Config flow for garbage_collection."""

    VERSION = 1
    CONNECTION_CLASS = config_entries.CONN_CLASS_LOCAL_POLL

    def __init__(self):
        """Initialize."""
        CONFIGURATION.reset_defaults()
        self.options = garbage_collection_options(str(uuid.uuid4()))

    async def async_step_user(
        self, user_input={}
    ):  # pylint: disable=dangerous-default-value
        """
        C O N F I G U R A T I O N   S T E P   1
        """
        next_step = self.options.step1_user_init(user_input)
        if next_step:
            if self.options.frequency in ANNUAL_GROUP_FREQUENCY:
                return await self.async_step_annual_group()
            elif self.options.frequency in DAILY_FREQUENCY:
                return await self.async_step_final()
            else:
                return await self.async_step_detail()
        else:
            return self.async_show_form(
                step_id="user",
                data_schema=vol.Schema(self.options.data_schema),
                errors=self.options.errors,
            )

    async def async_step_annual_group(
        self, user_input={}
    ):  # pylint: disable=dangerous-default-value
        """
        C O N F I G U R A T I O N   S T E P   2   (  A N N U A L   O R   G R O U P  )
        (no week days)
        """
        next_step = self.options.step2_annual_group(user_input)
        if next_step:
            return self.async_create_entry(
                title=self.options.name, data=self.options.data
            )
        else:
            return self.async_show_form(
                step_id="annual_group",
                data_schema=vol.Schema(self.options.data_schema),
                errors=self.options.errors,
            )

    async def async_step_detail(
        self, user_input={}
    ):  # pylint: disable=dangerous-default-value
        """
        C O N F I G U R A T I O N   S T E P   2   ( O T H E R   T H A N   A N N U A L   O R   G R O U P )
        """
        next_step = self.options.step3_detail(user_input)
        if next_step:
            return await self.async_step_final()
        else:
            return self.async_show_form(
                step_id="detail",
                data_schema=vol.Schema(self.options.data_schema),
                errors=self.options.errors,
            )

    async def async_step_final(
        self, user_input={}
    ):  # pylint: disable=dangerous-default-value
        """
        C O N F I G U R A T I O N   S T E P   3
        """
        if self.options.step4_final(user_input):
            return self.async_create_entry(
                title=self.options.name, data=self.options.data
            )
        else:
            return self.async_show_form(
                step_id="final",
                data_schema=vol.Schema(self.options.data_schema),
                errors=self.options.errors,
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


"""


O P T I O N S   F L O W


"""


class OptionsFlowHandler(config_entries.OptionsFlow):
    def __init__(self, config_entry):
        self.config_entry = config_entry
        self.options = garbage_collection_options(config_entry.options.get("unique_id"))

    async def async_step_init(self, user_input=None):
        """
        O P T I O N S   S T E P   1
        """
        CONFIGURATION.clean(self.config_entry.options)
        next_step = self.options.step1_user_init(user_input, self.config_entry.options)
        if next_step:
            if self.options.frequency in ANNUAL_GROUP_FREQUENCY:
                return await self.async_step_annual_group()
            elif self.options.frequency in DAILY_FREQUENCY:
                return await self.async_step_final()
            else:
                return await self.async_step_detail()
        else:
            return self.async_show_form(
                step_id="init",
                data_schema=vol.Schema(self.options.data_schema),
                errors=self.options.errors,
            )

    async def async_step_annual_group(
        self, user_input={}
    ):  # pylint: disable=dangerous-default-value
        """
        O P T I O N S   S T E P   2   (  A N N U A L   O R   G R O U P  )
        (no week days)
        """
        next_step = self.options.step2_annual_group(
            user_input, self.config_entry.options
        )
        if next_step:
            return self.async_create_entry(
                title=self.options.name, data=self.options.data
            )
        else:
            return self.async_show_form(
                step_id="annual_group",
                data_schema=vol.Schema(self.options.data_schema),
                errors=self.options.errors,
            )

    async def async_step_detail(
        self, user_input={}
    ):  # pylint: disable=dangerous-default-value
        """
        C O N F I G U R A T I O N   S T E P   2   ( O T H E R   T H A N   A N N U A L   O R   G R O U P )
        """
        next_step = self.options.step3_detail(user_input, self.config_entry.options)
        if next_step:
            return await self.async_step_final()
        else:
            return self.async_show_form(
                step_id="detail",
                data_schema=vol.Schema(self.options.data_schema),
                errors=self.options.errors,
            )

    async def async_step_final(
        self, user_input={}
    ):  # pylint: disable=dangerous-default-value
        """
        C O N F I G U R A T I O N   S T E P   3
        """
        if self.options.step4_final(user_input, self.config_entry.options):
            return self.async_create_entry(
                title=self.options.name, data=self.options.data
            )
        else:
            return self.async_show_form(
                step_id="final",
                data_schema=vol.Schema(self.options.data_schema),
                errors=self.options.errors,
            )


class EmptyOptions(config_entries.OptionsFlow):
    def __init__(self, config_entry):
        self.config_entry = config_entry


def is_month_day(date) -> bool:
    """Validates mm/dd format"""
    try:
        date = datetime.strptime(date, "%m/%d")
        return True
    except ValueError:
        return False


def is_date(date) -> bool:
    """Validates yyyy-mm-dd format"""
    if date == "":
        return True
    try:
        datetime.strptime(date, "%Y-%m-%d")
        return True
    except ValueError:
        return False


def string_to_list(string) -> list:
    if string is None or string == "":
        return []
    return list(map(lambda x: x.strip(), string.split(",")))


def days_to_list(src):
    src[CONF_COLLECTION_DAYS] = []
    for day in WEEKDAYS:
        if src[f"collection_days_{day.lower()}"]:
            src[CONF_COLLECTION_DAYS].append(day)
        del src[f"collection_days_{day.lower()}"]


def weekdays_to_list(src, prefix):
    src[prefix] = []
    for i in range(5):
        if src[f"{prefix}_{i+1}"]:
            src[prefix].append(i + 1)
        del src[f"{prefix}_{i+1}"]


def list_to_days(data_schema):
    copy = data_schema.copy()
    data_schema.clear()
    for day in WEEKDAYS:
        data_schema[
            vol.Required(
                f"collection_days_{day.lower()}",
                default=bool(
                    CONF_COLLECTION_DAYS in CONFIGURATION.defaults
                    and day in CONFIGURATION.defaults[CONF_COLLECTION_DAYS]
                ),
            )
        ] = bool
    items = {
        key: value for (key, value) in copy.items() if key not in [CONF_COLLECTION_DAYS]
    }
    for key, value in items.items():
        data_schema[key] = value


def list_to_weekdays(data_schema, prefix):
    copy = data_schema.copy()
    data_schema.clear()
    for i in range(5):
        data_schema[
            vol.Required(
                f"{prefix}_{i+1}",
                default=bool(
                    prefix in CONFIGURATION.defaults
                    and (i + 1) in CONFIGURATION.defaults[prefix]
                ),
            )
        ] = bool
    items = {
        key: value
        for (key, value) in copy.items()
        if key not in [CONF_WEEKDAY_ORDER_NUMBER, CONF_WEEK_ORDER_NUMBER]
    }
    for key, value in items.items():
        data_schema[key] = value


def is_dates(dates) -> bool:
    """Validates list of dates (yyyy-mm-dd, yyyy-mm-dd)"""
    if dates == []:
        return True
    check = True
    for date in dates:
        if not is_date(date):
            check = False
    return check
