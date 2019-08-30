"""Support for garbage_collection sensors."""
import logging
from datetime import datetime, date, timedelta

import voluptuous as vol
from homeassistant.components.sensor import PLATFORM_SCHEMA
from homeassistant.util import Throttle
from homeassistant.const import (
    CONF_NAME
)
from homeassistant.core import HomeAssistant, State
import homeassistant.helpers.config_validation as cv
from homeassistant.helpers.entity import Entity

_LOGGER = logging.getLogger(__name__)

DEFAULT_NAME = "garbage_collection"

FREQUENCY_OPTIONS = ["weekly","even-weeks","odd-weeks","monthly","every-n-weeks"]
DAY_OPTIONS = ["mon","tue","wed","thu","fri","sat","sun"]
MONTH_OPTIONS = ["jan","feb","mar","apr","may","jun","jul","aug","sep","oct","nov","dec"]

DEFAULT_FIRST_MONTH = "jan"
DEFAULT_LAST_MONTH = "dec"
DEFAULT_FREQUENCY = "weekly"
DEFAULT_PERIOD = 1
DEFAULT_FIRST_WEEK = 1

ICON_TRASH = "mdi:trash-can"
ICON_TRASH_TODAY = "mdi:delete-restore"
ICON_TRASH_TOMORROW = "mdi:delete-circle"

CONF_NAME = "name"
CONF_FIRST_MONTH = "first_month"
CONF_LAST_MONTH = "last_month"
CONF_COLLECTION_DAYS = "collection_days"
CONF_FREQUENCY = "frequency"
CONF_MONTHLY_DAY_ORDER_NUMBER = "monthly_day_order_number"
CONF_EXCLUDE_DATES = "exclude_dates"
CONF_INCLUDE_DATES = "include_dates"
CONF_PERIOD = "period"
CONF_FIRST_WEEK = "first_week"

ATTR_NEXT_DATE = "next_date"
ATTR_DAYS = "days"

PLATFORM_SCHEMA = PLATFORM_SCHEMA.extend({
    vol.Required(CONF_COLLECTION_DAYS): vol.All(cv.ensure_list, [vol.In(DAY_OPTIONS)]),
    vol.Optional(CONF_FIRST_MONTH, default=DEFAULT_FIRST_MONTH): vol.In(MONTH_OPTIONS),
    vol.Optional(CONF_LAST_MONTH, default=DEFAULT_LAST_MONTH): vol.In(MONTH_OPTIONS),
    vol.Optional(CONF_FREQUENCY, default=DEFAULT_FREQUENCY): vol.In(FREQUENCY_OPTIONS),
    vol.Optional(CONF_MONTHLY_DAY_ORDER_NUMBER,default=1): vol.All(vol.Coerce(int), vol.Range(min=1, max=5)),
    vol.Optional(CONF_PERIOD, default=DEFAULT_PERIOD): vol.All(vol.Coerce(int), vol.Range(min=1, max=52)),
    vol.Optional(CONF_FIRST_WEEK, default=DEFAULT_FIRST_WEEK): vol.All(vol.Coerce(int), vol.Range(min=1, max=52)),
    vol.Optional(CONF_INCLUDE_DATES, default=[]): vol.All(cv.ensure_list, [cv.date]),
    vol.Optional(CONF_EXCLUDE_DATES, default=[]): vol.All(cv.ensure_list, [cv.date]),
    vol.Optional(CONF_NAME, default=DEFAULT_NAME): cv.string,
})

SCAN_INTERVAL = timedelta(seconds=60)
THROTTLE_INTERVAL = timedelta(seconds=60)

TRACKABLE_DOMAINS = ["sensor"]

def setup_platform(hass, config, add_devices, discovery_info=None):
    """Setup the sensor platform."""
    name = config.get(CONF_NAME)
    collection_days = config.get(CONF_COLLECTION_DAYS)
    first_month = config.get(CONF_FIRST_MONTH)
    last_month = config.get(CONF_LAST_MONTH)
    frequency = config.get(CONF_FREQUENCY)
    monthly_day_order_number = config.get(CONF_MONTHLY_DAY_ORDER_NUMBER)
    period = config.get(CONF_PERIOD)
    first_week = config.get(CONF_FIRST_WEEK)
    include_dates = config.get(CONF_INCLUDE_DATES)
    exclude_dates = config.get(CONF_EXCLUDE_DATES)
    add_devices([garbageSensor(hass, name, collection_days,first_month,last_month,frequency,monthly_day_order_number,period,first_week,include_dates,exclude_dates)])

class garbageSensor(Entity):
    """Representation of a openroute service travel time sensor."""
    def __init__(self, hass, name, collection_days,first_month,last_month,frequency,monthly_day_order_number,period,first_week,include_dates,exclude_dates):
        """Initialize the sensor."""
        self._hass = hass
        self._name = name
        self._collection_days = collection_days
        if first_month in MONTH_OPTIONS:
            self._first_month = MONTH_OPTIONS.index(first_month)+1
        else:
            self._first_month = 1
        if last_month in MONTH_OPTIONS:
            self._last_month = MONTH_OPTIONS.index(last_month)+1
        else:
            self._last_month = 12                 
        self._frequency = frequency
        self._monthly_day_order_number = monthly_day_order_number
        self._include_dates = include_dates
        self._exclude_dates = exclude_dates
        self._period = period
        self._first_week = first_week
        self._next_date = None
        self._today = None
        self._days = 0
        self._state = 2
        self._icon = ICON_TRASH

    @property
    def name(self):
        """Return the name of the sensor."""
        return self._name

    @property
    def state(self):
        """Return the name of the sensor."""
        return self._state

    @property
    def device_state_attributes(self):
        """Return the state attributes."""
        res = {}
        if self._next_date == None:
            res[ATTR_NEXT_DATE] = None
        else:    
            res[ATTR_NEXT_DATE] = datetime(self._next_date.year,self._next_date.month,self._next_date.day)
        res[ATTR_DAYS] = self._days
        return res

    @property
    def icon(self):
        return self._icon

    @Throttle(THROTTLE_INTERVAL)
    def update(self):
        """ Call the do_update function based on scan interval and throttle    """
        today = datetime.now().date()
        if self._today == None or self._today != today:
            self.do_update("Scan Interval")
        else:
            _LOGGER.debug( "(" + self._name + ") Skipping the update, already did it today")

    def date_inside(self,dat):
        month=dat.month
        if self._first_month <= self._last_month:
            if month >= self._first_month and month <= self._last_month:
                return True
            else:
                return False
        else:
            if month <= self._last_month or month >= self._first_month:
                return True
            else:
                return False

    def find_candidate_date(self, day1):
        """Find the next possible date starting from day1, only based on calendar, not lookimg at include/exclude days"""
        week = int(day1.strftime('%V'))
        day = int(day1.strftime('%u'))-1
        month = day1.month
        year = day1.year
        
        if self._frequency in ['weekly','even-weeks','odd-weeks','every-n-weeks']:
            if self._frequency == 'weekly':
                period = 1
                first_week = 1
            elif self._frequency == 'even-weeks':
                period = 2
                first_week = 2
            elif self._frequency == 'odd-weeks':
                period = 2
                first_week = 1
            else:
                period = self._period
                first_week = self._first_week
            offset = -1
            if (week-first_week) % period == 0: # Collection this week
                for day_name in self._collection_days:
                    day_index=DAY_OPTIONS.index(day_name)
                    if day_index >= day: # Collection still did not happen
                        offset = day_index-day
                        break
            if offset == -1: # look in following weeks
                in_weeks = period - (week-first_week) % period
                offset = 7*in_weeks-day+DAY_OPTIONS.index(self._collection_days[0])
            return day1 + timedelta(days=offset)
        elif self._frequency == 'monthly':
            # Monthly
            first_day=datetime(year,month,1).date()
            first_day_day=int(first_day.strftime('%u'))-1
            target_day_day=DAY_OPTIONS.index(self._collection_days[0])
            if target_day_day >= first_day_day:
                target_day = first_day + timedelta(days=target_day_day-first_day_day+(self._monthly_day_order_number-1)*7)
            else:
                target_day = first_day + timedelta(days=7-first_day_day+target_day_day+(self._monthly_day_order_number-1)*7)
            if target_day < day1:
                if month==12:
                    first_day=datetime(year+1,1,1).date()
                else:
                    first_day=datetime(year,month+1,1).date()
                first_day_day=int(first_day.strftime('%u'))-1
                target_day_day=DAY_OPTIONS.index(self._collection_days[0])
                if target_day_day >= first_day_day:
                    target_day = first_day + timedelta(days=target_day_day-first_day_day+(self._monthly_day_order_number-1)*7)
                else:
                    target_day = first_day + timedelta(days=7-first_day_day+target_day_day+(self._monthly_day_order_number-1)*7)
            return target_day
        else:
            _LOGGER.info( "(" + self._name + ") Unknown frequency " + self._frequency )
            return None

    def get_next_date(self, day1):
        """Find the nexte starting from day1. Looks at include and exclude days"""
        first_day=day1
        i=0
        while True:
            next_date = self.find_candidate_date(first_day)
            include_dates = list(filter(lambda date: date >= day1,self._include_dates))
            if len(include_dates)>0 and include_dates[0] < next_date:
                next_date = include_dates[0]
            if next_date not in self._exclude_dates:
                break
            else:
                first_day = next_date + timedelta(days=1)
            i=i+1
            if i>365:
                _LOGGER.error( "(" + self._name + ") Cannot find any suitable date" )
                next_date = None
                break
        return next_date

    def do_update(self, reason):
        """Get the latest data and updates the states."""
        _LOGGER.info( "(" + self._name + ") Calling update due to " + reason )
        today = datetime.now().date()
        year = today.year
        month = today.month
        self._today = today
        
        if self.date_inside(today):
            next_date=self.get_next_date(today)
            if next_date != None:
                next_date_year=next_date.year
                if not self.date_inside(next_date):
                    if self._first_month<=self._last_month:
                        next_year=datetime(next_date_year+1,self._first_month,1).date()
                        next_date=self.get_next_date(next_year)
                        _LOGGER.debug( "(" + self._name + ") Did not find the date this year, lookig at next year")
                    else:
                        next_year=datetime(next_date_year,self._first_month,1).date()
                        next_date=self.get_next_date(next_year)
                        _LOGGER.debug( "(" + self._name + ") Arrived to the end of date range, starting at first month")
        else:
            if self._first_month<=self._last_month and month>self._last_month:
                next_year=datetime(year+1,self._first_month,1).date()
                next_date=self.get_next_date(next_year)
                _LOGGER.debug( "(" + self._name + ") Current date is outside of the range, lookig at next year")
            else:
                next_year=datetime(year,self._first_month,1).date()
                next_date=self.get_next_date(next_year)
                _LOGGER.debug( "(" + self._name + ") Current date is outside of the range, starting from first month")
        self._next_date = next_date
        if next_date != None:
            self._days=(self._next_date-today).days
            _LOGGER.debug( "(" + self._name + ") Found next date: "+self._next_date.strftime("%d-%b-%Y")+", that is in "+str(self._days)+" days")
            if self._days > 1:
                self._state = 2
                self._icon = ICON_TRASH
            else:
                self._state = self._days
                if self._days == 0:
                    self._icon = ICON_TRASH_TODAY
                elif self._days == 1:
                    self._icon = ICON_TRASH_TOMORROW
        else:
            self._days=None
