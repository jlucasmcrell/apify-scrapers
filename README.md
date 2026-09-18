<!-- mcp-name: io.github.jlucasmcrell/apify-scrapers -->
mcp-name: io.github.jlucasmcrell/apify-scrapers
# Apify Public Data MCP: 40 Production Data Tools & Public Records

[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![Node.js 18+](https://img.shields.io/badge/node-18+-green.svg)](https://nodejs.org/)
[![Apify Verified](https://img.shields.io/badge/apify-store-orange.svg)](https://apify.com/captainhandsome)
[![Glama MCP Server](https://glama.ai/mcp/servers/jlucasmcrell/apify-scrapers/badge)](https://glama.ai/mcp/servers/jlucasmcrell/apify-scrapers)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Smithery](https://img.shields.io/badge/Smithery-jlucasmcrell%2Fapify--scrapers-orange)](https://smithery.ai/servers/jlucasmcrell/apify-scrapers)
[![Listed on mcpservers.org](https://mcpservers.org/badge.svg)](https://mcpservers.org/servers/jlucasmcrell/apify-scrapers)
One MCP server gives an AI agent **40 production data extractors** - Google Maps business leads, Google News, Google Autocomplete, LinkedIn and Glassdoor jobs, SEC EDGAR, USAspending, Grants.gov, TED tenders, NHTSA recalls, FEC, EPA, ClinicalTrials.gov, openFDA, Europe PMC, GLEIF, CMS providers, Census geocoding, state business registries, contractor licences, Airbnb, YouTube, Twitch and Google Play - each running as an Actor on your own **[Apify](https://apify.com/captainhandsome)** account. Install with `uvx apify-data-scrapers` (Claude Desktop, Cursor, any MCP client), or call the same Actors directly from Python, Node.js or no-code tools.

Each actor is built with strict schema validation, deterministic field mapping, self-healing DOM selectors, and pay-per-event pricing (per-result rates from **$0.00015**, Actor-start from **$0.0005**; the live Apify Store price is authoritative).

---

## Runtime contract and spending control

Since version 1.1.0, calls return `{results, status, run?}` in both MCP structured content and text. Status is `success`, `partial`, `empty_unverified`, or `error`; errors include a stable code and retry guidance. Zero rows are not proof that no matching records exist. Existing integrations that parsed a bare result array must now read `results`. Native dataset field names are preserved.

Each call requests a 120-second Actor timeout and a pay-per-event charge cap of $1 by default. Set `APIFY_MAX_CHARGE_USD` to adjust the cap. This is per run, not a total account spending limit; platform fees outside Actor event charges may still apply. Up to four calls may run concurrently. Cancelling a request attempts to abort its cloud run; check the returned run ID if confirmation fails. An ambiguous start is never retried automatically.

The MCP executable is Python; Node.js files are direct Actor API examples, not a second MCP server. Private queued Actors are omitted from this public catalog.

## Quick Navigation

- [Make.com templates](#makecom-templates)
- [Use-case guides](#use-case-guides)
- [Available Extractors & Store Listings](#available-extractors--store-listings)
- [Python Quickstart](#python-quickstart)
- [Node.js Quickstart](#nodejs-quickstart)
- [No-Code & Automation Workflows (n8n, Sheets, Slack)](#no-code--automation-workflows)
- [Pre-Built Example Tasks (Zero Code)](#pre-built-example-tasks-zero-code)
- [Free Sample Datasets](#free-sample-datasets)
- [AI Agent & MCP Integration (Claude Desktop, Cursor, Custom Agent)](#ai-agent--mcp-integration)
- [In-Depth Engineering Guides](#in-depth-engineering-guides)
- [Repository Structure](#repository-structure)
- [Contributing & Author](#author--support)

---

## Choose your tools

[Choose a focused tool profile and generate your installation configuration](https://apify.revenuesystemslabs.com/choose-tools/).

Version 1.2.0 adds the optional `APIFY_TOOL_PROFILE` environment variable: `all` (default), `leads`, `market`, `government`, or `research`. These correspond to the four catalog categories below. Profiles restrict tool discovery and calls, prompts, and the Actor catalog. Restart the MCP server and refresh/reconnect your client after changing the profile. Keep only the focused server entry if you do not also want the full catalog loaded. Direct Actor API examples are unchanged; this setting is not an Apify account permission boundary.

## Choose your first workflow

| Your goal | Start here | What to expect |
|---|---|---|
| Build a local contractor lead list | [Dallas electrician example task](https://apify.com/captainhandsome/google-maps-business-search/examples/dallas-commercial-electrician-leads) | Review the prefilled input, set a small result limit, then run and export the dataset. |
| Track company filings | [SEC filing-monitor tutorial](https://apify.revenuesystemslabs.com/tutorials/monitor-sec-filings/) | Choose companies and form types; retain filing identifiers to avoid duplicate alerts. |
| Compare healthcare providers over time | [CMS provider-monitor tutorial](https://apify.revenuesystemslabs.com/tutorials/monitor-healthcare-provider-changes/) | Save snapshots and compare changes in the source dataset, not real-time clinical outcomes. |
| Use an AI chat interface | [ChatGPT and Apify MCP setup](https://apify.revenuesystemslabs.com/tutorials/use-apify-actors-in-chatgpt/) | Connect your own Apify account and choose the Actor explicitly. |

No separate subscription to this MCP package is required. Actor runs are billed through your Apify account at the displayed Store price. Start with a small run and inspect its output before scheduling recurring work; public-source data can be delayed, incomplete, or temporarily unavailable.

---

## Privacy Policy

The MCP server collects nothing. It runs on your machine, reads `APIFY_TOKEN` from your environment, and its only outbound calls are to the Apify API to run the Actor you asked for — on your own Apify account. No telemetry, no logs, no data sent to us. Full policy: [apify.revenuesystemslabs.com/privacy](https://apify.revenuesystemslabs.com/privacy/).

## Make.com templates

Eight published Make scenarios, one click to copy into your own Make account. Each asks for your Apify token and your destination (Google Sheets or Slack) in the setup wizard.

| Template | Actor it runs |
|---|---|
| [Google Maps Leads to Google Sheets](https://www.make.com/en/integration/19727?templatePublicId=19727) | [`google-maps-business-search`](https://apify.com/captainhandsome/google-maps-business-search) |
| [Glassdoor Jobs to Google Sheets](https://www.make.com/en/integration/19728?templatePublicId=19728) | [`glassdoor-jobs-scraper`](https://apify.com/captainhandsome/glassdoor-jobs-scraper) |
| [California Contractor Licenses to Google Sheets](https://www.make.com/en/integration/19729?templatePublicId=19729) | [`ca-contractor-license-search`](https://apify.com/captainhandsome/ca-contractor-license-search) |
| [SEC EDGAR Filing Alerts to Slack](https://www.make.com/en/integration/19730?templatePublicId=19730) | [`sec-edgar-filings-search`](https://apify.com/captainhandsome/sec-edgar-filings-search) |
| [Export Google News Results to Google Sheets](https://www.make.com/en/integration/19731?templatePublicId=19731) | [`google-news-search`](https://apify.com/captainhandsome/google-news-search) |
| [Export Grants.gov Opportunities to Google Sheets](https://www.make.com/en/integration/19732?templatePublicId=19732) | [`grants-gov-opportunity-search`](https://apify.com/captainhandsome/grants-gov-opportunity-search) |
| [Export TED EU Tenders to Google Sheets](https://www.make.com/en/integration/19733?templatePublicId=19733) | [`ted-eu-tender-search`](https://apify.com/captainhandsome/ted-eu-tender-search) |
| [Export NHTSA Vehicle Recalls to Google Sheets](https://www.make.com/en/integration/19734?templatePublicId=19734) | [`nhtsa-vehicle-recall-search`](https://apify.com/captainhandsome/nhtsa-vehicle-recall-search) |

## Use-case guides

One page per question an agent gets asked, each listing the tools, arguments, returned fields and prices for that job:

- [MCP server for SEC EDGAR filings](https://apify.revenuesystemslabs.com/mcp/sec-edgar/)
- [MCP server for Google Maps data and business leads](https://apify.revenuesystemslabs.com/mcp/google-maps/)
- [MCP server for public records: business registries, licences and providers](https://apify.revenuesystemslabs.com/mcp/public-records/)
- [MCP server for job search: LinkedIn and Glassdoor listings](https://apify.revenuesystemslabs.com/mcp/job-search/)
- [MCP server for US government data](https://apify.revenuesystemslabs.com/mcp/government-data/)

Focused, end-to-end tutorials:

- [Use public-data Actors directly in ChatGPT with Apify MCP](https://apify.revenuesystemslabs.com/tutorials/use-apify-actors-in-chatgpt/)
- [Monitor SEC EDGAR filings automatically](https://apify.revenuesystemslabs.com/tutorials/monitor-sec-filings/)
- [Build a contractor lead list from Google Maps](https://apify.revenuesystemslabs.com/tutorials/contractor-lead-generation/)
- [Monitor CMS healthcare-provider changes](https://apify.revenuesystemslabs.com/tutorials/monitor-healthcare-provider-changes/)

---

## Available Extractors & Store Listings

Every extractor below is both an Apify Store listing and an MCP tool of the same server; the sections are the questions buyers arrive with.

### Business intelligence & lead generation

Also available: [Cross-border company registry search](https://apify.com/captainhandsome/company-registry-search), combining UK, French and GLEIF records where available.

| Tool | Store Link | Key Output Fields | Best For |
|---|---|---|---|
| **Google Maps Business Leads** | [`captainhandsome/google-maps-business-search`](https://apify.com/captainhandsome/google-maps-business-search) | Name, phone, website, rating, reviews, address, coordinates, hours | B2B lead generation, local agency prospecting |
| **Website Tech Stack & Ecommerce Scanner** | [`captainhandsome/tech-stack-detector`](https://apify.com/captainhandsome/tech-stack-detector) | technologies, cms, ecommerce_platform, payments, emails | Best for competitive tech research and B2B lead qualification across a batch of company websites. |
| **US Business Entity Registries** | [`captainhandsome/us-business-entity-search`](https://apify.com/captainhandsome/us-business-entity-search) | Legal entity name, filing number, jurisdiction, status | Legal due diligence, corporate registration checks |
| **Alabama Business Entity Search** | [`captainhandsome/al-business-entity-search`](https://apify.com/captainhandsome/al-business-entity-search) | entity id, entity name, location, entity type, status | Search Alabama business entities by company name and export entity IDs |
| **Florida Sunbiz Business Entity Search** | [`captainhandsome/fl-sos-new-filings`](https://apify.com/captainhandsome/fl-sos-new-filings) | entity name, document number, status, entity type, date filed | Search Florida Sunbiz company-name results and export legal entity nam |
| **Florida Sunbiz Officer & Registered Agent Search** | [`captainhandsome/fl-sunbiz-officer-search`](https://apify.com/captainhandsome/fl-sunbiz-officer-search) | officer name, entity name, document number, detail url, entity type | Search Florida Sunbiz by officer or registered-agent name and export o |
| **French Company Search** | [`captainhandsome/french-company-search`](https://apify.com/captainhandsome/french-company-search) | siren, name, legal name, acronym, status | Search France's official company register by name, activity, postcode, |
| **GLEIF LEI Lookup** | [`captainhandsome/gleif-lei-search`](https://apify.com/captainhandsome/gleif-lei-search) | lei, legal_name, registered_as, legal_form_name, status | Best for KYC and counterparty due diligence: resolving a company's Legal Entity Identifier, registration status, and own national registry number before onboarding. |
| **US Contractor Licenses** | [`captainhandsome/us-contractor-license-search`](https://apify.com/captainhandsome/us-contractor-license-search) | Contractor name, license number, classification, status, state | Trades verification, subcontractor diligence |
| **California Contractor License Search** | [`captainhandsome/ca-contractor-license-search`](https://apify.com/captainhandsome/ca-contractor-license-search) | contractor name, name type, license number, city, status | Search California CSLB contractor records by contractor name and expor |

### Jobs, market & consumer intelligence

| Tool | Store Link | Key Output Fields | Best For |
|---|---|---|---|
| **Glassdoor Jobs & Salaries** | [`captainhandsome/glassdoor-jobs-scraper`](https://apify.com/captainhandsome/glassdoor-jobs-scraper) | Title, company, salary estimate, rating, location, job URL, posting date | Hiring intelligence, compensation benchmarking |
| **LinkedIn Public Jobs** | [`captainhandsome/linkedin-public-jobs-search`](https://apify.com/captainhandsome/linkedin-public-jobs-search) | Job title, employer, location, direct apply URL, posting age | Recruitment, tech talent monitoring |
| **Airbnb Vacation Rentals** | [`captainhandsome/airbnb-listings-search`](https://apify.com/captainhandsome/airbnb-listings-search) | Title, room type, nightly price, rating, reviews count, listing URL | Real estate research, market rate tracking |
| **Google Play App Reviews** | [`captainhandsome/google-play-reviews-scraper`](https://apify.com/captainhandsome/google-play-reviews-scraper) | Review text, star score, thumbs up, date, reviewer name | App store sentiment, competitor feedback |
| **Apple App Store Reviews** | [`captainhandsome/app-store-reviews-search`](https://apify.com/captainhandsome/app-store-reviews-search) | app_name, review_rating, review_body, review_version, app_average_rating | iOS review mining, ASO research and cross-platform sentiment |
| **YouTube Video Search** | [`captainhandsome/youtube-search-scraper`](https://apify.com/captainhandsome/youtube-search-scraper) | Title, video URL, channel, views count, duration, publish date | Content tracking, creator outreach |
| **Twitch Live Streams** | [`captainhandsome/twitch-live-streams-scraper`](https://apify.com/captainhandsome/twitch-live-streams-scraper) | Streamer username, title, viewer count, language, category | Esports analytics, live stream monitoring |

### Government & public records

Also available: [SEC Form 4 insider transactions](https://apify.com/captainhandsome/sec-form-4-insider-transactions), [OFAC sanctions](https://apify.com/captainhandsome/ofac-sanctions-search), [CourtListener cases](https://apify.com/captainhandsome/courtlistener-case-search), and [NVD/CISA vulnerability intelligence](https://apify.com/captainhandsome/nvd-cisa-vulnerability-intelligence).

| Tool | Store Link | Key Output Fields | Best For |
|---|---|---|---|
| **SEC EDGAR Corporate Filings** | [`captainhandsome/sec-edgar-filings-search`](https://apify.com/captainhandsome/sec-edgar-filings-search) | Ticker, CIK, form (10-K, 10-Q, 8-K), filing date, primary document URL | Financial diligence, equity research, compliance |
| **USAspending Federal Awards** | [`captainhandsome/usaspending-federal-awards`](https://apify.com/captainhandsome/usaspending-federal-awards) | Recipient vendor, award amount, awarding agency, description, dates | Government contracting, procurement intel |
| **Grants.gov Funding Opportunities** | [`captainhandsome/grants-gov-opportunity-search`](https://apify.com/captainhandsome/grants-gov-opportunity-search) | Opportunity number, agency, deadline, award range, eligibility, contacts | Federal grant prospecting and funding monitoring |
| **TED European Tenders** | [`captainhandsome/ted-eu-tender-search`](https://apify.com/captainhandsome/ted-eu-tender-search) | Buyer, country, CPV code, deadline, estimated value, source documents | European procurement and bid discovery |
| **NHTSA Vehicle Recalls** | [`captainhandsome/nhtsa-vehicle-recall-search`](https://apify.com/captainhandsome/nhtsa-vehicle-recall-search) | Campaign number, component, defect, consequence, remedy, affected units | Vehicle-safety checks and recall monitoring |
| **FEC Campaign Finance Search** | [`captainhandsome/fec-campaign-finance-search`](https://apify.com/captainhandsome/fec-campaign-finance-search) | record type, id, name, party, office | Search US federal candidates, PACs and campaign contributions by state |
| **EPA ECHO Facility Compliance & Violations** | [`captainhandsome/epa-echo-facility-search`](https://apify.com/captainhandsome/epa-echo-facility-search) | registry id, name, street, city, state | Search EPA-regulated US facilities by state, ZIP, NAICS, name, program |
| **US Census Address Geocoder** | [`captainhandsome/us-census-geocoder`](https://apify.com/captainhandsome/us-census-geocoder) | matched_address, county_name, tract_geoid, block_geoid, congressional_district_geoid | Best for appending census tract, county FIPS and district GEOIDs to US addresses for demographic joins and compliance reporting. |

### Research & health data

| Tool | Store Link | Key Output Fields | Best For |
|---|---|---|---|
| **ClinicalTrials.gov Search** | [`captainhandsome/clinical-trials-search`](https://apify.com/captainhandsome/clinical-trials-search) | nct id, title, official title, acronym, org study id | Search the official ClinicalTrials.gov API by condition, intervention, |
| **Europe PMC Paper Search** | [`captainhandsome/europe-pmc-paper-search`](https://apify.com/captainhandsome/europe-pmc-paper-search) | title, doi, pmid, abstract, cited_by_count | Best for biomedical literature reviews, citation tracking, and open-access discovery across PubMed and Europe PMC. |
| **openFDA Drug Labels, Recalls & Adverse Events** | [`captainhandsome/openfda-search`](https://apify.com/captainhandsome/openfda-search) | dataset, id, brand name, generic name, manufacturer | Search official FDA drug labels, approvals, adverse events, and drug,  |
| **CMS Healthcare Provider Search** | [`captainhandsome/cms-healthcare-provider-search`](https://apify.com/captainhandsome/cms-healthcare-provider-search) | name, provider_type, city, state, star_rating | Compare CMS-certified hospitals, nursing homes, and other Medicare providers by location, ownership, and star rating. |

---

## Python Quickstart

### 1. Install dependencies

```bash
pip install apify-client pandas python-dotenv
```

### 2. Export 50 Google Maps Leads to CSV

```python
import os
from apify_client import ApifyClient
import pandas as pd

# Get your API token from https://console.apify.com/account/integrations
client = ApifyClient(os.getenv("APIFY_TOKEN"))

# Run the actor
run = client.actor("captainhandsome/google-maps-business-search").call(run_input={
    "search_query": "commercial electricians",
    "location": "Dallas, Texas",
    "max_items": 50,
    "include_details": True,
})

# Fetch dataset items and export to CSV
items = list(client.dataset(run["defaultDatasetId"]).iterate_items())
df = pd.DataFrame(items)
df.to_csv("dallas_electricians.csv", index=False)
print(f"Exported {len(df)} leads to dallas_electricians.csv")
```

See [examples/google_maps_leads_to_csv.py](examples/google_maps_leads_to_csv.py) for the full script.

---

## Node.js Quickstart

### 1. Install dependencies

```bash
npm install apify-client
```

### 2. Query SEC EDGAR Filings

```javascript
import { ApifyClient } from 'apify-client';

const client = new ApifyClient({ token: process.env.APIFY_TOKEN });

const run = await client.actor('captainhandsome/sec-edgar-filings-search').call({
  companies: ['AAPL', 'NVDA', 'MSFT'],
  forms: ['10-K'],
  max_items: 15,
});

const { items } = await client.dataset(run.defaultDatasetId).listItems();
items.forEach(filing => {
  console.log(`[${filing.ticker}] ${filing.form} (${filing.filing_date}): ${filing.filing_url}`);
});
```

See [examples/sec_filings.js](examples/sec_filings.js) for the full script.

---

## No-Code & Automation Workflows

If you automate via n8n, Make, Zapier, or Google Sheets, ready-to-import blueprints are included in [`workflows/`](workflows/):

- **[Google Maps Leads to Google Sheets (n8n)](workflows/n8n_google_maps_to_sheets.json):** Weekly scheduled local-lead extraction into Google Sheets with persistent duplicate suppression.
- **[SEC EDGAR 10-K & 8-K Alerts (n8n)](workflows/n8n_sec_edgar_to_slack.json):** Four-hour filing monitor with persistent duplicate suppression.
- **[Competitor News Alerts (n8n)](workflows/n8n_google_news_competitor_monitor.json):** Daily Google News monitoring with persistent duplicate suppression.
- **[Grants.gov Opportunity Alerts (n8n)](workflows/n8n_grants_gov_opportunity_monitor.json):** Daily funding-opportunity monitoring with persistent duplicate suppression.
- **[TED European Tender Alerts (n8n)](workflows/n8n_ted_eu_tender_monitor.json):** Daily procurement monitoring with persistent duplicate suppression.
- **[NHTSA Vehicle Recall Alerts (n8n)](workflows/n8n_nhtsa_vehicle_recall_monitor.json):** Daily safety-recall monitoring with persistent duplicate suppression.
- **[Eight Make-approved templates](https://github.com/jlucasmcrell/apify-scrapers/tree/master/templates/make_blueprints):** Guided setup for Google Sheets and Slack workflows. Connect your own accounts and review inputs before running; Apify and Make usage charges may apply.

Open a template in Make: [Google Maps](https://www.make.com/en/hq/template/19727-google-maps-leads-to-google-sheets-with-apify), [Glassdoor](https://www.make.com/en/hq/template/19728-glassdoor-jobs-to-google-sheets-with-apify), [California contractors](https://www.make.com/en/hq/template/19729-california-contractor-licenses-to-google-sheets-with-apify), [SEC filings to Slack](https://www.make.com/en/hq/template/19730-sec-edgar-filing-alerts-to-slack-with-apify), [Google News](https://www.make.com/en/hq/template/19731-export-google-news-results-to-google-sheets-with-apify), [Grants.gov](https://www.make.com/en/hq/template/19732-export-grants-gov-opportunities-to-google-sheets-with-apify), [TED tenders](https://www.make.com/en/hq/template/19733-export-ted-eu-tenders-to-google-sheets-with-apify), or [NHTSA recalls](https://www.make.com/en/hq/template/19734-export-nhtsa-vehicle-recalls-to-google-sheets-with-apify).

---

## Pre-Built Example Tasks (Zero Code)

If you prefer runnable web UI tasks without writing any code, each actor includes pre-configured tasks published on Apify Store:

### Google Maps Leads
- [Phoenix HVAC Company Leads](https://apify.com/captainhandsome/google-maps-business-search/examples/phoenix-hvac-company-leads)
- [Dallas Commercial Electrician Leads](https://apify.com/captainhandsome/google-maps-business-search/examples/dallas-commercial-electrician-leads)
- [Chicago Dentist Directory](https://apify.com/captainhandsome/google-maps-business-search/examples/chicago-dentist-directory)

### Glassdoor Jobs
- [Austin Software Developer Jobs](https://apify.com/captainhandsome/glassdoor-jobs-scraper/examples/austin-software-developer-jobs)
- [Seattle Product Manager Jobs](https://apify.com/captainhandsome/glassdoor-jobs-scraper/examples/seattle-product-manager-jobs)
- [New York Data Analyst Jobs](https://apify.com/captainhandsome/glassdoor-jobs-scraper/examples/new-york-data-analyst-jobs)

### Airbnb Rentals
- [Nashville Airbnb Listings](https://apify.com/captainhandsome/airbnb-listings-search/examples/nashville-airbnb-listings)
- [Miami Airbnb Listings](https://apify.com/captainhandsome/airbnb-listings-search/examples/miami-airbnb-listings)
- [Austin Airbnb Listings](https://apify.com/captainhandsome/airbnb-listings-search/examples/austin-airbnb-listings)

### YouTube & Google Play
- [Small Business Marketing Videos](https://apify.com/captainhandsome/youtube-search-scraper/examples/small-business-marketing-videos)
- [Python Tutorial Video Research](https://apify.com/captainhandsome/youtube-search-scraper/examples/python-tutorial-video-research)
- [Instagram One-Star Play Store Reviews](https://apify.com/captainhandsome/google-play-reviews-scraper/examples/one-star-instagram-reviews)

---

## Free Sample Datasets

Looking for clean data to benchmark, analyze, or train models? Verified sample bundles with metadata schemas are available in [`datasets/`](datasets/) and hosted publicly on Hugging Face Datasets:

Eight verified sample bundles, each exported from a production run of the Actor named beside it. Every one is served from this repository and mirrored to Hugging Face, where the dataset card links back to the Actor that produced it.

1. **Phoenix HVAC Contractor Leads:** [`datasets/phoenix_hvac_leads/`](https://huggingface.co/datasets/joeygambino/phoenix-hvac-contractor-leads) | [Hugging Face Hub](https://huggingface.co/datasets/joeygambino/phoenix-hvac-contractor-leads) — 10 verified HVAC contractor profiles with ratings, addresses, and phone numbers ([Google Maps Business Leads](https://apify.com/captainhandsome/google-maps-business-search)).
2. **California Licensed Contractors:** [`datasets/california_solar_contractors/`](https://huggingface.co/datasets/joeygambino/california-solar-contractors) | [Hugging Face Hub](https://huggingface.co/datasets/joeygambino/california-licensed-contractors) — 50 active C-46 and B licensed solar installers with state verification numbers ([California Contractor License Search](https://apify.com/captainhandsome/ca-contractor-license-search)).
3. **Austin Software Engineer Postings:** [`datasets/austin_software_jobs/`](https://huggingface.co/datasets/joeygambino/austin-software-jobs) | [Hugging Face Hub](https://huggingface.co/datasets/joeygambino/austin-software-engineer-jobs) — 30 normalized job listings with estimated posting dates and salary ranges ([LinkedIn Public Jobs](https://apify.com/captainhandsome/linkedin-public-jobs-search)).
4. **S&P 500 Corporate Filings:** [`datasets/sp500_sec_edgar_filings/`](https://huggingface.co/datasets/joeygambino/sp500-sec-edgar-filings) | [Hugging Face Hub](https://huggingface.co/datasets/joeygambino/sp500-sec-edgar-filings) — 5 SEC EDGAR filing records with CIK, ticker, SIC and document links ([SEC EDGAR Filings](https://apify.com/captainhandsome/sec-edgar-filings-search)).
5. **US Federal Defense & AI Awards:** [`datasets/us_federal_defense_ai_awards/`](https://huggingface.co/datasets/joeygambino/us-federal-defense-ai-awards) | [Hugging Face Hub](https://huggingface.co/datasets/joeygambino/us-federal-defense-ai-awards) — 10 federal contract awards with recipient, agency, obligation amount and dates ([USAspending Federal Awards](https://apify.com/captainhandsome/usaspending-federal-awards)).
6. **US Remote AI & ML Job Postings:** [`datasets/us_remote_ai_ml_job_postings/`](https://huggingface.co/datasets/joeygambino/us-remote-ai-ml-job-postings) | [Hugging Face Hub](https://huggingface.co/datasets/joeygambino/us-remote-ai-ml-job-postings) — 10 remote AI/ML postings with title, company, location and apply URL ([LinkedIn Public Jobs](https://apify.com/captainhandsome/linkedin-public-jobs-search)).
7. **Top Twitch Live Streams:** [`datasets/twitch_top_live_streams_metadata/`](https://huggingface.co/datasets/joeygambino/twitch-top-live-streams-metadata) | [Hugging Face Hub](https://huggingface.co/datasets/joeygambino/twitch-top-live-streams-metadata) — 10 live-channel records with viewer counts, category and language ([Twitch Live Streams](https://apify.com/captainhandsome/twitch-live-streams-scraper)).
8. **Mobile App Sentiment Reviews:** [`datasets/mobile_apps_user_sentiment_reviews/`](https://huggingface.co/datasets/joeygambino/mobile-apps-user-sentiment-reviews) | [Hugging Face Hub](https://huggingface.co/datasets/joeygambino/mobile-apps-user-sentiment-reviews) — 10 Google Play reviews with score, thumbs-up count and reviewer metadata ([Google Play Reviews](https://apify.com/captainhandsome/google-play-reviews-scraper)).

---

## AI Agent & MCP Integration

All actors in this repository conform to OpenAPI and JSON Schema standards, making them directly callable by AI agents via the Model Context Protocol (MCP):

### Option 1: Claude Desktop / Cursor with UVX (Recommended)

Add this to your `claude_desktop_config.json` or Cursor MCP settings:

```json
{
  "mcpServers": {
    "apify-data-scrapers": {
      "command": "uvx",
      "args": ["apify-data-scrapers"],
      "env": {
        "APIFY_TOKEN": "YOUR_APIFY_API_TOKEN"
      }
    }
  }
}
```

### Option 2: Docker Container (Glama / Cloud)

Run via Docker:

```json
{
  "mcpServers": {
    "apify-data-scrapers": {
      "command": "docker",
      "args": ["run", "-i", "--rm", "-e", "APIFY_TOKEN", "glcr.b-cdn.net/jlucasmcrell/apify-scrapers:latest"],
      "env": {
        "APIFY_TOKEN": "YOUR_APIFY_API_TOKEN"
      }
    }
  }
}
```

### Option 3: Local Python Stdio Runner

Install via pip or run directly:

```bash
pip install apify-data-scrapers
export APIFY_TOKEN="your_token_here"
apify-data-scrapers
```

Or from local source:
```bash
python mcp_server.py
```

### Agent Prompts That Work Out-of-the-Box:
- *"Search Google Maps for 50 commercial roofers in Atlanta with phone numbers and websites."*
- *"Retrieve Apple and Microsoft Form 10-K filings from SEC EDGAR for the last 2 years."*
- *"Search Glassdoor for remote product manager jobs with salary estimates."*

---

## In-Depth Engineering Guides

Technical case studies and problem-solution writeups are located in [`articles/`](articles/):

- **[Bypassing Playwright Headless Pagination Hurdles on Airbnb](articles/airbnb_playwright_pagination_guide.md):** How to solve sticky overlay modal interruptions and viewport boundary clipping in large headless browser crawls.
- **[Extracting & Normalizing Clean Job Posting Dates from Glassdoor](articles/glassdoor_posting_dates_guide.md):** Overcoming relative timestamp drift (\"24h\", \"3d\", \"30d+\") with deterministic parsing and ISO-8601 boundary tracking.

---

## Repository Structure

```text
apify-scrapers/
 README.md                                # Documentation and quickstart
 LICENSE                                  # MIT License
 requirements.txt                         # Python client dependencies
 package.json                             # Node.js dependencies
 mcp.json                                 # MCP tool registry specification
 mcp_server.py                            # Native Python stdio MCP server
 articles/                                # In-depth engineering case studies
    airbnb_playwright_pagination_guide.md
    glassdoor_posting_dates_guide.md
    reddit_community_responses.md        # Reference technical answers for forums
 datasets/                                # Sample benchmark datasets
    phoenix_hvac_leads/
    california_solar_contractors/
    austin_software_jobs/
 workflows/                               # No-code automation templates
    n8n_google_maps_to_sheets.json
    n8n_sec_edgar_to_slack.json
    n8n_google_news_competitor_monitor.json
    n8n_grants_gov_opportunity_monitor.json
    n8n_ted_eu_tender_monitor.json
    README.md
 examples/                                # Standalone developer scripts
     google_maps_leads_to_csv.py
     sec_edgar_filings_downloader.py
     glassdoor_jobs_tracker.py
     airbnb_market_scraper.py
     usaspending_defense_awards.py
     twitch_live_stream_monitor.py
     google_maps_leads.js
     sec_filings.js
```

---

## Author & Support

Maintained by **[Joseph McRell](https://apify.com/captainhandsome)**.

- **Apify Store:** [https://apify.com/captainhandsome](https://apify.com/captainhandsome)
- **GitHub:** [@jlucasmcrell](https://github.com/jlucasmcrell)
- **Hugging Face:** [@joeygambino](https://huggingface.co/joeygambino)
- **Issues & Requests:** Please open an issue on this repository or submit a ticket on the respective Apify Actor Store page.

---

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

