---
layout: default
title: "MCP server for Google Maps data and business leads"
description: "This MCP server lets an AI agent fetch Google Maps business listings, phone numbers, websites, addresses, ratings, and review counts on demand."
permalink: /mcp/google-maps/
---
# MCP server for Google Maps data and business leads

This MCP server for Google Maps data and business leads gives an AI agent one tool, `google_maps_search`, for pulling local commercial listings straight out of Google Maps. An agent can hand it a trade category and a city and get back a structured list of businesses with phone numbers, websites, addresses, and review data, ready to drop into a spreadsheet or a CRM import. Every tool in the toolset runs as an Apify Actor on your own Apify account, so nothing routes through a shared quota, and the free plan works fine for testing and light use. This page is one of 33 tools exposed by [Apify Public Data MCP](/), a single MCP server that also covers business registries, contractor licenses, job boards, SEC filings, and more.

Want the complete workflow? Follow the [contractor lead-generation tutorial](/tutorials/contractor-lead-generation/) from search through licence verification and CSV export.

## What an agent can ask

- "Find HVAC contractors in Phoenix, AZ" -> google_maps_search(search_query="HVAC contractors in Phoenix, AZ")
- "Get me 25 commercial electricians in Dallas, TX" -> google_maps_search(search_query="Commercial Electricians Dallas TX", max_results=25)
- "List roofing companies near Denver, CO with their phone numbers" -> google_maps_search(search_query="roofing companies in Denver, CO")
- "Pull the top 10 plumbers in Austin, TX for a lead list" -> google_maps_search(search_query="plumbers in Austin, TX", max_results=10)
- "What technology is running on the websites of these landscaping companies?" -> google_maps_search(search_query="landscaping companies in Tampa, FL") then tech_stack_detector(urls=["example-landscaping.com"])
- "Is this contractor actually licensed in California?" -> google_maps_search(search_query="Smith Construction San Diego, CA") then us_contractor_license_search(search_query="Smith Construction")
- "Geocode the addresses of these business leads for a territory map" -> google_maps_search(search_query="dentists in Cleveland, OH") then us_census_geocoder(addresses=["123 Main St, Cleveland, OH 44101"])

## Tools

### google_maps_search - Google Maps Local Business and B2B Lead Extractor

This tool extracts verified commercial business listings from Google Maps, including postal addresses, phone numbers, customer review ratings, and canonical websites. It is meant for local commercial directories, trade contractors, physical retail storefronts, and B2B regional sales leads, not for employment listings, corporate filings, federal contracts, or vacation rentals. The call is read-only: it does not modify any external database, account, or state, and it runs synchronously in the cloud through the Apify Actor named in the digest below.

| Argument | Required | What it does |
|---|---|---|
| search_query | Yes | Geographic search query combining target trade category and municipal market location (e.g. 'HVAC contractors in Phoenix, AZ' or 'Commercial Electricians Dallas TX'). |
| max_results | No | Maximum count of business lead records to extract and return. default: 10 |

Returns: title, phone, website, address, totalScore, reviewsCount, categoryName, url

Price: $0.0025 per result plus $0.001 Actor-start per run (free-tier price; 10-30% lower on paid Apify plans)

Store listing: [Google Maps Business Leads Scraper - Local Lead Generation](https://apify.com/captainhandsome/google-maps-business-search)

Not for: employment job listings, corporate regulatory filings, federal procurement awards, or short-term vacation rentals.

## Pairs well with

A google_maps_search result gives an agent a name, address, and website; these four tools take that lead further without leaving the same MCP server.

- tech_stack_detector - checks the CMS, ecommerce platform, and contact links on a lead's website - [Store](https://apify.com/captainhandsome/tech-stack-detector)
- us_business_entity_search - confirms a lead's corporate registration across Florida, Alabama, Iowa, and Wisconsin - [Store](https://apify.com/captainhandsome/us-business-entity-search)
- us_contractor_license_search - verifies a contracting lead's California or Oregon license status - [Store](https://apify.com/captainhandsome/us-contractor-license-search)
- us_census_geocoder - turns a lead's street address into census tract, county, and district geography - [Store](https://apify.com/captainhandsome/us-census-geocoder)

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
- [/mcp/public-records/](/mcp/public-records/)
- [/mcp/job-search/](/mcp/job-search/)
- [/mcp/government-data/](/mcp/government-data/)
- [/](/)

## FAQ

**How does authentication work?**
Each tool, including google_maps_search, requires the `APIFY_TOKEN` environment variable. Runs execute as an Apify Actor under your own Apify account, so usage bills to your account, not a shared one, and no separate Google API key is needed.

**How fast is a typical google_maps_search call?**
Typical run duration is 15-45 seconds, with a timeout capped at 120 seconds, the same latency and limits figures the tool digest states for this Actor.

**What is google_maps_search not for?**
It is not for employment job listings, corporate regulatory filings, federal procurement awards, or short-term vacation rentals. The digest names glassdoor_jobs_search, sec_edgar_filings, usaspending_contracts, and airbnb_listings_search as the tools built for those cases instead.

**How do results come back?**
As JSON records, one per business listing, with fields such as title, phone, website, address, totalScore, reviewsCount, categoryName, and url. An agent can filter, sort, or re-shape that list however the task needs once it has the raw records.
