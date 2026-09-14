---
layout: default
title: "How to build a contractor lead list from Google Maps"
description: "Build a qualified local contractor lead list with Google Maps phone, website, rating, category, and address data, then verify selected licences."
permalink: /tutorials/contractor-lead-generation/
---
# How to build a contractor lead list from Google Maps

This workflow turns a trade and territory into a clean contractor prospect list. The [Google Maps Business Leads Actor](https://apify.com/captainhandsome/google-maps-business-search) returns business names, phone numbers, websites, ratings, review counts, categories, addresses, hours, place IDs, and coordinates. A second public Actor can verify selected California and Oregon contractors against their state licence boards.

## Try a ready-made lead search

- [HVAC company leads in Phoenix](https://apify.com/captainhandsome/google-maps-business-search/examples/phoenix-hvac-company-leads)
- [Commercial electricians in Dallas](https://apify.com/captainhandsome/google-maps-business-search/examples/dallas-commercial-electrician-leads)
- [Chicago dentist directory](https://apify.com/captainhandsome/google-maps-business-search/examples/chicago-dentist-directory)

Each task opens with working input and exports to JSON, CSV, Excel, XML, or RSS from the Dataset tab.

## Build a qualified list

Start with one service category and one market. Narrow inputs produce a list that is easier to evaluate and less likely to mix unrelated trades.

```json
{
  "search_query": "roofing contractors",
  "location": "Austin, Texas",
  "max_items": 100,
  "include_details": true,
  "min_rating": 4.2,
  "require_website": true,
  "exclude_closed": true,
  "category_exact": ["Roofing contractor"]
}
```

The filters are applied before the result count, so filtered-out rows are not billed. Use `category_exact` only after checking Google's displayed category for the trade; an overly narrow category can exclude good prospects. For broader prospecting, omit it and filter the exported CSV yourself.

## Turn results into sales-ready rows

Use `place_id` as the primary deduplication key and `place_url` as the fallback. Keep these fields in the first-pass export:

- `name`, `category`, `phone`, `phone_unformatted`, and `website`
- `address`, `city`, `state`, `postal_code`, `latitude`, and `longitude`
- `rating`, `reviews_count`, `open_state`, and `opening_hours`
- `place_id`, `place_url`, and `search_url` for traceability

A practical qualification score can reward a working website, a public phone number, a rating above your threshold, and enough reviews to make the rating meaningful. Keep missing data as missing rather than treating it as a negative fact.

## Verify licences for selected leads

Google Maps is a business directory, not a licensing authority. For California or Oregon, send the best prospects by business name to the [US Contractor License Search Actor](https://apify.com/captainhandsome/us-contractor-license-search):

```json
{
  "search_query": "Example Roofing",
  "states": ["california"],
  "max_items": 10,
  "include_details": true
}
```

Review `source`, `business_name`, `license_number`, `status`, and `city`. With details enabled, you can also inspect classifications, bonding, insurance, workers' compensation, disciplinary history, and issue or expiry dates when the board publishes them. Match names and cities deliberately; a similar name is not proof that two records describe the same company.

## Run the discovery step from Python

```python
import os
from apify_client import ApifyClient

client = ApifyClient(os.environ["APIFY_TOKEN"])
run = client.actor("captainhandsome/google-maps-business-search").call(run_input={
    "search_query": "roofing contractors",
    "location": "Austin, Texas",
    "max_items": 100,
    "include_details": True,
    "min_rating": 4.2,
    "require_website": True,
    "exclude_closed": True,
})
leads = list(client.dataset(run["defaultDatasetId"]).iterate_items())
```

## Ask an AI agent through MCP

With [Apify Public Data MCP](/) installed:

> Find 25 commercial electricians in Dallas with phone numbers, websites, addresses, ratings, and Google Maps URLs. Return a CSV-ready table.

The agent calls `google_maps_search(search_query="commercial electricians in Dallas, TX", max_results=25)`. Follow with `us_contractor_license_search` for individual names that need licence verification.

## Cost and responsible use

The Google Maps Actor charge is $0.0025 per returned business plus a $0.001 start charge. A 100-result run is therefore capped at about $0.251 in Actor charges. The multi-state licence Actor is $0.003 per returned licence record plus $0.0005 per start. Live Store prices are authoritative.

Public contact data is not blanket permission for unsolicited outreach. Apply the laws and platform rules relevant to your location, channel, and audience, and give recipients a clear way to opt out.

## Next steps

- [Open the Google Maps Business Leads Actor](https://apify.com/captainhandsome/google-maps-business-search)
- [See the Google Maps MCP tool contract](/mcp/google-maps/)
- [See public-record and contractor-licence tools](/mcp/public-records/)
- [Use the ready-made n8n Google-Maps-to-Sheets workflow](https://github.com/jlucasmcrell/apify-scrapers/blob/master/workflows/n8n_google_maps_to_sheets.json)
