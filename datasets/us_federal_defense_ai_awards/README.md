---
license: mit
task_categories:
  - other
tags:
  - procurement
  - defense
  - government
  - usaspending
  - apify
size_categories:
  - n<1K
---

# US Federal Defense & AI Contract Awards (USAspending)

## Overview
This dataset contains clean, structured public data exported directly from production runs of Apify actors.
It serves as a benchmark and sample for lead qualification, market intelligence, research, and machine learning pipelines.

- **Source Actor:** [captainhandsome/usaspending-federal-awards](https://apify.com/captainhandsome/usaspending-federal-awards)
- **Dataset Page:** [Public sample and schema](https://apify.revenuesystemslabs.com/datasets/us_federal_defense_ai_awards/README.html)
- **Preconfigured Run Task:** [captainhandsome/defense-prime-contracts](https://apify.com/captainhandsome/defense-prime-contracts)
- **Records in Sample:** 10
- **Formats Included:** CSV (`us_federal_defense_ai_awards.csv`) and JSON (`us_federal_defense_ai_awards.json`)

## Description
Public procurement dataset of prime federal awards, defense contracts, and AI grant obligations from USAspending.gov. Includes recipient names, awarding agencies, funding offices, award amounts, action dates, and award descriptions. Generated via Apify Actor captainhandsome/usaspending-federal-awards.

## Fields
- `award_family`: (e.g. `contracts`)
- `award_id`: (e.g. `DEAC0494AL85000`)
- `recipient_name`: (e.g. `LOCKHEED MARTIN CORP`)
- `award_type`: (e.g. `DEFINITIVE CONTRACT`)
- `amount`: (e.g. `48063737196.35`)
- `total_outlays`: (e.g. `-4166130.71`)
- `subsidy_cost`: (e.g. `None`)
- `awarding_agency`: (e.g. `Department of Energy`)
- `awarding_sub_agency`: (e.g. `Department of Energy`)
- `start_date`: (e.g. `1993-10-15`)


## How to Fetch Live or Unlimited Data
To extract thousands of records, schedule recurring daily alerts, or run custom queries:

1. Visit the production Actor on Apify: **[captainhandsome/usaspending-federal-awards](https://apify.com/captainhandsome/usaspending-federal-awards)**
2. Pass your target query parameters or run the preconfigured task: **[captainhandsome/defense-prime-contracts](https://apify.com/captainhandsome/defense-prime-contracts)**
3. Export results directly into CSV, JSON, Google Sheets, or integrate into your AI workflow via the [apify-scrapers open-source repository](https://github.com/jlucasmcrell/apify-scrapers).

---
*Published by Joseph McRell (@captainhandsome). Open data for research, lead qualification, and software development.*
