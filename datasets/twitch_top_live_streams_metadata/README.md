---
license: mit
task_categories:
  - other
tags:
  - gaming
  - streaming
  - twitch
  - viewership
  - apify
size_categories:
  - n<1K
---

# Top Twitch Channels Live Viewership & Broadcast Metadata

## Overview
This dataset contains clean, structured public data exported directly from production runs of Apify actors.
It serves as a benchmark and sample for lead qualification, market intelligence, research, and machine learning pipelines.

- **Source Actor:** [captainhandsome/twitch-live-streams-scraper](https://apify.com/captainhandsome/twitch-live-streams-scraper)
- **Dataset Page:** [Public sample and schema](https://apify.revenuesystemslabs.com/datasets/twitch_top_live_streams_metadata/README.html)
- **Preconfigured Run Task:** [captainhandsome/twitch-live-fortnite-streams](https://apify.com/captainhandsome/twitch-live-fortnite-streams)
- **Records in Sample:** 10
- **Formats Included:** CSV (`twitch_top_live_streams_metadata.csv`) and JSON (`twitch_top_live_streams_metadata.json`)

## Description
Real-time snapshot of top live streaming channels on Twitch. Includes channel display names, game/category names, stream titles, concurrent viewer counts, broadcaster languages, stream start timestamps, and thumbnail URLs. Generated via Apify Actor captainhandsome/twitch-live-streams-scraper.

## Fields
- `stream_label`: (e.g. `1 million subscriber celebration 🎉 - happyhappygal`)
- `channel_url`: (e.g. `https://www.twitch.tv/happyhappygal`)
- `channel_name`: (e.g. `happyhappygal`)
- `viewer_count`: (e.g. `6.4k viewers`)
- `thumbnail_url`: (e.g. `https://static-cdn.jtvnw.net/previews-ttv/live_user_happyhap`)
- `live_status`: (e.g. `live`)


## How to Fetch Live or Unlimited Data
To extract thousands of records, schedule recurring daily alerts, or run custom queries:

1. Visit the production Actor on Apify: **[captainhandsome/twitch-live-streams-scraper](https://apify.com/captainhandsome/twitch-live-streams-scraper)**
2. Pass your target query parameters or run the preconfigured task: **[captainhandsome/twitch-live-fortnite-streams](https://apify.com/captainhandsome/twitch-live-fortnite-streams)**
3. Export results directly into CSV, JSON, Google Sheets, or integrate into your AI workflow via the [apify-scrapers open-source repository](https://github.com/jlucasmcrell/apify-scrapers).

---
*Published by Joseph McRell (@captainhandsome). Open data for research, lead qualification, and software development.*
