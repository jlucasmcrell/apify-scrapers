---
license: mit
task_categories:
  - other
tags:
  - nlp
  - sentiment-analysis
  - reviews
  - google-play
  - apify
size_categories:
  - n<1K
---

# Top Mobile Apps User Sentiment & Review Corpus (Google Play)

## Overview
This dataset contains clean, structured public data exported directly from production runs of Apify actors.
It serves as a benchmark and sample for lead qualification, market intelligence, research, and machine learning pipelines.

- **Source Actor:** [captainhandsome/google-play-reviews-scraper](https://apify.com/captainhandsome/google-play-reviews-scraper)
- **Preconfigured Run Task:** [captainhandsome/instagram-1star-reviews](https://apify.com/captainhandsome/instagram-1star-reviews)
- **Records in Sample:** 10
- **Formats Included:** CSV (`mobile_apps_user_sentiment_reviews.csv`) and JSON (`mobile_apps_user_sentiment_reviews.json`)

## Description
Structured user review and sentiment corpus extracted from the Google Play Store. Includes app package IDs, reviewer ratings (1-5 stars), review text, user thumbs-up vote counts, review submission timestamps, and developer responses. Generated via Apify Actor captainhandsome/google-play-reviews-scraper.

## Fields
- `app_id`: (e.g. `com.google.android.youtube`)
- `review_id`: (e.g. `c0338d5d-4dd2-4288-ba3d-f146055e4a99`)
- `user_name`: (e.g. `mohd Arif Arif`)
- `user_image`: (e.g. `https://play-lh.googleusercontent.com/a-/ALV-UjVmJt0B1fYAwZz`)
- `text`: (e.g. `very good 👍 👏 standing 🧍‍♂️ 👏`)
- `score`: (e.g. `5`)
- `thumbs_up`: (e.g. `0`)
- `review_version`: (e.g. `21.34.245`)
- `app_version`: (e.g. `21.34.245`)
- `reviewed_at`: (e.g. `2026-09-09T20:49:53`)


## How to Fetch Live or Unlimited Data
To extract thousands of records, schedule recurring daily alerts, or run custom queries:

1. Visit the production Actor on Apify: **[captainhandsome/google-play-reviews-scraper](https://apify.com/captainhandsome/google-play-reviews-scraper)**
2. Pass your target query parameters or run the preconfigured task: **[captainhandsome/instagram-1star-reviews](https://apify.com/captainhandsome/instagram-1star-reviews)**
3. Export results directly into CSV, JSON, Google Sheets, or integrate into your AI workflow via the [apify-scrapers open-source repository](https://github.com/jlucasmcrell/apify-scrapers).

---
*Published by Joseph McRell (@captainhandsome). Open data for research, lead qualification, and software development.*
