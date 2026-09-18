---
layout: default
title: "Monitor healthcare provider changes"
description: "Compare scheduled CMS provider snapshots to detect ownership, rating, staffing, inspection, penalty, and service changes for facilities you follow."
permalink: /tutorials/monitor-healthcare-provider-changes/
---
# How to monitor CMS healthcare-provider changes

CMS publishes rich facility directories, but it is easier to act on changes than to reread a full directory. This workflow runs the public [CMS Healthcare Provider Search Actor](https://apify.com/captainhandsome/cms-healthcare-provider-search) on a schedule, compares each snapshot by CMS Certification Number, and emits only new, removed, or changed facilities.

The Actor covers hospitals, nursing homes, home health agencies, hospices, dialysis facilities, long-term care hospitals, and inpatient rehabilitation facilities. It does not provide patient records or clinical-trial data.

## Try the current dataset shape

Open [Build a California Hospital Directory](https://apify.com/captainhandsome/cms-healthcare-provider-search/examples/california-hospital-directory) to run a public example and inspect the resulting rows.

For an actual monitor, keep the scope narrow enough that every expected facility fits below `max_items`. A truncated snapshot cannot distinguish a removed provider from a provider that fell beyond the limit.

```json
{
  "provider_types": ["nursing_home"],
  "state": "TX",
  "county": "Harris",
  "max_items": 250
}
```

Save the input as a task and schedule it weekly in Apify Console. CMS datasets update on source-specific cycles, so running every few minutes adds cost without creating fresher source data.

## Choose a stable key and fields to watch

Use the pair `(provider_type, ccn)` as the record key. `ccn` is the CMS Certification Number, and including provider type prevents accidental collisions across directories.

Useful common fields include `name`, `address`, `phone`, `ownership`, `star_rating`, `certification_date`, and `data_processing_date`. Nursing-home monitoring can additionally watch:

- `ownership_changed_last_12_months`, `chain`, and `chain_owned`
- `health_inspection_rating`, `staffing_rating`, and `quality_measure_rating`
- `special_focus_status`, `abuse_flag`, and `infection_control_citations`
- `number_of_fines`, `total_fines_usd`, and `number_of_payment_denials`
- staffing hours, turnover percentages, deficiencies, and the last inspection date

Not every field applies to every provider type. A null dialysis staffing field on a hospital is not a change or an error.

## Compare two snapshots

The essential comparison is small enough to keep explicit:

```python
WATCH = {
    "name", "address", "phone", "ownership", "star_rating",
    "special_focus_status", "abuse_flag", "number_of_fines",
    "total_fines_usd", "staffing_rating", "health_inspection_rating",
}

def keyed(rows):
    return {(row["provider_type"], row["ccn"]): row for row in rows}

def changes(previous_rows, current_rows):
    previous, current = keyed(previous_rows), keyed(current_rows)
    events = []
    for key in current.keys() - previous.keys():
        events.append({"type": "added", "key": key, "current": current[key]})
    for key in previous.keys() - current.keys():
        events.append({"type": "removed", "key": key, "previous": previous[key]})
    for key in previous.keys() & current.keys():
        diff = {field: {"before": previous[key].get(field), "after": current[key].get(field)}
                for field in WATCH if previous[key].get(field) != current[key].get(field)}
        if diff:
            events.append({"type": "changed", "key": key, "fields": diff})
    return events
```

Retain the source snapshot even after creating the change events. It provides the evidence needed to review a surprising alert. Treat a missing record cautiously until a second complete run confirms it, because an upstream interruption can resemble a removal.

## Ask an AI agent through MCP

With [Apify Public Data MCP](/) installed:

> List up to 100 Medicare-certified nursing homes in Harris County, Texas, including CMS number, ownership, star rating, address, and phone.

That maps to `cms_healthcare_provider_search(provider_types=["nursing_home"], state="TX", county="Harris", max_results=100)`. MCP is useful for an analyst's one-off snapshot; a saved Actor task is better for repeatable change detection.

## Cost and interpretation

The Actor charge is $0.02 per returned provider plus a $0.0005 start charge. A complete 250-row snapshot is about $5.0005 in Actor charges; a weekly monitor at that maximum is roughly $20 per four-run month. Narrow by state, county, city, ZIP, name, or provider type to control both cost and review volume. The live Store price is authoritative.

These fields reproduce public CMS data; they are not medical advice or an independent quality judgment. Confirm consequential decisions against the linked official record and its reporting period.

## Next steps

- [Open the CMS Healthcare Provider Search Actor](https://apify.com/captainhandsome/cms-healthcare-provider-search)
- [See all public-record MCP tools](/mcp/public-records/)
- [Install the complete MCP server](/)
