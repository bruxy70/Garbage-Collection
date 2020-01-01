"""Sensor platform for garbage_collection."""
from homeassistant.helpers.entity import Entity
import homeassistant.util.dt as dt_util
import holidays
import logging
import locale
from datetime import datetime, date, timedelta
from homeassistant.core import HomeAssistant, State
from typing import List, Any

_LOGGER = logging.getLogger(__name__)

SCAN_INTERVAL = timedelta(seconds=60)
THROTTLE_INTERVAL = timedelta(seconds=60)
ATTR_NEXT_DATE = "next_date"
ATTR_DAYS = "days"

from homeassistant.const import CONF_NAME, WEEKDAYS, CONF_ENTITIES
from .const import (
    ATTRIBUTION,
    DEFAULT_NAME,
    DOMAIN,
    CONF_SENSOR,
    CONF_ENABLED,
    CONF_FREQUENCY,
    CONF_ICON_NORMAL,
    CONF_ICON_TODAY,
    CONF_ICON_TOMORROW,
    CONF_VERBOSE_STATE,
    CONF_VERBOSE_FORMAT,
    CONF_DATE_FORMAT,
    DEFAULT_DATE_FORMAT,
    DEFAULT_VERBOSE_FORMAT,
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
    MONTH_OPTIONS,
    FREQUENCY_OPTIONS,
    STATE_TODAY,
    STATE_TOMORROW,
)

_LOGGER = logging.getLogger(__name__)


async def async_setup_platform(
    hass, config, async_add_entities, discovery_info=None
):  # pylint: disable=unused-argument
    """Setup sensor platform."""
    async_add_entities([GarbageCollection(hass, discovery_info)], True)


async def async_setup_entry(hass, config_entry, async_add_devices):
    """Setup sensor platform."""
    async_add_devices([GarbageCollection(hass, config_entry.data)], True)


def nth_week_date(n: int, date_of_month: date, collection_day: int) -> date:
    """Find weekday in the nth week of the month"""
    first_of_month = date(date_of_month.year, date_of_month.month, 1)
    month_starts_on = first_of_month.weekday()
    return first_of_month + timedelta(
        days=collection_day - month_starts_on + (n - 1) * 7
    )


def nth_weekday_date(n: int, date_of_month: date, collection_day: int) -> date:
    """Find nth weekday of the month"""
    first_of_month = date(date_of_month.year, date_of_month.month, 1)
    month_starts_on = first_of_month.weekday()
    # 1st of the month is before the day of collection
    # (so 1st collection week the week when month starts)
    if collection_day >= month_starts_on:
        return first_of_month + timedelta(
            days=collection_day - month_starts_on + (n - 1) * 7
        )
    else:  # Next week
        return first_of_month + timedelta(
            days=7 - month_starts_on + collection_day + (n - 1) * 7
        )


def to_date(day: Any) -> date:
    if day is None:
        return None
    if type(day) == date:
        return day
    if type(day) == datetime:
        return day.date()
    return date.fromisoformat(day)


def to_dates(dates: List[Any]) -> List[date]:
    # Convert list of text to datetimes, if not already datetimes
    converted = []
    for day in dates:
        try:
            converted.append(to_date(day))
        except ValueError:
            continue
    return converted


class GarbageCollection(Entity):
    """GarbageCollection Sensor class."""

    def __init__(self, hass, config):
        self.config = config
        self.__name = config.get(CONF_NAME)
        self.__frequency = config.get(CONF_FREQUENCY)
        self.__collection_days = config.get(CONF_COLLECTION_DAYS)
        first_month = config.get(CONF_FIRST_MONTH)
        if first_month in MONTH_OPTIONS:
            self.__first_month = MONTH_OPTIONS.index(first_month) + 1
        else:
            self.__first_month = 1
        last_month = config.get(CONF_LAST_MONTH)
        if last_month in MONTH_OPTIONS:
            self.__last_month = MONTH_OPTIONS.index(last_month) + 1
        else:
            self.__last_month = 12
        self._weekday_order_numbers = config.get(CONF_WEEKDAY_ORDER_NUMBER)
        self._week_order_numbers = config.get(CONF_WEEK_ORDER_NUMBER)
        self.__monthly_force_week_numbers = bool(
            self._week_order_numbers is not None and len(self._week_order_numbers) != 0
        )
        self.__include_dates = to_dates(config.get(CONF_INCLUDE_DATES, []))
        self.__exclude_dates = to_dates(config.get(CONF_EXCLUDE_DATES, []))
        country_holidays = config.get(CONF_MOVE_COUNTRY_HOLIDAYS)
        self.__holidays = []
        if country_holidays is not None and country_holidays != "":
            today = dt_util.now().date()
            this_year = today.year
            years = [this_year, this_year + 1]
            try:
                for date, name in holidays.CountryHoliday(
                    country_holidays, years=years
                ).items():
                    if date >= today:
                        self.__holidays.append(date)
            except KeyError:
                _LOGGER.error("Invalid country code (%s)", country_holidays)
            _LOGGER.debug("(%s) Found these holidays %s", self.__name, self.__holidays)
        self.__period = config.get(CONF_PERIOD)
        self.__first_week = config.get(CONF_FIRST_WEEK)
        self.__first_date = to_date(config.get(CONF_FIRST_DATE))
        self.__next_date = None
        self.__today = None
        self.__days = 0
        self.__date = config.get(CONF_DATE)
        self.__entities = config.get(CONF_ENTITIES)
        self.__verbose_state = config.get(CONF_VERBOSE_STATE)
        self.__state = "" if bool(self.__verbose_state) else 2
        self.__icon_normal = config.get(CONF_ICON_NORMAL)
        self.__icon_today = config.get(CONF_ICON_TODAY)
        self.__icon_tomorrow = config.get(CONF_ICON_TOMORROW)
        self.__date_format = config.get(CONF_DATE_FORMAT, DEFAULT_DATE_FORMAT)
        self.__verbose_format = config.get(CONF_VERBOSE_FORMAT, DEFAULT_VERBOSE_FORMAT)
        self.__icon = self.__icon_normal

    @property
    def unique_id(self):
        """Return a unique ID to use for this sensor."""
        return self.config.get("unique_id", None)

    @property
    def device_info(self):
        return {
            "identifiers": {(DOMAIN, self.config.get("unique_id", None))},
            "name": self.config.get("name"),
            "manufacturer": "Garbage Collection",
        }

    @property
    def name(self):
        """Return the name of the sensor."""
        return self.__name

    @property
    def state(self):
        """Return the state of the sensor."""
        return self.__state

    @property
    def icon(self):
        return self.__icon

    @property
    def device_state_attributes(self):
        """Return the state attributes."""
        res = {}
        if self.__next_date is None:
            res[ATTR_NEXT_DATE] = None
        else:
            res[ATTR_NEXT_DATE] = datetime(
                self.__next_date.year, self.__next_date.month, self.__next_date.day
            ).astimezone()
        res[ATTR_DAYS] = self.__days
        return res

    def date_inside(self, dat: date) -> bool:
        month = dat.month
        if self.__first_month <= self.__last_month:
            return bool(month >= self.__first_month and month <= self.__last_month)
        else:
            return bool(month <= self.__last_month or month >= self.__first_month)

    def find_candidate_date(self, day1: date) -> date:
        """Find the next possible date starting from day1,
        only based on calendar, not lookimg at include/exclude days"""
        week = day1.isocalendar()[1]
        weekday = day1.weekday()
        year = day1.year
        if self.__frequency in ["weekly", "even-weeks", "odd-weeks", "every-n-weeks"]:
            # Everything except montthly
            # convert to every-n-weeks
            if self.__frequency == "weekly":
                period = 1
                first_week = 1
            elif self.__frequency == "even-weeks":
                period = 2
                first_week = 2
            elif self.__frequency == "odd-weeks":
                period = 2
                first_week = 1
            else:
                period = self.__period
                first_week = self.__first_week
            offset = -1
            if (week - first_week) % period == 0:  # Collection this week
                for day_name in self.__collection_days:
                    day_index = WEEKDAYS.index(day_name)
                    if day_index >= weekday:  # Collection still did not happen
                        offset = day_index - weekday
                        break
            if offset == -1:  # look in following weeks
                in_weeks = period - (week - first_week) % period
                offset = (
                    7 * in_weeks - weekday + WEEKDAYS.index(self.__collection_days[0])
                )
            return day1 + timedelta(days=offset)
        elif self.__frequency == "every-n-days":
            if self.__first_date is None or self.__period is None:
                _LOGGER.error(
                    "(%s) Please configure first_date and period for every-n-days collection frequency.",
                    self.__name,
                )
                return None

            if (day1 - self.__first_date).days % self.__period == 0:
                return day1
            offset = self.__period - ((day1 - self.__first_date).days % self.__period)
            return day1 + timedelta(days=offset)
        elif self.__frequency == "monthly":
            # Monthly
            if self.__monthly_force_week_numbers:
                for week_order_number in self._week_order_numbers:
                    candidate_date = nth_week_date(
                        week_order_number,
                        day1,
                        WEEKDAYS.index(self.__collection_days[0]),
                    )
                    # date is today or in the future -> we have the date
                    if candidate_date >= day1:
                        return candidate_date
            else:
                for weekday_order_number in self._weekday_order_numbers:
                    candidate_date = nth_weekday_date(
                        weekday_order_number,
                        day1,
                        WEEKDAYS.index(self.__collection_days[0]),
                    )
                    # date is today or in the future -> we have the date
                    if candidate_date >= day1:
                        return candidate_date
            if day1.month == 12:
                next_collection_month = date(year + 1, 1, 1)
            else:
                next_collection_month = date(year, day1.month + 1, 1)
            if self.__monthly_force_week_numbers:
                return nth_week_date(
                    self._week_order_numbers[0],
                    next_collection_month,
                    WEEKDAYS.index(self.__collection_days[0]),
                )
            else:
                return nth_weekday_date(
                    self._weekday_order_numbers[0],
                    next_collection_month,
                    WEEKDAYS.index(self.__collection_days[0]),
                )
        elif self.__frequency == "annual":
            # Annual
            if self.__date is None:
                _LOGGER.error(
                    "(%s) Please configure the date for annual collection frequency.",
                    self.__name,
                )
                return None
            conf_date = datetime.strptime(self.__date, "%m/%d").date()
            candidate_date = date(year, conf_date.month, conf_date.day)
            if candidate_date < day1:
                candidate_date = date(year + 1, conf_date.month, conf_date.day)
            return candidate_date
        elif self.__frequency == "group":
            if self.__entities is None:
                _LOGGER.error("(%s) Please add entities for the group.", self.__name)
                return None
            candidate_date = None
            for entity in self.__entities:
                d = self.hass.states.get(entity).attributes.get(ATTR_NEXT_DATE).date()
                if candidate_date is None or d < candidate_date:
                    candidate_date = d
            return candidate_date
        else:
            _LOGGER.debug(f"({self.__name}) Unknown frequency {self.__frequency}")
            return None

    def __insert_include_date(self, day1: date, next_date: date) -> date:
        include_dates = list(filter(lambda date: date >= day1, self.__include_dates))
        if len(include_dates) > 0 and include_dates[0] < next_date:
            _LOGGER.debug(
                "(%s) Inserting include_date %s", self.__name, include_dates[0]
            )
            return include_dates[0]
        else:
            return next_date

    def __skip_holiday(self, day: date) -> date:
        return day + timedelta(days=1)

    def get_next_date(self, day1: date) -> date:
        """Find the next date starting from day1."""
        first_day = day1
        i = 0
        while i < 365:
            next_date = self.find_candidate_date(first_day)
            while next_date in self.__holidays:
                _LOGGER.debug(
                    "(%s) Skipping public holiday on %s", self.__name, next_date
                )
                next_date = self.__skip_holiday(next_date)
            next_date = self.__insert_include_date(first_day, next_date)
            if next_date not in self.__exclude_dates:
                return next_date
            _LOGGER.debug("(%s) Skipping exclude_date %s", self.__name, next_date)
            first_day = next_date + timedelta(days=1)
            i += 1
        _LOGGER.error("(%s) Cannot find any suitable date", self.__name)
        return None

    async def async_update(self) -> None:
        """Get the latest data and updates the states."""
        today = dt_util.now().date()
        if self.__today is not None and self.__today == today:
            # _LOGGER.debug(
            #     "(%s) Skipping the update, already did it today",
            #     self.__name)
            return
        _LOGGER.debug("(%s) Calling update", self.__name)
        year = today.year
        month = today.month
        self.__today = today
        if self.date_inside(today):
            next_date = self.get_next_date(today)
            if next_date is not None:
                if not self.date_inside(next_date):
                    if self.__first_month <= self.__last_month:
                        next_year = date(year + 1, self.__first_month, 1)
                        next_date = self.get_next_date(next_year)
                        _LOGGER.debug(
                            "(%s) Did not find a date this year, "
                            "lookig at next year",
                            self.__name,
                        )
                    else:
                        next_year = date(year, self.__first_month, 1)
                        next_date = self.get_next_date(next_year)
                        _LOGGER.debug(
                            "(%s) Date not within the range, "
                            "searching again from %s",
                            self.__name,
                            MONTH_OPTIONS[self.__first_month - 1],
                        )
        else:
            if self.__first_month <= self.__last_month and month > self.__last_month:
                next_year = date(year + 1, self.__first_month, 1)
                next_date = self.get_next_date(next_year)
                _LOGGER.debug(
                    "(%s) Date outside range, lookig at next year", self.__name
                )
            else:
                next_year = date(year, self.__first_month, 1)
                next_date = self.get_next_date(next_year)
                _LOGGER.debug(
                    "(%s) Current date is outside of the range, "
                    "starting from first month",
                    self.__name,
                )

        self.__next_date = next_date
        if next_date is not None:
            self.__days = (next_date - today).days
            next_date_txt = next_date.strftime(self.__date_format)
            _LOGGER.debug(
                "(%s) Found next date: %s, that is in %d days",
                self.__name,
                next_date_txt,
                self.__days,
            )
            if self.__days > 1:
                if bool(self.__verbose_state):
                    self.__state = self.__verbose_format.format(
                        date=next_date_txt, days=self.__days
                    )
                    # self.__state = "on_date"
                else:
                    self.__state = 2
                self.__icon = self.__icon_normal
            else:
                if self.__days == 0:
                    if bool(self.__verbose_state):
                        self.__state = STATE_TODAY
                    else:
                        self.__state = self.__days
                    self.__icon = self.__icon_today
                elif self.__days == 1:
                    if bool(self.__verbose_state):
                        self.__state = STATE_TOMORROW
                    else:
                        self.__state = self.__days
                    self.__icon = self.__icon_tomorrow
        else:
            self.__days = None
