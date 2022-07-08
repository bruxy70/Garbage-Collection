[![hacs_badge](https://img.shields.io/badge/HACS-Default-orange.svg)](https://github.com/custom-components/hacs) [![Garbage-Collection](https://img.shields.io/github/v/release/bruxy70/Garbage-Collection.svg?1)](https://github.com/bruxy70/Garbage-Collection) ![Maintenance](https://img.shields.io/maintenance/yes/2022.svg)

[![Buy me a coffee](https://img.shields.io/static/v1.svg?label=Buy%20me%20a%20coffee&message=🥨&color=black&logo=buy%20me%20a%20coffee&logoColor=white&labelColor=6f4e37)](https://www.buymeacoffee.com/3nXx0bJDP)

{% if prerelease %}

### NB!: This is a Beta version!

{% endif %}

# Garbage Collection

The `garbage_collection` component is a Home Assistant custom helper for scheduling/monitoring regular garbage collection. The helper can be configured for weekly schedule (including multiple collection days), bi-weekly (in even or odd weeks), monthly schedule (nth day each month), or annual (e.g. birthdays). You can also configure seasonal calendars (e.g. for bio-waste collection) by configuring the first and last month. You can also group entities, which will merge multiple schedules into one sensor.

## Examples

### Images (picture-entity)

<img src="https://github.com/bruxy70/Garbage-Collection/blob/master/images/picture-entity.png">

### List view (entities)

<img src="https://github.com/bruxy70/Garbage-Collection/blob/master/images/sensor.png">

### Icon view (glance)

<img src="https://github.com/bruxy70/Garbage-Collection/blob/master/images/entities.png">

### Garbage Collection custom card

<img src="https://github.com/amaximus/garbage-collection-card/blob/master/garbage_collection_lovelace.jpg">

Look to the <a href="https://github.com/bruxy70/Garbage-Collection">repository</a> for examples of Lovelace configuration.

## Configuration

Go to `Settings`/`Devices & Services`/`Helpers`, click on the `+ CREATE HELPER` button, select `Garbage Collection` and configure the helper.<br />If you would like to add more than one collection schedule, click on the `+ CREATE HELPER` button again and add another `Garbage Collection` helper instance.

The configuration via `configuration.yaml` has been deprecated. If you have previously configured the integration there, it will be imported to ConfigFlow, and you should remove it.

For the configuration documentation check the <a href="https://github.com/bruxy70/Garbage-Collection/blob/master/README.md">repository</a> file

## STATE AND ATTRIBUTES

### State

The state can be one of

| Value | Meaning                |
| :---- | ---------------------- |
| 0     | Collection is today    |
| 1     | Collection is tomorrow |
| 2     | Collection is later    |

If the `verbose_state` parameter is set, it will show the date, and remaining days. For example "Today" or "Tomorrow" or "on 2019-09-10, in 2 days"

### Attributes

| Attribute         | Description                              |
| :---------------- | ---------------------------------------- |
| `next_date`       | The date of next collection              |
| `days`            | Days till the next collection            |
| `last_collection` | The date and time of the last collection |

## Services

### garbage_collection.collect_garbage

If the collection is scheduled for today, mark it completed and look for the next collection.
It will set the `last_collection` attribute to the current date and time.

| Attribute   | Description                                                    |
| :---------- | -------------------------------------------------------------- |
| `entity_id` | The garbage collection entity id (e.g. `sensor.general_waste`) |

For more details see the <a href="https://github.com/bruxy70/Garbage-Collection/blob/master/README.md">repository.</a>
