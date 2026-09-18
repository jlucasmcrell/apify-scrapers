---
title: "Glassdoor posting dates, explained"
published: true
tags: webscraping, python, jobs, dataengineering
canonical_url: https://apify.revenuesystemslabs.com/articles/glassdoor_posting_dates_guide.html
---

One of the biggest headaches when building automated job aggregators or market compensation trackers is **posting age**.

Job portals like Glassdoor don't expose clean ISO timestamps (`2026-09-10T12:00:00Z`) in the listing feed HTML. Instead, they present relative, human-readable strings like:
- `"24h"`
- `"3d"`
- `"14d"`
- `"30d+"`

If you are dumping these raw strings into Postgres, BigQuery, or Pandas, running temporal queries (e.g. *"Show only jobs posted within the last 7 days"*) becomes messy.

Here is how to cleanly normalize relative posting ages into deterministic ISO dates and precision flags in Python.

---

## The Mathematical Parser

We can parse relative durations using regular expressions and calculate estimated timestamps relative to run execution (`scraped_at`), tagging the calculation with a precision enum (`exact_day`, `estimated`, or `lower_bound`):

```python
import re
from datetime import datetime, timezone, timedelta

def parse_posting_age(age_str: str, reference_time: datetime = None):
    if not reference_time:
        reference_time = datetime.now(timezone.utc)
        
    if not age_str:
        return {
            "posting_age": None,
            "posting_date_estimated": None,
            "posting_date_precision": None
        }

    clean_str = age_str.strip().lower()

    # Matches "24h", "5h", "1h"
    hour_match = re.match(r"^(\d+)\s*h(?:ours?)?$", clean_str)
    if hour_match:
        hours = int(hour_match.group(1))
        est_date = reference_time - timedelta(hours=hours)
        return {
            "posting_age": clean_str,
            "posting_date_estimated": est_date.strftime("%Y-%m-%d"),
            "posting_date_precision": "estimated"
        }

    # Matches "30d+", "60d+" (Lower bound)
    plus_match = re.match(r"^(\d+)\s*d(?:ays?)?\+$", clean_str)
    if plus_match:
        days = int(plus_match.group(1))
        est_date = reference_time - timedelta(days=days)
        return {
            "posting_age": clean_str,
            "posting_date_estimated": est_date.strftime("%Y-%m-%d"),
            "posting_date_precision": "lower_bound"
        }

    # Matches "3d", "7d", "14 days"
    day_match = re.match(r"^(\d+)\s*d(?:ays?)?$", clean_str)
    if day_match:
        days = int(day_match.group(1))
        est_date = reference_time - timedelta(days=days)
        return {
            "posting_age": clean_str,
            "posting_date_estimated": est_date.strftime("%Y-%m-%d"),
            "posting_date_precision": "estimated"
        }

    # Fallback for unexpected formats
    return {
        "posting_age": clean_str,
        "posting_date_estimated": None,
        "posting_date_precision": "unknown"
    }
```

---

## Canonical Link Extraction

Glassdoor URLs from search grids are loaded with dynamic tracking telemetry, session IDs, and redirection wrappers:

```text
https://www.glassdoor.com/partner/jobListing.htm?pos=101&ao=1136043&s=58&guid=00000191...&jobListingId=100987654321
```

To prevent database duplicates, extract the pure numeric `job_id` and construct a clean canonical permalink:

```python
from urllib.parse import urlparse, parse_qs

def canonicalize_glassdoor_url(raw_url: str):
    parsed = urlparse(raw_url)
    qs = parse_qs(parsed.query)
    
    # Try finding the jobListingId or jl parameter
    job_id = qs.get("jobListingId", [None])[0] or qs.get("jl", [None])[0]
    
    if not job_id:
        # Regex search for digits in path
        id_match = re.search(r"-jl_(\d+)\.htm", raw_url) or re.search(r"/(\d{8,12})\.htm", raw_url)
        if id_match:
            job_id = id_match.group(1)

    if job_id:
        canonical_url = f"https://www.glassdoor.com/job-listing/-jl_{job_id}.htm"
        return job_id, canonical_url

    return None, raw_url
```

---

## Production Cloud Endpoint

If you need this pipeline running with zero server maintenance, rotating proxies, and automated retries, we run this continuous enrichment pipeline on Apify:

- **Actor:** [captainhandsome/glassdoor-jobs-scraper](https://apify.com/captainhandsome/glassdoor-jobs-scraper)
- **GitHub Repository:** [jlucasmcrell/apify-scrapers](https://github.com/jlucasmcrell/apify-scrapers)

```python
from apify_client import ApifyClient

client = ApifyClient("YOUR_APIFY_TOKEN")
run = client.actor("captainhandsome/glassdoor-jobs-scraper").call(run_input={
    "keyword": "Software Engineer",
    "location": "Austin, TX",
    "max_items": 30
})

jobs = list(client.dataset(run["defaultDatasetId"]).iterate_items())
for job in jobs[:3]:
    print(job["job_title"], "|", job["employer"], "|", job["posting_date_estimated"], f"({job['posting_age']})")
```
