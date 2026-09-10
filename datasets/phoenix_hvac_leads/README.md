---
language:
- en
license: mit
task_categories:
- tabular-classification
- feature-extraction
tags:
- web-scraping
- b2b-leads
- business-data
- apify
- local-business
- google-maps
size_categories:
- n<1K
---

# Phoenix HVAC Contractor & Local Business Leads (2026)

## Overview
This dataset contains clean, structured public data exported directly from production runs of Apify actors.
It serves as a benchmark and sample for lead generation, labor market intelligence, and compliance verification.

- **Source Actor:** [captainhandsome/google-maps-business-search](https://apify.com/captainhandsome/google-maps-business-search)
- **Preconfigured Run Task:** [captainhandsome/phoenix-hvac-company-leads](https://apify.com/captainhandsome/phoenix-hvac-company-leads)
- **Records in Sample:** 10
- **Formats Included:** CSV (`phoenix_hvac_leads.csv`) and JSON (`phoenix_hvac_leads.json`)

## Description
Real verified extract of HVAC repair, installation, and commercial contractor businesses across Phoenix, Arizona including business names, phone numbers, full addresses, ratings, review counts, Google Maps URLs, and website domains. Generated via Apify Actor captainhandsome/google-maps-business-search.

## Fields
- `name`: (e.g. `Ken Muncy Air Conditioning`)
- `place_url`: (e.g. `https://www.google.com/maps/place/Ken+Muncy+Air+Conditioning`)
- `place_id`: (e.g. `0x872baecd59e7ddcb:0x27e4782f03fde181`)
- `category`: (e.g. `Air conditioning contractor`)
- `address`: (e.g. `450 E Warner Rd Ste 6, Chandler, AZ 85225`)
- `phone`: (e.g. `(480) 210-9071`)
- `phone_unformatted`: (e.g. `+14802109071`)
- `website`: (e.g. `https://www.kenmuncy.com/`)
- `rating`: (e.g. `5`)
- `reviews_count`: (e.g. `317`)
- `opening_hours_today`: (e.g. `Thursday, 7 AM5 PM`)
- `plus_code`: (e.g. `85P8+J7 Chandler, Arizona`)
- `latitude`: (e.g. `33.336571`)
- `longitude`: (e.g. `-111.834342`)

## How to Fetch Live or Unlimited Data
To extract thousands of records, schedule recurring daily alerts, or run custom location/industry searches:

1. Visit the production Actor on Apify: **[captainhandsome/google-maps-business-search](https://apify.com/captainhandsome/google-maps-business-search)**
2. Pass your target query parameters or run the preconfigured task: **[captainhandsome/phoenix-hvac-company-leads](https://apify.com/captainhandsome/phoenix-hvac-company-leads)**
3. Export results directly into CSV, JSON, Google Sheets, or integrate into your AI workflow via the [apify-scrapers open-source repository](https://github.com/jlucasmcrell/apify-scrapers).

---
*Published by Joseph McRell (@captainhandsome). Open data for research, lead qualification, and software development.*
