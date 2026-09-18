---
license: mit
task_categories:
  - other
tags:
  - finance
  - sec-edgar
  - corporate-filings
  - b2b
  - apify
size_categories:
  - n<1K
---

# S&P 500 Corporate Filings (SEC EDGAR 10-K & 8-K Archive)

## Overview
This dataset contains clean, structured public data exported directly from production runs of Apify actors.
It serves as a benchmark and sample for lead qualification, market intelligence, research, and machine learning pipelines.

- **Source Actor:** [captainhandsome/sec-edgar-filings-search](https://apify.com/captainhandsome/sec-edgar-filings-search)
- **Dataset Page:** [Public sample and schema](https://apify.revenuesystemslabs.com/datasets/sp500_sec_edgar_filings/README.html)
- **Preconfigured Run Task:** [captainhandsome/apple-microsoft-10k-filings](https://apify.com/captainhandsome/apple-microsoft-10k-filings)
- **Records in Sample:** 5
- **Formats Included:** CSV (`sp500_sec_edgar_filings.csv`) and JSON (`sp500_sec_edgar_filings.json`)

## Description
Real verified extract of corporate annual (10-K) and quarterly/material filings from the SEC EDGAR system. Includes company names, CIK numbers, tickers, form types, filing dates, accession numbers, and direct SEC EDGAR URLs. Generated via Apify Actor captainhandsome/sec-edgar-filings-search.

## Fields
- `cik`: (e.g. `0000789019`)
- `company_name`: (e.g. `MICROSOFT CORP`)
- `ticker`: (e.g. `MSFT`)
- `tickers`: (e.g. `['MSFT']`)
- `exchanges`: (e.g. `['Nasdaq']`)
- `sic`: (e.g. `7372`)
- `sic_description`: (e.g. `Services-Prepackaged Software`)
- `state_of_incorporation`: (e.g. `WA`)
- `fiscal_year_end`: (e.g. `0630`)
- `form`: (e.g. `10-K`)


## How to Fetch Live or Unlimited Data
To extract thousands of records, schedule recurring daily alerts, or run custom queries:

1. Visit the production Actor on Apify: **[captainhandsome/sec-edgar-filings-search](https://apify.com/captainhandsome/sec-edgar-filings-search)**
2. Pass your target query parameters or run the preconfigured task: **[captainhandsome/apple-microsoft-10k-filings](https://apify.com/captainhandsome/apple-microsoft-10k-filings)**
3. Export results directly into CSV, JSON, Google Sheets, or integrate into your AI workflow via the [apify-scrapers open-source repository](https://github.com/jlucasmcrell/apify-scrapers).

---
*Published by Joseph McRell (@captainhandsome). Open data for research, lead qualification, and software development.*
