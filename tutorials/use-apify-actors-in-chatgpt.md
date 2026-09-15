---
layout: default
title: "How to use Apify public-data Actors directly in ChatGPT"
description: "Connect focused Apify public-data tools to ChatGPT through the hosted MCP server, then search business, regulatory, procurement, safety, and news data."
permalink: /tutorials/use-apify-actors-in-chatgpt/
---
# How to use Apify public-data Actors directly in ChatGPT

ChatGPT can call selected Apify Actors as tools through Apify's hosted Model Context Protocol server. This route requires no local server, exposes only the Actors you choose, and runs each search in your own Apify account.

The setup below is useful when you want ChatGPT to fetch current structured records instead of relying on general web search. It follows Apify's official [ChatGPT integration guide](https://docs.apify.com/integrations/chatgpt) and [MCP tool-selection documentation](https://docs.apify.com/integrations/mcp#tool-selection).

## Create the connector

1. In ChatGPT, enable Developer mode and open **Settings -> Apps & Connectors -> Create**.
2. Name the connector `Apify Public Data`.
3. Use one of the focused MCP server URLs below.
4. Choose OAuth authentication. No client ID or client secret is required.
5. Create the connector and authorize access to your Apify account.

ChatGPT does not currently let you change the selected tools after creating a connector. Create a second focused connector when you need a different group of Actors.

## Local business and due-diligence tools

Use this URL for business leads, website qualification, company-registration checks, and contractor verification:

```text
https://mcp.apify.com?tools=captainhandsome/google-maps-business-search,captainhandsome/tech-stack-detector,captainhandsome/us-business-entity-search,captainhandsome/us-contractor-license-search
```

Try prompts such as:

- "Find 25 commercial electricians in Dallas with phone numbers and websites."
- "Check the technology used by these company websites and identify ecommerce platforms."
- "Verify the public business registration for this company name."
- "Look up the contractor licence for this business before I add it to the lead list."

## Filings, funding, procurement, and safety tools

Use this URL for public-company filings, federal spending, funding opportunities, European tenders, and vehicle recalls:

```text
https://mcp.apify.com?tools=captainhandsome/sec-edgar-filings-search,captainhandsome/usaspending-federal-awards,captainhandsome/grants-gov-opportunity-search,captainhandsome/ted-eu-tender-search,captainhandsome/nhtsa-vehicle-recall-search
```

Try prompts such as:

- "Get Apple's five most recent 8-K filings and link the primary documents."
- "Find open federal grants about artificial intelligence and compare their deadlines and award ceilings."
- "Find recent European cybersecurity tenders and return the buyer, deadline, estimated value, and notice link."
- "Check official NHTSA recalls for a 2020 Honda Civic and summarize each remedy."

## News, jobs, and research tools

Use this URL for current news, public job listings, clinical trials, and biomedical papers:

```text
https://mcp.apify.com?tools=captainhandsome/google-news-search,captainhandsome/linkedin-public-jobs-search,captainhandsome/glassdoor-jobs-scraper,captainhandsome/clinical-trials-search,captainhandsome/europe-pmc-paper-search
```

Try prompts such as:

- "Find today's news about OpenAI or Anthropic and group the articles by publisher."
- "Find remote machine-learning jobs and return title, employer, location, and application URL."
- "Find recruiting clinical trials for glioblastoma and compare enrollment and sponsor details."
- "Find recent open-access papers about CAR-T therapy and include DOI and citation counts."

## Cost and privacy

OAuth authorizes ChatGPT to run the selected tools in your Apify account. Actor usage is charged according to each live Apify Store listing; use a small result limit while testing. The Actors query public sources and return structured datasets, but you remain responsible for lawful use, retention, and any downstream outreach.

If you prefer Claude Desktop, Cursor, or another local MCP client, install the full 33-tool package with `uvx apify-data-scrapers` as described on the [project homepage](/). The hosted ChatGPT route above is intentionally narrower so tool selection stays predictable.

## Next steps

- [Open the complete Actor catalog](/#available-extractors--store-listings)
- [Use the Google Maps business-lead workflow](/tutorials/contractor-lead-generation/)
- [Build an SEC filing monitor](/tutorials/monitor-sec-filings/)
- [Download n8n and Make automation templates](/#no-code--automation-workflows)
