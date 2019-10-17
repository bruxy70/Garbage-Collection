[![hacs_badge](https://img.shields.io/badge/HACS-Default-orange.svg)](https://github.com/custom-components/hacs) [![Garbage-Collection](https://img.shields.io/github/v/release/bruxy70/Garbage-Collection.svg?1)](https://github.com/bruxy70/Garbage-Collection) ![Maintenance](https://img.shields.io/maintenance/yes/2019.svg)

[![Buy me a coffee](https://img.shields.io/static/v1.svg?label=Buy%20me%20a%20coffee&message=🥨&color=black&logo=buy%20me%20a%20coffee&logoColor=white&labelColor=6f4e37)](https://www.buymeacoffee.com/3nXx0bJDP)

# Garbage Collection

The `garbage_collection` component is a Home Assistant custom sensor for monitoring regular garbage collection schedule. The sensor can be configured for weekly schedule (including multiple collection days), bi-weekly in even or odd weeks, or monthly schedule (nth day each month) or anual (e.g. birthdays). You can also configure seasonal calendars (e.g. for bio-waste collection), by configuring the first and last month. 

<img src="https://github.com/bruxy70/Garbage-Collection/blob/master/images/sensor.png">

## Configuration
There are 2 ways to configure the integration:
1. Using *Congfig Flow*: in `Configuration/Integrations` click on the `+` button, select `Garbage Collection` and configure the sensor.
2. Using *YAML*: add `garbage_collection` integration in your `configuration.yaml` and add individual sensors. The following example adds 4 sensors - bio-waste with bi-weekly schedule, waste with weekly schedule and large-waste with monthly schedule on 1st Saturday each month. And a birthday:
```yaml
# Example configuration.yaml entry
garbage_collection:
  sensors:
  - name: Waste # Each week on Wednesday
    frequency: "weekly"
    collection_days: wed
  - name: Bio # Each week on Wednesday
    frequency: "odd-weeks"
    collection_days: thu
    first_month: "mar"
    last_month: "nov"
  - name: Large Waste
    frequency: "monthly"
    collection_days: sat
    weekday_order_number: 1
  - name: 'Someone's birthday'
    frequency: 'annual'
    date: '11/24'
```
For more examples and configuration documentation check the [README.md](https://github.com/bruxy70/Garbage-Collection/blob/development/README.md) file

## STATE AND ATTRIBUTES

### State
The state can be one of

| Value | Meaning
|:------|---------
| 0 | Collection is today
| 1 | Collection is tomorrow
| 2 | Collection is later 

If the `verbose_state` parameter is set, it will show date and remaining days, for example "Today" or "Tomorrow" or "on 2019-09-10, in 2 days"

### Attributes
| Attribute | Description
|:----------|------------
| `next_date` | The date of next collection
| `days` | Days till the next collection
