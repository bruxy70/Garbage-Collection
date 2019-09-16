# Garbage Collection

The `garbage_collection` component is a Home Assistant custom sensor for monitoring regular garbage collection schedule. The sensor can be configured for weekly schedule (including multiple collection days), bi-weekly in even or odd weeks, or monthly schedule (nth day each month). You can also configure seasonal calendars (e.g. for bio-waste collection), by configuring the first and last month. 

<img src="https://github.com/bruxy70/Garbage-Collection/blob/master/images/sensor.png">

## Configuration
Add `garbage_collection` sensor in your `configuration.yaml`. The following example adds three sensors - bio-waste with bi-weekly schedule, waste with weekly schedule and large-waste with monthly schedule on 1st Saturday each month:
```yaml
# Example configuration.yaml entry
sensor:
  - platform: garbage_collection
    name: waste # Each week on Wednesday
    frequency: "weekly"
    collection_days: wed
```
For more examples check the [README.md](https://github.com/bruxy70/Garbage-Collection/blob/development/README.md) file

### CONFIGURATION PARAMETERS
|Attribute |Optional|Description
|:----------|----------|------------
|`platform` | No | `garbage_collection`
|`collection_days` | No |Day three letter abbreviation, list of `"mon"`, `"tue"`, `"wed"`, `"thu"`, `"fri"`, `"sat"`, `"sun"`
|`frequency` | Yes | `"weekly"`, `"even-weeks"`, `"odd-weeks"` `"every-n-weeks"` or `"monthly"`<br/>**Default**: `"weekly"`<br/>*(The week number is using [ISO-8601](https://en.wikipedia.org/wiki/ISO_8601#Week_dates) numeric representatio of the week)*
|`name` | Yes | Sensor friendly name<br/>**Default**: `"garbage_collection"`
|`first_month` | Yes | Month three letter abbreviation, e.g. `"jan"`, `"feb"`...<br/>**Default**: `"jan"`
|`last_month` | Yes | Month three letter abbreviation.<br/>**Default**: `"dec"`
|`monthly_day_order_number` | Yes | List of week numbers of `collection_day` each month. E.g., if `collection_day` is `"sat"`, 1 will mean 1<sup>st</sup> Saturday each month (integer 1-4)<br/>**Default**: 1<br/>(relevant for `monthly_collection`)
|`period` | Yes | Collection every `"period"` weeks (integer 1-53)<br/>**Default**: 1<br/>(relevant for `every-n-weeks`)
|`first_week` | Yes | First collection on the `"first_week"` week (integer 1-53)<br/>**Default**: 1<br/>*(The week number is using [ISO-8601](https://en.wikipedia.org/wiki/ISO_8601#Week_dates) numeric representatio of the week)*<br/>(relevant for `every-n-weeks`)
| `exclude_dates` | Yes | List of dates with no collection (using international date format 'yyyy-mm-dd'. 
| `include_dates` | Yes | List of extra collection (using international date format 'yyyy-mm-dd'.
| `icon_normal` | Yes | Default icon **Default**:  `mdi:trash-can`
| `icon_today` | Yes | Icon if the collection is today **Default**: `mdi:delete-restore`
| `icon_tomorrow` | Yes | Icon if the collection is tomorrow **Default**: `mdi:delete-circle`
| `verbose_state` | Yes | The sensor state will show collection date and remaining days, instead of number **Default**: `False`

**IMPORTANT - put include/exclude dates within quotes. Dates without quotes might cause Home Assistant not loading configuration when starting - in case the date is invalid. Validation for dates within quotes works fine.** I think this is general bug, I am addressing that. (See the example above)

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

---
<a href="https://www.buymeacoffee.com/3nXx0bJDP" target="_blank"><img src="https://www.buymeacoffee.com/assets/img/custom_images/white_img.png" alt="Buy Me A Coffee" style="height: auto !important;width: auto !important;" ></a>
