import voluptuous as vol
from datetime import datetime, date
import homeassistant.helpers.config_validation as cv
from homeassistant.const import CONF_NAME, WEEKDAYS, CONF_ENTITIES

"""Constants for garbage_collection."""
# Base component constants
DOMAIN = "garbage_collection"
DOMAIN_DATA = f"{DOMAIN}_data"
VERSION = "0.0.1"
PLATFORM = "sensor"
ISSUE_URL = "https://github.com/bruxy70/Garbage-Collection/issues"
ATTRIBUTION = "Data from this is provided by garbage_collection."

ATTR_NEXT_DATE = "next_date"
ATTR_DAYS = "days"

# Device classes
BINARY_SENSOR_DEVICE_CLASS = "connectivity"

# Configuration
CONF_SENSOR = "sensor"
CONF_ENABLED = "enabled"
CONF_FREQUENCY = "frequency"
CONF_ICON_NORMAL = "icon_normal"
CONF_ICON_TODAY = "icon_today"
CONF_ICON_TOMORROW = "icon_tomorrow"
CONF_VERBOSE_STATE = "verbose_state"
CONF_FIRST_MONTH = "first_month"
CONF_LAST_MONTH = "last_month"
CONF_COLLECTION_DAYS = "collection_days"
CONF_FORCE_WEEK_NUMBERS = "force_week_order_numbers"
CONF_WEEKDAY_ORDER_NUMBER = "weekday_order_number"
CONF_WEEK_ORDER_NUMBER = "week_order_number"
CONF_DATE = "date"
CONF_EXCLUDE_DATES = "exclude_dates"
CONF_INCLUDE_DATES = "include_dates"
CONF_MOVE_COUNTRY_HOLIDAYS = "move_country_holidays"
CONF_PROV = "prov"
CONF_STATE = "state"
CONF_OBSERVED = "observed"
CONF_PERIOD = "period"
CONF_FIRST_WEEK = "first_week"
CONF_FIRST_DATE = "first_date"
CONF_SENSORS = "sensors"
CONF_VERBOSE_FORMAT = "verbose_format"
CONF_DATE_FORMAT = "date_format"

# Defaults
DEFAULT_NAME = DOMAIN
DEFAULT_FIRST_MONTH = "jan"
DEFAULT_LAST_MONTH = "dec"
DEFAULT_FREQUENCY = "weekly"
DEFAULT_PERIOD = 1
DEFAULT_FIRST_WEEK = 1
DEFAULT_VERBOSE_STATE = False
DEFAULT_DATE_FORMAT = "%d-%b-%Y"
DEFAULT_VERBOSE_FORMAT = "on {date}, in {days} days"

# Icons
DEFAULT_ICON_NORMAL = "mdi:trash-can"
DEFAULT_ICON_TODAY = "mdi:delete-restore"
DEFAULT_ICON_TOMORROW = "mdi:delete-circle"
ICON = DEFAULT_ICON_NORMAL

# States
STATE_TODAY = "today"
STATE_TOMORROW = "tomorrow"

FREQUENCY_OPTIONS = [
    "weekly",
    "even-weeks",
    "odd-weeks",
    "every-n-weeks",
    "every-n-days",
    "monthly",
    "annual",
    "group",
]

MONTH_OPTIONS = [
    "jan",
    "feb",
    "mar",
    "apr",
    "may",
    "jun",
    "jul",
    "aug",
    "sep",
    "oct",
    "nov",
    "dec",
]

COUNTRY_CODES = [
    "",
    "AR",
    "AT",
    "AU",
    "AW",
    "BE",
    "BG",
    "BR",
    "BY",
    "CA",
    "CH",
    "CO",
    "CZ",
    "DE",
    "DK",
    "DO",
    "ECB",
    "EE",
    "ES",
    "FI",
    "FRA",
    "HR",
    "HU",
    "IE",
    "IND",
    "IS",
    "IT",
    "JP",
    "KE",
    "LT",
    "LU",
    "MX",
    "NG",
    "NI",
    "NL",
    "NO",
    "NZ",
    "PE",
    "PL",
    "PT",
    "PTE",
    "RU",
    "SE",
    "SI",
    "SK",
    "UA",
    "UK",
    "US",
    "ZA",
]


def date_text(value):
    if value is None or value == "":
        return ""
    try:
        return datetime.strptime(value, "%Y-%m-%d").date().strftime("%Y-%m-%d")
    except ValueError:
        raise vol.Invalid(f"Invalid date: {value}")


def month_day_text(value):
    if value is None or value == "":
        return ""
    try:
        return datetime.strptime(value, "%m/%d").date().strftime("%m/%d")
    except ValueError:
        raise vol.Invalid(f"Invalid date: {value}")


SENSOR_SCHEMA = vol.Schema(
    {
        vol.Required(CONF_NAME): cv.string,
        vol.Required(CONF_FREQUENCY): vol.In(FREQUENCY_OPTIONS),
        vol.Optional(CONF_COLLECTION_DAYS): vol.All(cv.ensure_list, [vol.In(WEEKDAYS)]),
        vol.Optional(CONF_FIRST_MONTH, default=DEFAULT_FIRST_MONTH): vol.In(
            MONTH_OPTIONS
        ),
        vol.Optional(CONF_LAST_MONTH, default=DEFAULT_LAST_MONTH): vol.In(
            MONTH_OPTIONS
        ),
        vol.Optional(CONF_WEEKDAY_ORDER_NUMBER, default=[1]): vol.All(
            cv.ensure_list, [vol.All(vol.Coerce(int), vol.Range(min=1, max=5))]
        ),
        vol.Optional(CONF_WEEK_ORDER_NUMBER, default=[]): vol.All(
            cv.ensure_list, [vol.All(vol.Coerce(int), vol.Range(min=1, max=5))]
        ),
        vol.Optional(CONF_PERIOD, default=DEFAULT_PERIOD): vol.All(
            vol.Coerce(int), vol.Range(min=1, max=52)
        ),
        vol.Optional(CONF_FIRST_WEEK, default=DEFAULT_FIRST_WEEK): vol.All(
            vol.Coerce(int), vol.Range(min=1, max=52)
        ),
        vol.Optional(CONF_FIRST_DATE): date_text,
        vol.Optional(CONF_DATE): month_day_text,
        vol.Optional(CONF_ENTITIES): cv.entity_ids,
        vol.Optional(CONF_INCLUDE_DATES, default=[]): vol.All(
            cv.ensure_list, [date_text]
        ),
        vol.Optional(CONF_EXCLUDE_DATES, default=[]): vol.All(
            cv.ensure_list, [date_text]
        ),
        vol.Optional(CONF_MOVE_COUNTRY_HOLIDAYS): vol.In(COUNTRY_CODES),
        vol.Optional(CONF_PROV): cv.string,
        vol.Optional(CONF_STATE): cv.string,
        vol.Optional(CONF_OBSERVED, default=True): bool,
        vol.Optional(CONF_ICON_NORMAL, default=DEFAULT_ICON_NORMAL): cv.icon,
        vol.Optional(CONF_ICON_TODAY, default=DEFAULT_ICON_TODAY): cv.icon,
        vol.Optional(CONF_ICON_TOMORROW, default=DEFAULT_ICON_TOMORROW): cv.icon,
        vol.Optional(CONF_VERBOSE_STATE, default=DEFAULT_VERBOSE_STATE): cv.boolean,
        vol.Optional(CONF_DATE_FORMAT, default=DEFAULT_DATE_FORMAT): cv.string,
        vol.Optional(CONF_VERBOSE_FORMAT, default=DEFAULT_VERBOSE_FORMAT): cv.string,
    }
)

CONFIG_SCHEMA = vol.Schema(
    {
        DOMAIN: vol.Schema(
            {vol.Optional(CONF_SENSORS): vol.All(cv.ensure_list, [SENSOR_SCHEMA])}
        )
    },
    extra=vol.ALLOW_EXTRA,
)


WEEKLY_FREQUENCY = ["weekly", "even-weeks", "odd-weeks"]
WEEKLY_FREQUENCY_X = ["every-n-weeks"]
DAILY_FREQUENCY = ["every-n-days"]
MONTHLY_FREQUENCY = ["monthly"]
ANNUAL_FREQUENCY = ["annual"]
GROUP_FREQUENCY = ["group"]
