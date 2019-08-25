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
```

### CONFIGURATION PARAMETERS
| Attribute | Optional | Description
|:----------|----------|------------
| `platform` | No | `garbage_collection`
| `collection_days` | No | Day three letter abbreviation, list of `"mon"`, `"tue"`, `"wed"`, `"thu"`, `"fri"`, `"sat"`, `"sun"`
| `frequency` | Yes | `"weekly"` or `"even-weeks"` or `"odd-weeks"` or `"monthly"`. **Default**: `"weekly"`
| `name` | Yes | Sensor friendly name. **Default**: `"garbage_collection"`
| `first_month` | Yes | Month three letter abbreviation, e.g. `"jan"`, `"feb"`... **Default**: `"jan"`
| `last_month` | Yes | Month three letter abbreviation.  **Default**: `"dec"`
| `monthly_day_order_number` | Yes | integer 1-4. Used for monthly collection - 1 for 1st `collection-day` each month, 2 for 2nd etc. **Default**: 1

## STATE AND ATTRIBUTES
<img src="https://github.com/bruxy70/Garbage-Collection/blob/master/images/sensor_state.jpg">

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
<a href="https://www.buymeacoffee.com/3nXx0bJDP" target="_blank"><img src="https://bmc-cdn.nyc3.digitaloceanspaces.com/BMC-button-images/custom_images/orange_img.png" alt="Buy Me A Coffee" style="height: auto !important;width: auto !important;" ></a>
