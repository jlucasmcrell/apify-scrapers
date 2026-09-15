---
layout: default
title: "MCP server for SEC EDGAR filings"
description: "An MCP server for SEC EDGAR filings that lets an AI agent pull 10-K, 10-Q, and 8-K filings straight from SEC.gov, billed to your own Apify account."
permalink: /mcp/sec-edgar/
---
# MCP server for SEC EDGAR filings

This is an MCP server for SEC EDGAR filings: it exposes the `sec_edgar_filings` and `sec_form_4_insider_transactions` tools so an AI agent can retrieve periodic filings and structured insider transactions directly from the SEC's own EDGAR system. Every tool, including these, runs as an Apify Actor on your own Apify account. This page is one of several use-case pages built on [Apify Public Data MCP](/), which exposes 30 tools in total.

Want alerts instead of one-off lookups? Follow the [SEC filing-monitor tutorial](/tutorials/monitor-sec-filings/) to create a scheduled, deduplicated workflow.

## What an agent can ask

- Pull Tesla's latest annual report -> sec_edgar_filings(ticker="TSLA", form_type="10-K", max_results=1)
- What has NVIDIA filed with the SEC in the last few quarters? -> sec_edgar_filings(ticker="NVDA", form_type="10-Q", max_results=5)
- Show me the five most recent material event filings for Apple -> sec_edgar_filings(ticker="AAPL", form_type="8-K", max_results=5)
- Get every filing type on record for Boeing -> sec_edgar_filings(ticker="Boeing", form_type="ALL", max_results=10)
- Does Siemens hold an active Legal Entity Identifier? -> gleif_lei_search(query="Siemens", search_mode="name", status="ACTIVE")
- What federal contracts has Lockheed Martin been awarded? -> usaspending_contracts(recipient_name="Lockheed Martin", max_results=10)

## Tools

### sec_edgar_filings - SEC EDGAR Public Corporate Filings Retrieval

Retrieves official United States Securities and Exchange Commission filings, including 10-K annual reports, 10-Q quarterly reports, and 8-K material events, by company ticker or name. It is a read-only query against public federal securities disclosures, so it works for pulling audited financial statements, executive compensation disclosures, and regulatory event filings, but it does not surface anything the SEC itself hasn't published. Each result also carries the filing company's CIK and the filing's accession number, so an agent can cite the exact SEC document rather than paraphrasing a summary.

| Argument | Required | What it does |
|---|---|---|
| ticker | Yes | Public stock ticker symbol or official company name (e.g. 'AAPL', 'NVDA', or 'Tesla Inc'). |
| form_type | No | SEC form classification: '10-K' for annual reports, '10-Q' for quarterly reports, '8-K' for material events, or 'ALL' for any filing. default: 10-K |
| max_results | No | Maximum count of chronological filing records to retrieve. default: 5 |

Returns: cik, company_name, tickers, exchanges, sic, sic_description, state_of_incorporation, fiscal_year_end, form, is_amendment, filing_date, report_date, acceptance_datetime, accession_number, act, file_number, film_number, items, size_bytes, is_xbrl, is_inline_xbrl, primary_document, primary_document_description, filing_url, primary_document_url, company_submissions_url, ticker, exchange, entity_type, filer_category, owner_org, ein, phone, state_of_incorporation_description, business_address, business_address_street1, business_address_street2, business_address_city, business_address_state, business_address_state_description, business_address_zip, business_address_country, business_address_is_foreign, mailing_address, mailing_address_street1, mailing_address_street2, mailing_address_city, mailing_address_state, mailing_address_zip, mailing_address_country, former_names, current_name_since, has_insider_transactions_as_owner, has_insider_transactions_as_issuer, filing_directory_url, filing_txt_url, company_filings_url, document_count, document_types, exhibit_count, item_descriptions, filer_names, filer_ciks, reporting_owner_names, reporting_owner_ciks, issuer_name, issuer_cik, subject_company_name, subject_company_cik, group_members, filing_date_changed

Price: $0.002 per result plus $0.0005 Actor-start per run (free-tier price; 10-30% lower on paid Apify plans)

Store listing: [SEC EDGAR Filings Scraper & Search API - 10-K, 10-Q, 8-K](https://apify.com/captainhandsome/sec-edgar-filings-search)

Not for: private non-public company intelligence, real-time stock prices, or local trade vendor lists.

## Pairs well with

An agent researching a company rarely stops at its SEC filings. These tools cover related angles: global entity identity, state-level registration, and public money trails.

- gleif_lei_search - adds the company's global Legal Entity Identifier, registration status, and jurisdiction for counterparty checks - [Store](https://apify.com/captainhandsome/gleif-lei-search)
- us_business_entity_search - adds state-level Secretary of State registry records when the entity isn't SEC-registered - [Store](https://apify.com/captainhandsome/us-business-entity-search)
- usaspending_contracts - adds federal procurement contract awards tied to the same company - [Store](https://apify.com/captainhandsome/usaspending-federal-awards)
- fec_campaign_finance_search - adds political campaign finance and donor records for related executives or committees - [Store](https://apify.com/captainhandsome/fec-campaign-finance-search)

## Install the MCP server

The server is a Python stdio MCP server published on PyPI as `apify-data-scrapers`. Every tool runs an Apify Actor on **your own** Apify account, so you need a free Apify account and its API token (Apify Console -> Settings -> Integrations).

**Claude Desktop / Claude Code** - add to `claude_desktop_config.json` (or `.mcp.json`):

```json
{
  "mcpServers": {
    "apify-scrapers": {
      "command": "uvx",
      "args": ["apify-data-scrapers"],
      "env": { "APIFY_TOKEN": "YOUR_APIFY_API_TOKEN" }
    }
  }
}
```

**Cursor** - Settings -> MCP -> Add server, same command (`uvx apify-data-scrapers`) and the `APIFY_TOKEN` environment variable.

**Smithery** - one-click install from [smithery.ai/servers/jlucasmcrell/apify-scrapers](https://smithery.ai/servers/jlucasmcrell/apify-scrapers).

**Without an MCP client** - the same Actors are callable from Python (`apify-client`), Node.js, n8n, Make or the Apify Console; see the [project README](/).

## Other use-case pages

- [/mcp/google-maps/](/mcp/google-maps/)
- [/mcp/public-records/](/mcp/public-records/)
- [/mcp/job-search/](/mcp/job-search/)
- [/mcp/government-data/](/mcp/government-data/)
- [/](/)

## FAQ

**Does this need an API key?**
Yes. Every tool, including `sec_edgar_filings`, requires the `APIFY_TOKEN` environment variable, and each call runs as an Apify Actor on your own account, so usage bills you directly rather than a shared service. There is no separate SEC API key to request; the Actor reads EDGAR's own public data.

**How fast is a typical run?**
Typical run duration for `sec_edgar_filings` is 10-30 seconds, with a timeout capped at 120 seconds. A lower `max_results` generally finishes toward the fast end of that range.

**What isn't in this data?**
`sec_edgar_filings` is not for private non-public company intelligence, real-time stock prices, or local trade vendor lists. For federal contract awards use `usaspending_contracts`; for local business leads use `google_maps_search`; for hiring data use `glassdoor_jobs_search`.

**How are results returned?**
Each matching filing comes back as a JSON record with fields including formType, filingDate, accessionNumber, companyName, cik, and documentUrl, ready for an agent to read directly or pass along in a summary.
