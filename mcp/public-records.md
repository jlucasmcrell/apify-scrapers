---
layout: default
title: "MCP server for public records: business registries, licences and providers"
description: "An MCP server that lets AI agents pull US and French business registries, contractor licenses, LEI records, and Medicare provider data as Apify Actors."
permalink: /mcp/public-records/
---
# MCP server for public records: business registries, licences and providers

This MCP server for public records gives an AI agent these tools: `us_business_entity_search`, `alabama_business_search`, `florida_new_filings_search`, `florida_officer_search`, `california_contractor_license_search`, `us_contractor_license_search`, `gleif_lei_search`, `french_company_search`, and `cms_healthcare_provider_search`. Each runs as an Apify Actor on the reader's own account, so a free plan works. These are part of [Apify Public Data MCP](/), which exposes 25 tools in total.

## What an agent can ask

- "Is Acme LLC registered in Florida?" -> florida_new_filings_search(search_query="Acme LLC")
- "Which Florida companies list Jane Doe as an officer?" -> florida_officer_search(search_query="Doe")
- "Is Acme a licensed California contractor?" -> california_contractor_license_search(search_query="Acme")
- "Look up the LEI for Siemens." -> gleif_lei_search(query="Siemens")
- "List Medicare-certified hospitals in Houston." -> cms_healthcare_provider_search(state="TX", city="Houston")

## Tools

### us_business_entity_search - US Multi-State Business Entity Search

Searches Florida, Alabama, Iowa, and Wisconsin registries in one call.

| Argument | Required | What it does |
|---|---|---|
| search_query | Yes | Business name to search. |
| states | No | States to search; default: florida, alabama, iowa, wisconsin. |
| max_results | No | Records to bill; default: 10. |
| include_details | No | Adds formation date, agent; default: false. |

Returns: source, entity_name, status, entity_type, location, registered_agent

Price: $0.0025 per result plus $0.0005 Actor-start per run (free-tier price; 10-30% lower on paid Apify plans)

Store listing: [Apify Store](https://apify.com/captainhandsome/us-business-entity-search)

Not for: single-state or officer search.

### alabama_business_search - Alabama Business Entity Registry Search

Searches Alabama business-entity records by name.

| Argument | Required | What it does |
|---|---|---|
| search_query | Yes | Alabama business name. |
| max_results | No | Records to bill; default: 10. |
| include_details | No | Adds formation date, agent; default: false. |

Returns: entity_id, entity_name, entity_type, status, location, registered_agent

Price: $0.0025 per result plus $0.0005 Actor-start per run (free-tier price; 10-30% lower on paid Apify plans)

Store listing: [Apify Store](https://apify.com/captainhandsome/al-business-entity-search)

Not for: other states or officer search.

### florida_new_filings_search - Florida Sunbiz Business Entity Search

Searches Florida Sunbiz by company name.

| Argument | Required | What it does |
|---|---|---|
| search_query | Yes | Florida business name. |
| max_results | No | Records to bill; default: 10. |
| include_details | No | Adds date filed, EIN, agent; default: false. |

Returns: entity_name, document_number, status, entity_type, date_filed, registered_agent

Price: $0.003 per result plus $0.001 Actor-start per run (free-tier price; 10-30% lower on paid Apify plans)

Store listing: [Apify Store](https://apify.com/captainhandsome/fl-sos-new-filings)

Not for: officer search or other states.

### florida_officer_search - Florida Sunbiz Officer and Registered Agent Search

Searches Florida Sunbiz by officer or agent name.

| Argument | Required | What it does |
|---|---|---|
| search_query | Yes | Officer or agent name. |
| max_results | No | Records to bill; default: 10. |
| include_details | No | Adds status, filing date; default: false. |

Returns: officer_name, entity_name, document_number, detail_url, entity_type, status

Price: $0.003 per result plus $0.001 Actor-start per run (free-tier price; 10-30% lower on paid Apify plans)

Store listing: [Apify Store](https://apify.com/captainhandsome/fl-sunbiz-officer-search)

Not for: company-name search or other states.

### california_contractor_license_search - California CSLB Contractor License Search

Searches California CSLB records by name.

| Argument | Required | What it does |
|---|---|---|
| search_query | Yes | Contractor or business name. |
| max_results | No | Records to bill; default: 10. |
| include_details | No | Adds dates, classifications; default: false. |

Returns: contractor_name, license_number, city, status, business_entity, issue_date

Price: $0.003 per result plus $0.0005 Actor-start per run (free-tier price; 10-30% lower on paid Apify plans)

Store listing: [Apify Store](https://apify.com/captainhandsome/ca-contractor-license-search)

Not for: Oregon or non-contractor trades.

### us_contractor_license_search - US Multi-State Contractor License Search

Searches CA CSLB and OR CCB records in one call.

| Argument | Required | What it does |
|---|---|---|
| search_query | Yes | Business or person name. |
| states | No | States to search; default: california, oregon. |
| max_results | No | Records to bill; default: 10. |
| include_details | No | Adds bonding, insurance; default: false. |

Returns: source, business_name, contractor_name, license_number, status, city

Price: $0.003 per result plus $0.0005 Actor-start per run (free-tier price; 10-30% lower on paid Apify plans)

Store listing: [Apify Store](https://apify.com/captainhandsome/us-contractor-license-search)

Not for: single-state or entity registries.

### gleif_lei_search - GLEIF Legal Entity Identifier Search

Searches GLEIF for Legal Entity Identifiers.

| Argument | Required | What it does |
|---|---|---|
| query | Yes | Name, LEI, or free text. |
| search_mode | No | name/fulltext/lei; default: name. |
| country | No | ISO country filter. |
| jurisdiction | No | Jurisdiction code filter. |
| status | No | Operating status filter. |
| include_relationships | No | Adds parent/subsidiary data; default: false. |
| max_results | No | Records to retrieve; default: 10. |

Returns: lei, legal_name, status, jurisdiction, legal_form_name, registered_as

Price: $0.003 per result plus $0.0005 Actor-start per run (free-tier price; 10-30% lower on paid Apify plans)

Store listing: [Apify Store](https://apify.com/captainhandsome/gleif-lei-search)

Not for: SEC filings or state registries.

### french_company_search - French Company Registry Search (SIRENE)

Searches France's SIRENE company register.

| Argument | Required | What it does |
|---|---|---|
| query | Yes | Company name or keyword. |
| department | No | Department code filter. |
| naf_code | No | NAF/APE activity code filter. |
| active_only | No | Active companies only; default: true. |
| max_results | No | Records to retrieve; default: 10. |

Returns: siren, name, legal_name, status, hq_city, employees

Price: $0.002 per result plus $0.0005 Actor-start per run (free-tier price; 10-30% lower on paid Apify plans)

Store listing: [Apify Store](https://apify.com/captainhandsome/french-company-search)

Not for: US environmental or finance data.

### cms_healthcare_provider_search - CMS Healthcare Provider Search

Searches CMS directories for Medicare-certified facilities.

| Argument | Required | What it does |
|---|---|---|
| provider_types | No | Directory types; default: hospitals. |
| state | Yes | State or territory. |
| city | No | City filter, exact match. |
| zip | No | ZIP code filter. |
| county | No | County filter, exact match. |
| name_contains | No | Substring of provider name. |
| max_results | No | Records to bill; default: 10. |

Returns: provider_type, ccn, name, city, state, star_rating

Price: $0.02 per result plus $0.0005 Actor-start per run (free-tier price; 10-30% lower on paid Apify plans)

Store listing: [Apify Store](https://apify.com/captainhandsome/cms-healthcare-provider-search)

Not for: clinical trials or licensing.

## Pairs well with

- us_census_geocoder - adds census tract and county FIPS to a registry address - [Store](https://apify.com/captainhandsome/us-census-geocoder)
- sec_edgar_filings - pulls 10-K, 10-Q, and 8-K filings for a company found in a registry search - [Store](https://apify.com/captainhandsome/sec-edgar-filings-search)

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

- [/mcp/sec-edgar/](/mcp/sec-edgar/)
- [/mcp/google-maps/](/mcp/google-maps/)
- [/mcp/job-search/](/mcp/job-search/)
- [/mcp/government-data/](/mcp/government-data/)
- [/](/) - home page, all 25 tools

## FAQ

**How does authentication work?** Requires `APIFY_TOKEN`; runs bill the caller's own Apify account.

**How fast are these tools?** Most searches take 10-30 seconds; multi-state tools take 15-45 seconds, and `gleif_lei_search` takes 5-30 seconds. All are timeout-capped at 120 seconds.

**What isn't this data?** Not job listings, procurement awards, SEC filings, or clinical trial data; `gleif_lei_search` covers only LEI holders, and CMS data covers only Medicare-certified facilities.

**How are results returned?** JSON records, one row per match, with the fields listed under "Returns" for each tool.
