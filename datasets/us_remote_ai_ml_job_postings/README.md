---
license: mit
task_categories:
  - other
tags:
  - jobs
  - recruitment
  - labor-market
  - ai-engineers
  - apify
size_categories:
  - n<1K
---

# US Remote AI & Machine Learning Job Postings

## Overview
This dataset contains clean, structured public data exported directly from production runs of Apify actors.
It serves as a benchmark and sample for lead qualification, market intelligence, research, and machine learning pipelines.

- **Source Actor:** [captainhandsome/linkedin-public-jobs-search](https://apify.com/captainhandsome/linkedin-public-jobs-search)
- **Preconfigured Run Task:** [captainhandsome/sf-ai-engineer-openings](https://apify.com/captainhandsome/sf-ai-engineer-openings)
- **Records in Sample:** 10
- **Formats Included:** CSV (`us_remote_ai_ml_job_postings.csv`) and JSON (`us_remote_ai_ml_job_postings.json`)

## Description
Fresh job listings for AI, ML, and Software Engineering positions across the United States. Includes canonical job posting URLs, hiring company names, job titles, locations, raw posting age, and estimated posting dates. Generated via Apify Actor captainhandsome/linkedin-public-jobs-search.

## Fields
- `title`: (e.g. `AI Engineer`)
- `company`: (e.g. `P-1 AI`)
- `location`: (e.g. `San Francisco Bay Area`)
- `url`: (e.g. `https://www.linkedin.com/jobs/view/ai-engineer-at-p-1-ai-443`)
- `posted_at`: (e.g. `2026-09-08`)


## How to Fetch Live or Unlimited Data
To extract thousands of records, schedule recurring daily alerts, or run custom queries:

1. Visit the production Actor on Apify: **[captainhandsome/linkedin-public-jobs-search](https://apify.com/captainhandsome/linkedin-public-jobs-search)**
2. Pass your target query parameters or run the preconfigured task: **[captainhandsome/sf-ai-engineer-openings](https://apify.com/captainhandsome/sf-ai-engineer-openings)**
3. Export results directly into CSV, JSON, Google Sheets, or integrate into your AI workflow via the [apify-scrapers open-source repository](https://github.com/jlucasmcrell/apify-scrapers).

---
*Published by Joseph McRell (@captainhandsome). Open data for research, lead qualification, and software development.*
