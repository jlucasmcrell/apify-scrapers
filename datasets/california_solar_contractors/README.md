---
language:
- en
license: mit
task_categories:
- tabular-classification
- feature-extraction
tags:
- web-scraping
- contractor-licenses
- compliance
- california
- public-records
- apify
size_categories:
- n<1K
---

# California State Licensed Contractors Sample Registry

## Overview
This dataset contains clean, structured public data exported directly from production runs of Apify actors.
It serves as a benchmark and sample for lead generation, labor market intelligence, and compliance verification.

- **Source Actor:** [captainhandsome/ca-contractor-license-search](https://apify.com/captainhandsome/ca-contractor-license-search)
- **Dataset Page:** [Public sample and schema](https://apify.revenuesystemslabs.com/datasets/california_solar_contractors/README.html)
- **Preconfigured Run Task:** [captainhandsome/california-contractor-smith](https://apify.com/captainhandsome/california-contractor-smith)
- **Records in Sample:** 50
- **Formats Included:** CSV (`california_licensed_contractors.csv`) and JSON (`california_licensed_contractors.json`)

## Description
Public registry extract of verified California licensed specialty and general building contractors from the California Contractors State License Board (CSLB). Includes business names, license numbers, current license status, issue dates, expiration dates, and classifications. Generated via Apify Actor captainhandsome/ca-contractor-license-search.

## Fields
- `contractor_name`: (e.g. `smith jay r`)
- `name_type`: (e.g. `previous`)
- `license_number`: (e.g. `1018539`)
- `city`: (e.g. `berkeley`)
- `status`: (e.g. `active`)

## How to Fetch Live or Unlimited Data
To extract thousands of records, schedule recurring daily alerts, or run custom location/industry searches:

1. Visit the production Actor on Apify: **[captainhandsome/ca-contractor-license-search](https://apify.com/captainhandsome/ca-contractor-license-search)**
2. Pass your target query parameters or run the preconfigured task: **[captainhandsome/california-contractor-smith](https://apify.com/captainhandsome/california-contractor-smith)**
3. Export results directly into CSV, JSON, Google Sheets, or integrate into your AI workflow via the [apify-scrapers open-source repository](https://github.com/jlucasmcrell/apify-scrapers).

---
*Published by Joseph McRell (@captainhandsome). Open data for research, lead qualification, and software development.*
