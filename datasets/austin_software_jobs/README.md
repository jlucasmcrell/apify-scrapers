---
language:
- en
license: mit
task_categories:
- tabular-classification
- feature-extraction
tags:
- web-scraping
- job-postings
- glassdoor
- labor-market
- career-intelligence
- apify
size_categories:
- n<1K
---

# Austin Software Engineer Job Postings with Normalized Dates

## Overview
This dataset contains clean, structured public data exported directly from production runs of Apify actors.
It serves as a benchmark and sample for lead generation, labor market intelligence, and compliance verification.

- **Source Actor:** [captainhandsome/glassdoor-jobs-scraper](https://apify.com/captainhandsome/glassdoor-jobs-scraper)
- **Preconfigured Run Task:** [captainhandsome/austin-software-engineer-jobs](https://apify.com/captainhandsome/austin-software-engineer-jobs)
- **Records in Sample:** 30
- **Formats Included:** CSV (`austin_software_jobs.csv`) and JSON (`austin_software_jobs.json`)

## Description
Clean structured extract of active software engineering, full stack, and AI developer job listings in the Austin, Texas metro area. Includes canonical job URLs, company names, employer ratings, location tags, salary estimates, raw posting age (e.g. 24h, 3d), and normalized estimated posting dates. Generated via Apify Actor captainhandsome/glassdoor-jobs-scraper.

## Fields
- `job_title`: (e.g. `Entry-level Software Developer`)
- `job_url`: (e.g. `https://www.glassdoor.com/job-listing/entry-level-software-d`)
- `job_id`: (e.g. `1010232358802`)
- `employer`: (e.g. `IXRF Systems`)
- `rating`: (e.g. `None`)
- `location`: (e.g. `Austin, TX`)
- `salary`: (e.g. `$80K (Employer provided)`)
- `posting_age`: (e.g. `24d`)
- `scraped_at`: (e.g. `2026-09-10T20:32:30Z`)
- `posting_date_estimated`: (e.g. `2026-08-17`)
- `posting_date_precision`: (e.g. `estimated`)

## How to Fetch Live or Unlimited Data
To extract thousands of records, schedule recurring daily alerts, or run custom location/industry searches:

1. Visit the production Actor on Apify: **[captainhandsome/glassdoor-jobs-scraper](https://apify.com/captainhandsome/glassdoor-jobs-scraper)**
2. Pass your target query parameters or run the preconfigured task: **[captainhandsome/austin-software-engineer-jobs](https://apify.com/captainhandsome/austin-software-engineer-jobs)**
3. Export results directly into CSV, JSON, Google Sheets, or integrate into your AI workflow via the [apify-scrapers open-source repository](https://github.com/jlucasmcrell/apify-scrapers).

---
*Published by Joseph McRell (@captainhandsome). Open data for research, lead qualification, and software development.*
