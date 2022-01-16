[![hacs_badge](https://img.shields.io/badge/HACS-Default-orange.svg)](https://github.com/custom-components/hacs) [![Garbage-Collection](https://img.shields.io/github/v/release/bruxy70/Garbage-Collection.svg?1)](https://github.com/bruxy70/Garbage-Collection) ![Maintenance](https://img.shields.io/maintenance/yes/2021.svg)

[![Buy me a coffee](https://img.shields.io/static/v1.svg?label=Buy%20me%20a%20coffee&message=🥨&color=black&logo=buy%20me%20a%20coffee&logoColor=white&labelColor=6f4e37)](https://www.buymeacoffee.com/3nXx0bJDP)

# Garbage Collection

The `garbage_collection` componnent is a Home Assistant integration that creates a custom sensor for monitoring regular garbage collection schedule. The sensor can be configured for number of different schedules:
- `weekly` schedule (including multiple collection days, e.g. on Tuesday and Thursday)
- `every-n-weeks` repeats every `period` of weeks, starting from the week number `first_week`. It uses the week number - it therefore restarts each year, as the week numbers start again from 1.
- bi-weekly in `even-weeks` or `odd-weeks` (technically, it is the same as every 2 weeks with 1<sup>st</sup> or 2<sup>nd</sup> `first_week`)
- `every-n-days` (repeats regularly from the given first date). If n is multiply of 7, it works similar to `every-n-weeks`, with the difference that it does not use the week numbers (that restart each year) but continues infinitely from the initial date.
- `monthly` schedule (n<sup>th</sup> weekday each month), or a specific weekday of each n<sup>th</sup> week. Using the `period` it could also be every 2<sup>nd</sup>, 3<sup>rd</sup> etc month.
- `annually` (e.g. birthdays). This is once per year. Using include dates you can add additional dates manually.
- `blank` does not automatically schedule any collections - in case you want make completely own schedule with `manual_update`.
You can also configure seasonal calendars (e.g. for bio-waste collection), by configuring the first and last month. 
And you can `group` entities, which will merge multiple schedules into one sensor.

These are some examples using this sensor. The Lovelace config examples are included below.
<img src="https://github.com/bruxy70/Garbage-Collection/blob/master/images/picture-entity.png">

<img src="https://github.com/bruxy70/Garbage-Collection/blob/master/images/entities.png">

<img src="https://github.com/bruxy70/Garbage-Collection/blob/master/images/sensor.png">

<img src="https://github.com/amaximus/garbage-collection-card/blob/master/garbage_collection_lovelace.jpg">

## Table of Contents
* [Installation](#installation)
  + [Manual Installation](#manual-installation)
  + [Installation via Home Assistant Community Store (HACS)](#installation-via-home-assistant-community-store-hacs)
* [Configuration](#configuration)
  + [Configuration Parameters](#configuration-parameters)
* [State and Attributes](#state-and-attributes)
* [Lovelace configuration examples](#lovelace-config-examples)

## Installation

### MANUAL INSTALLATION
1. Download the
   [latest release](https://github.com/bruxy70/garbage_collection/releases/latest).
2. Unpack the release and copy the `custom_components/garbage_collection` directory
   into the `custom_components` directory of your Home Assistant
   installation.
3. Configure the `garbage_collection` sensor.
4. Restart Home Assistant.

### INSTALLATION VIA Home Assistant Community Store (HACS)
1. Ensure that [HACS](https://hacs.xyz/) is installed.
2. Search for and install the "Garbage Collection" integration.
3. Configure the `garbage_collection` sensor.
4. Restart Home Assistant.

## Configuration
__Based on the [Home Assistant design guideline](https://www.home-assistant.io/blog/2020/04/14/the-future-of-yaml/#the-future-of-yaml), the YAML configuratio option will be removed in the future.__

There are 2 ways to configure the integration:
1. Using *Config Flow*: in `Configuration/Integrations` click on the `+` button, select `Garbage Collection` and configure the sensor (prefered). If you configure Garbage Collection using Config Flow, you can change the entity_name, name and change the sensor parameters from the Integrations configuration. The changes are instant and do not require HA restart.<br />If you would like to add more than 1 collection schedule, click on the `+` button again and add another `Garbage Collection` integration instance.
2. Using *YAML* (deprecated): add `garbage_collection` integration in your `configuration.yaml` and add individual sensors. 
<details>
  <summary>YAML configuration example:</summary>
  
```yaml
# Example configuration.yaml entry
garbage_collection:
  sensors:
  - name: "Regular waste" # Each week on Monday and Wednesday. No collection on Christmas, added extra collection on the 27th
    frequency: "weekly"
    collection_days:
    - mon
    - wed
    expire_after: '12:00'
    exclude_dates:
    - '2019-12-25'
    include_dates:
    - '2019-12-27'
  - name: "Bio-waste" # Bi-weekly (odd weeks) on Thursday. Between March and November
    frequency: "odd-weeks"
    first_month: "mar"
    last_month: "nov"
    collection_days: "thu"
  - name: "Large waste summer" # First and third Saturday each month
    frequency: "monthly"
    collection_days: "sat"
    weekday_order_number: 
    - 1
    - 3
    first_month: "may"
    last_month: "oct"
  - name: "Large waste winter" # First Saturday each month only
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
  
</details>
Entity_id change is not possible using the YAML configuration. Changing other paratemers require restarting Home Assistant.

### CONFIGURATION PARAMETERS
#### SENSOR PARAMETERS
|Attribute |Required|Description
|:----------|----------|------------
| `name` | Yes | Sensor friendly name
| `frequency` | Yes | `"weekly"`, `"even-weeks"`, `"odd-weeks"`, `"every-n-weeks"`, `"every-n-days"`, `"monthly"`, `"annual"`, `"group"` or `"blank"`
| `manual_update` | No | (Advanced). Do not automatically update the status. Status is updated manualy by calling the service `garbage_collection.update_state` from an automation triggered by event `garbage_collection_loaded`, that could manually add or remove collection dates, and manually trigger the state update at the end. [See the example](#manual-update-example).</br>**Default**: `False`
| `offset` | No | Offset calculated date by `offset` days (makes most sense for monthly frequency). Examples of use:</br>for last Saurday each month, configure first Saturday each month with `offset: -7`</br>for 1<sup>st</sup> Wednesday in of full week, configure first Monday each month with `offset: 2`</br>(integer between -31 and 31) **Default**: 0
| `hidden` | No | Hide in calendar (useful for sensors that are used in groups)<br/>**Default**: `False`
| `icon_normal` | No | Default icon **Default**:  `mdi:trash-can`
| `icon_today` | No | Icon if the collection is today **Default**: `mdi:delete-restore`
| `icon_tomorrow` | No | Icon if the collection is tomorrow **Default**: `mdi:delete-circle`
| `expire_after` | No | Time in format format `HH:MM`. If the collection is due today, start looking for the next occurence after this time (i.e. if the weekly collection is in the morning, change the state from 'today' to next week in the afternoon)
| `verbose_state` | No | The sensor state will show collection date and remaining days, instead of number **Default**: `False`
| `verbose_format` | No | (relevant when `verbose_state` is `True`). Verbose status formatting string. Can use placeholders `{date}` and `{days}` to show the date of next collection and remaining days. **Default**: `'on {date}, in {days} days'`</br>*When the collection is today or tomorrow, it will show `Today` or `Tomorrow`*</br>*(currently in English, French, Czech and Italian).*
| `date_format` | No | In the `verbose_format`, you can configure the format of date (using [strftime](http://strftime.org/) format)  **Default**: `'%d-%b-%Y'`


#### PARAMETERS FOR ALL FREQUENCIES EXCEPT ANNUAL, GROUP and BLANK
|Attribute |Required|Description
|:----------|----------|------------
| `first_month` | No | Month three letter abbreviation, e.g. `"jan"`, `"feb"`...<br/>**Default**: `"jan"`
| `last_month` | No | Month three letter abbreviation.<br/>**Default**: `"dec"`
| `exclude_dates` | No | List of dates with no collection (using international date format `'yyyy-mm-dd'`. Make sure to enter the date in quotes!
| `include_dates` | No | List of extra collection (using international date format `'yyyy-mm-dd'`. Make sure to enter the date in quotes!
| `move_country_holidays` | No | Country holidays - the country code (see [holidays](https://github.com/dr-prodigy/python-holidays) for the list of valid country codes).<br/>Automatically move garbage collection on public holidays to the following day.<br/>*Example:* `US` 
| `holiday_in_week_move` | No | Move garbage collection to the following day if a holiday is in week.<br/>**Default**: `false`
| `holiday_move_offset` | No | Move the collection by the number of days (integer -7..7) **Default**: 1
| `holiday_pop_named` | No | Ignore holidays (list of holiday names) *Example:* `"Columbus Day"`, `"Veterans Day"`
| `prov` | No | Country holidays - province (see [holidays](https://github.com/dr-prodigy/python-holidays) ).
| `state` | No | Country holidays - state (see [holidays](https://github.com/dr-prodigy/python-holidays) ).
| `observed` | No | Country holidays - observed (see [holidays](https://github.com/dr-prodigy/python-holidays) ).


#### PARAMETERS FOR ALL FREQUENCIES EXCEPT ANNUAL, EVERY-N-DAYS, GROUP and BLANK
|Attribute |Required|Description
|:----------|----------|------------
| `collection_days` | Yes | Day three letter abbreviation, list of `"mon"`, `"tue"`, `"wed"`, `"thu"`, `"fri"`, `"sat"`, `"sun"`. 


#### PARAMETERS FOR COLLECTION EVERY-N-WEEKS
|Attribute |Required|Description
|:----------|----------|------------
|`period` | No | Collection every `"period"` weeks (integer 1-53)<br/>**Default**: 1
|`first_week` | No | First collection on the `"first_week"` week (integer 1-53)<br/>**Default**: 1<br/>*(The week number is using [ISO-8601](https://en.wikipedia.org/wiki/ISO_8601#Week_dates) numeric representatio of the week)<br/><br/>Note: This parameter cannot be used to set the beginning of the collection period (use the `first_month` parameter for that). The purpose of `first_week` is to simply 'offset' the week number, so that the collection every n weeks does not always trigger on week numbers that are multiply of n. Technically, the value of this parameter shall be less than `period`, otherwise it will give weird results. Also note that the week numbers restart each year. Use `every-n-days` frequency if you need consistent period across the year ends.*


#### PARAMETERS FOR COLLECTION EVERY-N-DAYS
|Attribute |Required|Description
|:----------|----------|------------
|`first_date` | Yes | Repeats every n days from this first date<br>(date in the international ISO format `'yyyy-mm-dd'`).
|`period` | No | Collection every `"period"` days (warning - in this configuration it is days, not weeks!)<br/>**Default**: 1 (daily, which makes no sense I suppose)


#### PARAMETERS FOR MONTHLY COLLECTION
The monthly schedule has two flavors: it can trigger either on the **n<sup>th</sup> occurrence of the weekday** in a month, or on the weekday in the **n<sup>th</sup> week** of each month.

|Attribute |Required|Description
|:----------|----------|------------
|`weekday_order_number` | Yes/No | List of week numbers of `collection_day` each month. E.g., if `collection_day` is `"sat"`, 1 will mean 1<sup>st</sup> Saturday each month (integer 1-5)
|`week_order_number` | Yes/No | Similar to `weekday_order_number`, but instead of n<sup>th</sup> weekday of each month, take the weekday of the n<sup>th</sup> week of each month.</br>So if the month starts on Friday, the Wednesday of the 1<sup>st</sup> week would actually be last Wednesday of the previous month and the Wednesday of 2<sup>nd</sup> week will be the 1<sup>st</sup> Wednesday of the month.
|`period` | No | If `period` is not defined (or 1), the schedule will repeat monthly. If `period` is 2, it will be every 2<sup>nd</sup> month. If `period` is 3, it will be once per quarter, and so on.<br/>The `first_month` parameter will then define the starting month. So if the `first_month` is `jan` (or not defined), and `period` is 2, the collection will be in odd months (`jan`, `mar`, `may`, `jul`, `sep` and `nov`). If `first_month` is `feb`, it will be in even months. (integer 1-12)<br/>**Default**: 1

*One of the parameters `weekday_order_number` or `week_order_number` has to be defined. But you cannot combine both options in one sensor.*

#### PARAMETERS FOR ANNUAL COLLECTION
|Attribute |Required|Description
|:----------|----------|------------
|`date` | Yes | Date of the collection using format `'mm/dd'` (e.g. '11/24' for November 24 each year)

#### PARAMETERS FOR GROUP
|Attribute |Required|Description
|:----------|----------|------------
|`entities` | Yes | List of `entity_id`s to merge


**IMPORTANT - put include/exclude dates within quotes. Dates without quotes might cause Home Assistant not loading configuration when starting - in case the date is invalid. Validation for dates within quotes works fine.** I think this is general bug, I am addressing that. (See the example above)

## STATE AND ATTRIBUTES
### State
The state can be one of

| Value | Meaning
|:------|---------
| 0 | Collection is today
| 1 | Collection is tomorrow
| 2 | Collection is later 

If the `verbose_state` parameter is set, it will show date and remaining days, for example "Today" or "Tomorrow" or "on 10-Sep-2019, in 2 days" (configurable)

### Attributes
| Attribute | Description
|:----------|------------
| `next_date` | The date of next collection
| `days` | Days till the next collection
| `holidays` | List of used country (showing this year)
| `last_collection` | Date and time of the last collection


## Services
### garbage_collection.collect_garbage
If the collection is scheduled for today, mark it completed and look for the next collection.
It will set the `last_collection` attribute to the current date and time.

| Attribute | Description
|:----------|------------
| `entity_id` | The garbage collection entity id (e.g. `sensor.general_waste`)


### garbage_collection.add_date
...see the manual update example below

### garbage_collection.remove_date
...see the manual update example below

### garbage_collection.offset_date
...see the manual update example below

### garbage_collection.update_state
...see the manual update example below


## Manual update example
(!!! Advanced - if you think this is too complicated, then this is not for you !!!)

For the example below, the entity should be configured with `manual_update` set to `true`.
Then, when the `garbage_collection` entity is updated (normally once a day at midnight, or restart, or when triggering entity update by script), it will calculate the collection schedule for previous, current and next year. But it will **NOT UPDATE** the entity state. 
Instead, it will trigger an event `garbage_collection_loaded` with list of automatically calculated dates as a parameter. 
You will **have to create an automation triggered by this event**. In this automation you will need to call the service `garbage_collection.update_state` to update the state. Before that, you can call the servics `garbage_collection.add_date` and/or `garbage_collection.remove_date` to programatically tweak the dates in whatever way you need (e.g. based on values from external API sensor, comparing the dates with list of holidays, calculating custom offsets based on the day of the week etc.). This is complicated, but gives you an ultimate flexibility.

I made couple of [Blueprints](https://github.com/bruxy70/Garbage-Collection/tree/development/blueprints) to automatically move collection on pubic holidays using the manual update. The goal is to simplify this integration moving forward by removing the holidays feature and moving that to bluprints called by manual update. I am also in a process of creating a dedicated integration just for holidays. So you can check it out now and let me know. If you try that, just make sure you either use holidays from another `garbage_collection` entity, or set the `move_offset` to `0` - otherwise both the integration and the blueprint will move the collection, so it might move twice I think.

### garbage_collection.add_date
Add a date to the list of dates calculated automatically. To add multiple dates, call this service multiple times with different dates.
Note that this date will be removed on the next sensor update when data is re-calculated and loaded. This is why this service should be called from the automation triggered be the event `garbage_collection_loaded`, that is called each time the sensor is updated. And at the end of this automation you need to call the `garbage_collection.update_state` service to update the sensor state based on automatically collected dates with the dates added, removed or offset by the automation.

| Attribute | Description
|:----------|------------
| `entity_id` | The garbage collection entity id (e.g. `sensor.general_waste`)
| `date` | The date to be added, in ISO format (`'yyyy-mm-dd'`). Make sure to enter the date in quotes!

### garbage_collection.remove_date
Remove a date to the list of dates calculated automatically. To remove multiple dates, call this service multiple times with different dates.
Note that this date will reappear on the next sensor update when data is re-calculated and loaded. This is why this service should be called from the automation triggered be the event `garbage_collection_loaded`, that is called each time the sensor is updated. And at the end of this automation you need to call the `garbage_collection.update_state` service to update the sensor state based on automatically collected dates with the dates added, removed or offset by the automation.

| Attribute | Description
|:----------|------------
| `entity_id` | The garbage collection entity id (e.g. `sensor.general_waste`)
| `date` | The date to be removed, in ISO format (`'yyyy-mm-dd'`). Make sure to enter the date in quotes!

### garbage_collection.offset_date
Offset the calculated collection day by the `offset` number of days.
Note that this offset will revert back on the next sensor update when data is re-calculated and loaded. This is why this service should be called from the automation triggered be the event `garbage_collection_loaded`, that is called each time the sensor is updated. And at the end of this automation you need to call the `garbage_collection.update_state` service to update the sensor state based on automatically collected dates with the dates added,  removed or offset by the automation.

| Attribute | Description
|:----------|------------
| `entity_id` | The garbage collection entity id (e.g. `sensor.general_waste`)
| `date` | The date to be removed, in ISO format (`'yyyy-mm-dd'`). Make sure to enter the date in quotes!
| `offset` | By how many days to offset - integer between `-31` to `31` (e.g. `1`)

### garbage_collection.update_state
Choose the next collection date from the list of dates calculated automatically, added by service calls (and not removed), and update the entity state and attributes.

| Attribute | Description
|:----------|------------
| `entity_id` | The garbage collection entity id (e.g. `sensor.general_waste`)

## Events
### garbage_collection_loaded 
This event is triggered each time a `garbage_collection` entity is being updated. You can create an automation to modify the collection schedule before the entity state update.

Event data:
| Attribute | Description
|:----------|------------
| `entity_id` | The garbage collection entity id (e.g. `sensor.general_waste`)
| `collection_dates` | List of collection dates calculated automatically.

## Simple example
Adding an extra collection date (a fixed date in this case) - for the entity `sensor.test`.


```yaml
alias: garbage_collection event
description: 'Manually add a collection date, then trigger entity state update.'
trigger:
  - platform: event
    event_type: garbage_collection_loaded
    event_data:
      entity_id: sensor.test
action:
  - service: garbage_collection.add_date
    data:
      entity_id: "{{ trigger.event.data.entity_id }}"
      date: '2022-01-07'
  - service: garbage_collection.update_state
    data:
      entity_id: sensor.test
mode: single
```

## Moderate example
This will loop through the calculated dates, and add extra collection to a day after each calculated one. So if this is set for a collection each first Wednesday each month, it will result in a collection on first Wednesday, and the following day (kind of first Thursday, except if the week is starting on Thursday - just a random weird example :).

This example is for an entity `sensor.test`. If you want to use it for yours, replace it with the real entity name in the trigger.

```yaml
alias: test garbage_collection event
description: 'Loop through all calculated dates, add extra collection a day after the calculate one'
trigger:
  - platform: event
    event_type: garbage_collection_loaded
    event_data:
      entity_id: sensor.test
action:
  - repeat:
      count: '{{ trigger.event.data.collection_dates | count }}'
      sequence:
        - service: garbage_collection.add_date
          data:
            entity_id: "{{ trigger.event.data.entity_id }}"
            date: >-
              {{( as_datetime(trigger.event.data.collection_dates[repeat.index-1]) + timedelta( days = 1)) | as_timestamp | timestamp_custom("%Y-%m-%d") }}
  - service: garbage_collection.update_state
    data:
      entity_id: "{{ trigger.event.data.entity_id }}"
mode: single
```

## Advanced example
This is an equivalent of "holiday in week" move - checking if there is a public holiday on the calculated collection day, or in the same day before, and if yes, moving the collection by one day. This is fully custom logic, so it could be further complicated by whatever rules anyone wants.
Note that this does not disable the current holiday exception handling in the integration - so if you have also configured that to move the collection, it will move it one more day. So if you want to use, configure the `offset` to `0` (so that the integration movves the holiday by "zero" days). Or you can configure the calendar on another entity - the automation is really using them to check the list of the dates - the list could be anywhere, does not even have to be a garbage_collection entity.

This example is for an entity `sensor.test`. If you want to use it for yours, replace it with the real entity name in the trigger.

```yaml
alias: test garbage_collection event
description: >-
  Loop through all calculated dates, move the collection by 1 day if public holiday was in the week before or on the calculated collection date calculate one
trigger:
  - platform: event
    event_type: garbage_collection_loaded
    event_data:
      entity_id: sensor.test
action:
  - repeat:
      count: '{{ trigger.event.data.collection_dates | count }}'
      sequence:
        - condition: template
          value_template: >-
            {%- set collection_date = as_datetime(trigger.event.data.collection_dates[repeat.index-1]) %}
            {%- set ns = namespace(found=false) %}
            {%- for i in range(collection_date.weekday()+1) %}
              {%- set d = ( collection_date + timedelta( days=-i) ) | as_timestamp | timestamp_custom("%Y-%m-%d") %}
              {%- if d in state_attr(trigger.event.data.entity_id,'holidays') %}
                {%- set ns.found = true %}
              {%- endif %}
            {%- endfor %}  
            {{ ns.found }}
        - service: garbage_collection.offset_date
          data:
            entity_id: "{{ trigger.event.data.entity_id }}"
            date: '{{ trigger.event.data.collection_dates[repeat.index-1] }}'
            offset: 1
  - service: garbage_collection.update_state
    data:
      entity_id: "{{ trigger.event.data.entity_id }}"
mode: single
```

Or you can use the [blueprints](https://github.com/bruxy70/Garbage-Collection/tree/development/blueprints) I made for you. And you are welcome to create your own and share with the others.

# Lovelace config examples

## Garbage Collection custom card
You can use the custom  [garbage collection card](https://github.com/amaximus/garbage-collection-card) developped by @amaximus.

<img src="https://github.com/amaximus/garbage-collection-card/blob/master/garbage_collection_lovelace.jpg">


## With images (picture-entity)
This is what I use (I like images). I use a horizontal stack of picture-entities, with `card-templater` plugin ([Lovelace Card Templater](https://github.com/gadgetchnnel/lovelace-card-templater)) to show number of days:

<img src="https://github.com/bruxy70/Garbage-Collection/blob/master/images/picture-entity.png">

(The `state` is designed to be used like traffic lights, this is why it has 3 values. You obviously cannot use this with `verbose_state`)

This is the configuration
```yaml
      - type: 'custom:card-templater'
        card:
          type: picture-entity
          name_template: >-
            {{ state_attr('sensor.bio','days') }} days
          show_name: True
          show_state: False
          entity: sensor.bio
          state_image:
            "0": "/local/containers/bio_today.png"
            "1": "/local/containers/bio_tomorrow.png"
            "2": "/local/containers/bio_off.png"
        entities:
          - sensor.bio
```

## List view (entities)
The simplest visualisation is to use entities. In this case, I use `verbose_state` to show `state` as text.

<img src="https://github.com/bruxy70/Garbage-Collection/blob/master/images/entities.png">

Integration configuration (you can customise state text by `verbose_format` and `date_format` parameters)
```yaml
garbage_collection:
  sensors:
  - name: General Waste
    frequency: 'weekly'
    collection_days: wed
    verbose_state: True
  etc...
```
Lovelace configuration
```yaml
      - type: entities
        entities:
          - sensor.general_waste
          - sensor.bio
          - sensor.paper
          - sensor.plastic
```

## Icon view (glance)
<img src="https://github.com/bruxy70/Garbage-Collection/blob/master/images/sensor.png">

Integration configuration
```yaml
garbage_collection:
  sensors:
  - name: General Waste
    frequency: 'weekly'
    collection_days: wed
    verbose_state: True
    verbose_format: "on {date}, in {days} days"
  etc...
```

Configuration
```yaml
      - type: glance
        entities:
          - sensor.general_waste
```
