[![hacs_badge](https://img.shields.io/badge/HACS-Default-orange.svg)](https://github.com/custom-components/hacs) [![Garbage-Collection](https://img.shields.io/github/v/release/bruxy70/Garbage-Collection.svg?1)](https://github.com/bruxy70/Garbage-Collection) ![Maintenance](https://img.shields.io/maintenance/yes/2019.svg)

[![Buy me a coffee](https://img.shields.io/static/v1.svg?label=Buy%20me%20a%20coffee&message=🥨&color=black&logo=buy%20me%20a%20coffee&logoColor=white&labelColor=6f4e37)](https://www.buymeacoffee.com/3nXx0bJDP)

# Garbage Collection

The `garbage_collection` component is a Home Assistant custom sensor for monitoring regular garbage collection schedule. The sensor can be configured for weekly schedule (including multiple collection days), bi-weekly in even or odd weeks, monthly schedule (nth day each month), or annualy (e.g. birthdays). You can also configure seasonal calendars (e.g. for bio-waste collection), by configuring the first and last month. And you can also group entities, which will merge multile schedules into one sensor.

<img src="https://github.com/bruxy70/Garbage-Collection/blob/master/images/sensor.png">

## Table of Contents
* [Installation](#installation)
  + [Manual Installation](#manual-installation)
  + [Installation via HACS](#installation-via-hacs)
* [Configuration](#configuration)
  + [Configuration Parameters](#configuration-parameters)
* [State and Attributes](#state-and-attributes)

## Installation

### MANUAL INSTALLATION
1. Download the
   [latest release](https://github.com/bruxy70/garbage_collection/releases/latest).
2. Unpack the release and copy the `custom_components/garbage_collection` directory
   into the `custom_components` directory of your Home Assistant
   installation.
3. Configure the `garbage_collection` sensor.
4. Restart Home Assistant.

### INSTALLATION VIA HACS
1. Ensure that [HACS](https://custom-components.github.io/hacs/) is installed.
2. Search for and install the "Garbage Collection" integration.
3. Configure the `garbage_collection` sensor.
4. Restart Home Assistant.

## Configuration
There are 2 ways to configure the integration:
1. Using *Config Flow*: in `Configuration/Integrations` click on the `+` button, select `Garbage Collection` and configure the sensor (prefered). If you configure Garbage Collection using Config Flow, you can change the entity_name, name and change the sensor parameters from the Integrations configuration. The changes are instant and do not require HA restart.
2. Using *YAML*: add `garbage_collection` integration in your `configuration.yaml` and add individual sensors. Example:

```yaml
# Example configuration.yaml entry
garbage_collection:
  sensors:
  - name: waste # Each week on Monday and Wednesday. No collection on Christmas, added extra collection on the 27th
    frequency: "weekly"
    collection_days:
    - mon
    - wed
    exclude_dates:
    - '2019-12-25'
    include_dates:
    - '2019-12-27'
  - name: "Bio-waste" # Bi-weekly (odd weeks) on Thursday. Between March and November
    frequency: "odd-weeks"
    first_month: "mar"
    last_month: "nov"
    collection_days: "thu"
  - name: "Large waste summer" # First and third saturday each month
    frequency: "monthly"
    collection_days: "sat"
    weekday_order_number: 
    - 1
    - 3
    first_month: "may"
    last_month: "oct"
  - name: "Large waste winter" # First and third saturday each month
    frequency: "monthly"
    collection_days: "sat"
    weekday_order_number: 
    - 1
    first_month: "nov"
    last_month: "apr"
  - name: "Large waste" # Combination of winter and summer sensors
    frequency: "group"
    entities:
    - sensor.large_waste_summer
    - sensor.large_waste_winter
  - name: Paper # Every 4 weeks on Tuesday, starting on 4th week each year
    frequency: "every-n-weeks"
    collection_days: "tue"
    period: 4
    first_week: 4
  - name: "Someone's Birthday" 
    frequency: "annual"
    date: '11/24'
```
Entity_id change is not possible using the YAML configuration. Changing other paratemers require restarting Home Assistant.

### CONFIGURATION PARAMETERS
#### GENERAL PARAMETERS
|Attribute |Optional|Description
|:----------|----------|------------
| `name` | No | Sensor friendly name
| `frequency` | Yes | `"weekly"`, `"even-weeks"`, `"odd-weeks"`, `"every-n-weeks"`, `"monthly"`, `"annual"` or `"group"`
| `icon_normal` | Yes | Default icon **Default**:  `mdi:trash-can`
| `icon_today` | Yes | Icon if the collection is today **Default**: `mdi:delete-restore`
| `icon_tomorrow` | Yes | Icon if the collection is tomorrow **Default**: `mdi:delete-circle`
| `verbose_state` | Yes | The sensor state will show collection date and remaining days, instead of number **Default**: `False`

#### PARAMETERS FOR ALL FREQUENCIES EXCEPT ANNUAL
|Attribute |Optional|Description
|:----------|----------|------------
| `collection_days` | No |Day three letter abbreviation, list of `"mon"`, `"tue"`, `"wed"`, `"thu"`, `"fri"`, `"sat"`, `"sun"`. 
| `first_month` | Yes | Month three letter abbreviation, e.g. `"jan"`, `"feb"`...<br/>**Default**: `"jan"`
| `last_month` | Yes | Month three letter abbreviation.<br/>**Default**: `"dec"`
| `exclude_dates` | Yes | List of dates with no collection (using international date format `'yyyy-mm-dd'`. 
| `include_dates` | Yes | List of extra collection (using international date format `'yyyy-mm-dd'`.

#### PARAMETERS FOR COLLECTION EVERY-N-WEEKS
|Attribute |Optional|Description
|:----------|----------|------------
|`period` | Yes | Collection every `"period"` weeks (integer 1-53)<br/>**Default**: 1
|`first_week` | Yes | First collection on the `"first_week"` week (integer 1-53)<br/>**Default**: 1<br/>*(The week number is using [ISO-8601](https://en.wikipedia.org/wiki/ISO_8601#Week_dates) numeric representatio of the week)*

#### PARAMETERS FOR MONTHLY COLLECTION
|Attribute |Optional|Description
|:----------|----------|------------
|`weekday_order_number` | Yes | List of week numbers of `collection_day` each month. E.g., if `collection_day` is `"sat"`, 1 will mean 1<sup>st</sup> Saturday each month (integer 1-4)<br/>**Default**: 1

#### PARAMETERS FOR ANNUAL COLLECTION
|Attribute |Optional|Description
|:----------|----------|------------
|`date` | No | Date of the collection using format `'mm/dd'` (e.g. '11/24' for November 24 each year)

#### PARAMETERS FOR GROUP
|Attribute |Optional|Description
|:----------|----------|------------
|`entities` | No | List of `entity_id`s to merge


**IMPORTANT - put include/exclude dates within quotes. Dates without quotes might cause Home Assistant not loading configuration when starting - in case the date is invalid. Validation for dates within quotes works fine.** I think this is general bug, I am addressing that. (See the example above)

## STATE AND ATTRIBUTES
### State
The state can be one of

| Value | Meaning
|:------|---------
| 0 | Collection is today
| 1 | Collection is tomorrow
| 2 | Collection is later 

If the `verbose_state` parameter is set, it will show date and remaining days, for example "Today" or "Tomorrow" or "on 10-Sep-2019, in 2 days"

### Attributes
| Attribute | Description
|:----------|------------
| `next_date` | The date of next collection
| `days` | Days till the next collection
