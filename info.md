# Garbage Collection

The `garbage_collection` component is a Home Assistant custom sensor for monitoring regular garbage collection schedule. The sensor can be configured for weekly schedule (including multiple collection days), bi-weekly in even or odd weeks, or monthly schedule (nth day each month). You can also configure seasonal callendars (e.g. for bio-waste collection), by configuring the first and last month. 

## Table of Contents
* [Configuration](#configuration)
  + [Configuration Parameters](#configuration-parameters)
* [State and Attributes](#state-and-attributes)

## Configuration
Add `garbage_collection` sensor in your `configuration.yaml`. The following example adds three sensors - bio-waste with bi-weekly schedule, waste with weekly schedule and large-waste with monthly schedule on 1st Saturday each month:
```yaml
# Example configuration.yaml entry
sensor:
  - platform: garbage_collection
    name: waste
    frequency: "weekly"
    collection_days:
    - mon
    - thu
  - platform: garbage_collection
    name: bio-waste
    frequency: "odd-weeks"
    first_month: "mar"
    last_month: "nov"
    collection_days: "thu"
  - platform: garbage_collection
    name: large-waste
    frequency: "monthly"
    collection_days: "sat"
    monthly_day_order_number: 1
  - platform: garbage_collection
    name: paper
    frequency: "every-n-weeks"
    collection_days: "tue"
    period: 4
    first_week: 4
```

### CONFIGURATION PARAMETERS
|Attribute |Optional|Description
|:----------|----------|------------
|`platform` | No |`garbage_collection`
|`collection_days` | No |Day three letter abbreviation, list of `"mon"`, `"tue"`, `"wed"`, `"thu"`, `"fri"`, `"sat"`, `"sun"`
|`frequency` | Yes |`"weekly"`, `"even-weeks"`, `"odd-weeks"` `"every-n-weeks"` or `"monthly"`<br/>**Default**: `"weekly"`<br/>*(The week number is using [ISO-8601](https://en.wikipedia.org/wiki/ISO_8601#Week_dates) numeric representatio of the week)*
|`name` | Yes |Sensor friendly name<br/>**Default**: `"garbage_collection"`
|`first_month` | Yes |Month three letter abbreviation, e.g. `"jan"`, `"feb"`...<br/>**Default**: `"jan"`
|`last_month` | Yes |Month three letter abbreviation.<br/>**Default**: `"dec"`
|`monthly_day_order_number` | Yes |Number of the `collection_day` each month. E.g., if `collection_day` is `"sat"`, 1 will mean 1<sup>st</sup> Sunday each month, 2 for 2<sup>nd</sup> Sunday each month etc. (integer 1-4)<br/>**Default**: 1<br/>(relevant for `monthly_collection`)
|`period` | Yes |Collection every `"period"` weeks (integer 1-53)<br/>**Default**: 1<br/>(relevant for `every-n-weeks`)
|`first_week` | Yes |First collection on the `"first_week"` week (integer 1-53)<br/>**Default**: 1<br/>*(The week number is using [ISO-8601](https://en.wikipedia.org/wiki/ISO_8601#Week_dates) numeric representatio of the week)*<br/>(relevant for `every-n-weeks`)

## STATE AND ATTRIBUTES
<img src="https://github.com/bruxy70/Garbage-Collection/blob/master/images/sensor.png">
(the configuration of this screenshot is described in [issue #4](https://github.com/bruxy70/Garbage-Collection/issues/4))

### State
The state can be one of

| Value | Meaning
|:------|---------
| 0 | Collection is today
| 1 | Collection is tomorrow
| 2 | Collection is later 

### Attributes
| Attribute | Description
|:----------|------------
| `next_date` | The date of next collection
| `days` | Days till the next collection

---
<a href="https://www.buymeacoffee.com/3nXx0bJDP" target="_blank"><img src="https://www.buymeacoffee.com/assets/img/custom_images/white_img.png" alt="Buy Me A Coffee" style="height: auto !important;width: auto !important;" ></a>
