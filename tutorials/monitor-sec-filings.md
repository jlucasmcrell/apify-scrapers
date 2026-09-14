---
layout: default
title: "How to monitor SEC EDGAR filings automatically"
description: "Build a scheduled SEC EDGAR monitor for 10-K, 10-Q, and 8-K filings, deduplicate by accession number, and send each new filing into your workflow."
permalink: /tutorials/monitor-sec-filings/
---
# How to monitor SEC EDGAR filings automatically

This workflow checks a company watchlist for new 10-K annual reports, 10-Q quarterly reports, and 8-K material-event filings. It uses the public [SEC EDGAR Filings Actor](https://apify.com/captainhandsome/sec-edgar-filings-search), so it needs no EDGAR API key and produces flat records that can go directly to a spreadsheet, database, Slack workflow, or research agent.

## Try the finished search first

Open one of these public tasks to see the output without configuring a new workflow:

- [Tesla recent 8-K material-event filings](https://apify.com/captainhandsome/sec-edgar-filings-search/examples/tesla-8k-material-events)
- [Apple and Microsoft recent 10-K filings](https://apify.com/captainhandsome/sec-edgar-filings-search/examples/apple-microsoft-10k-filings)
- [NVIDIA historical annual reports](https://apify.com/captainhandsome/sec-edgar-filings-search/examples/nvidia-historical-annual-reports)

The dataset includes the company, form, filing and report dates, accession number, direct SEC filing URL, primary-document URL, and company metadata. Turn on filing details when you also need 8-K item descriptions, exhibit types, or reporting-owner data.

## Create the watchlist

In the Actor's Input tab, use a bounded input like this:

```json
{
  "companies": ["AAPL", "MSFT", "NVDA"],
  "forms": ["10-K", "10-Q", "8-K"],
  "date_from": "2026-09-01",
  "include_amendments": true,
  "include_filing_details": true,
  "max_items": 100
}
```

Set `date_from` to the beginning of the period you want the first run to cover. On later runs it is safe to use an overlapping window because `accession_number` is a stable filing identifier and makes duplicates easy to remove. `max_items` is a hard output and billing ceiling across the entire company list.

Save the input as an Apify task. In Apify Console, attach that task to a daily schedule and add a run-succeeded webhook if another system should process the resulting dataset immediately.

## Keep only genuinely new filings

Store every previously handled `accession_number`. After each scheduled run:

1. Read the run's default dataset.
2. Discard rows whose `accession_number` is already in your store.
3. Route the remaining rows according to `form`.
4. Save their accession numbers only after the downstream action succeeds.

For 8-K alerts, include `items`, `item_descriptions`, `filing_url`, and `acceptance_datetime` in the message. For annual and quarterly research, the useful fields are `form`, `report_date`, `filing_date`, `primary_document_url`, `sic_description`, and `fiscal_year_end`.

## Run it from Python

```python
import os
from apify_client import ApifyClient

client = ApifyClient(os.environ["APIFY_TOKEN"])
run = client.actor("captainhandsome/sec-edgar-filings-search").call(run_input={
    "companies": ["AAPL", "MSFT", "NVDA"],
    "forms": ["10-K", "10-Q", "8-K"],
    "date_from": "2026-09-01",
    "include_filing_details": True,
    "max_items": 100,
})
filings = list(client.dataset(run["defaultDatasetId"]).iterate_items())
seen_accessions = set()  # Load this from your persistent store on later runs.
new_filings = [row for row in filings if row["accession_number"] not in seen_accessions]
```

Replace the example date each time you create a new monitor. Do not put the Apify token in source control.

## Ask an AI agent through MCP

With [Apify Public Data MCP](/) installed, a one-off check can be as simple as:

> Find Tesla's five latest 8-K filings and return the filing date, accession number, company name, and SEC document URL.

That maps to `sec_edgar_filings(ticker="TSLA", form_type="8-K", max_results=5)`. The scheduled Actor task is the better choice for unattended monitoring; MCP is useful for ad hoc research and summarization.

## Cost and limits

The Actor charge is $0.002 per returned filing plus a $0.0005 start charge. A run capped at 100 results therefore has a maximum Actor charge of about $0.2005, and a run returning only three new or overlapping filings is charged for three results. The live Apify Store price is authoritative.

This is a filing monitor, not a real-time market-data feed. SEC publication timing, amendments, and upstream availability determine when a filing appears.

## Next steps

- [Open the SEC EDGAR Filings Actor](https://apify.com/captainhandsome/sec-edgar-filings-search)
- [See every SEC MCP argument and output field](/mcp/sec-edgar/)
- [Use the ready-made n8n SEC-to-Slack workflow](https://github.com/jlucasmcrell/apify-scrapers/blob/master/workflows/n8n_sec_edgar_to_slack.json)
