# Apify Public Data Scrapers & Extractors

[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![Node.js 18+](https://img.shields.io/badge/node-18+-green.svg)](https://nodejs.org/)
[![Apify Verified](https://img.shields.io/badge/apify-store-orange.svg)](https://apify.com/captainhandsome)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

A curated collection of reliable, production-ready scrapers and public-data extractors hosted on the **[Apify Store](https://apify.com/captainhandsome)**. 

Each actor is built with strict schema validation, deterministic field mapping, self-healing DOM selectors, and pay-per-event pricing starting at **$0.0002 / start**.

---

## Quick Navigation

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

## Available Extractors & Store Listings

| Tool | Store Link | Key Output Fields | Best For |
|---|---|---|---|
| **Google Maps Business Leads** | [`captainhandsome/google-maps-business-search`](https://apify.com/captainhandsome/google-maps-business-search) | Name, phone, website, rating, reviews, address, coordinates, hours | B2B lead generation, local agency prospecting |
| **Glassdoor Jobs & Salaries** | [`captainhandsome/glassdoor-jobs-scraper`](https://apify.com/captainhandsome/glassdoor-jobs-scraper) | Title, company, salary estimate, rating, location, job URL, posting date | Hiring intelligence, compensation benchmarking |
| **Airbnb Vacation Rentals** | [`captainhandsome/airbnb-listings-search`](https://apify.com/captainhandsome/airbnb-listings-search) | Title, room type, nightly price, rating, reviews count, listing URL | Real estate research, market rate tracking |
| **SEC EDGAR Corporate Filings** | [`captainhandsome/sec-edgar-filings-search`](https://apify.com/captainhandsome/sec-edgar-filings-search) | Ticker, CIK, form (10-K, 10-Q, 8-K), filing date, primary document URL | Financial diligence, equity research, compliance |
| **USAspending Federal Awards** | [`captainhandsome/usaspending-federal-awards`](https://apify.com/captainhandsome/usaspending-federal-awards) | Recipient vendor, award amount, awarding agency, description, dates | Government contracting, procurement intel |
| **LinkedIn Public Jobs** | [`captainhandsome/linkedin-public-jobs-search`](https://apify.com/captainhandsome/linkedin-public-jobs-search) | Job title, employer, location, direct apply URL, posting age | Recruitment, tech talent monitoring |
| **Google Play App Reviews** | [`captainhandsome/google-play-reviews-scraper`](https://apify.com/captainhandsome/google-play-reviews-scraper) | Review text, star score, thumbs up, date, reviewer name | App store sentiment, competitor feedback |
| **YouTube Video Search** | [`captainhandsome/youtube-search-scraper`](https://apify.com/captainhandsome/youtube-search-scraper) | Title, video URL, channel, views count, duration, publish date | Content tracking, creator outreach |
| **Twitch Live Streams** | [`captainhandsome/twitch-live-streams-scraper`](https://apify.com/captainhandsome/twitch-live-streams-scraper) | Streamer username, title, viewer count, language, category | Esports analytics, live stream monitoring |
| **US Contractor Licenses** | [`captainhandsome/us-contractor-license-search`](https://apify.com/captainhandsome/us-contractor-license-search) | Contractor name, license number, classification, status, state | Trades verification, subcontractor diligence |
| **US Business Entity Registries** | [`captainhandsome/us-business-entity-search`](https://apify.com/captainhandsome/us-business-entity-search) | Legal entity name, filing number, jurisdiction, status | Legal due diligence, corporate registration checks |

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
  console.log(`[${filing.ticker}] ${filing.form} (${filing.filing_date}): ${filing.primary_document_url}`);
});
```

See [examples/sec_filings.js](examples/sec_filings.js) for the full script.

---

## No-Code & Automation Workflows

If you automate via n8n, Make, Zapier, or Google Sheets, ready-to-import blueprints are included in [`workflows/`](workflows/):

- **[Google Maps Leads to Google Sheets (n8n)](workflows/n8n_google_maps_to_sheets.json):** Daily automated cron scrape piping HVAC/trade leads directly into Google Sheets with deduplication.
- **[SEC EDGAR 10-K & 8-K Alerts to Slack (n8n)](workflows/n8n_sec_edgar_to_slack.json):** Hourly monitor alerting Slack or Discord when watchlisted public companies drop new filings.

---

## Pre-Built Example Tasks (Zero Code)

If you prefer runnable web UI tasks without writing any code, each actor includes pre-configured tasks published on Apify Store:

### Google Maps Leads
- [Phoenix HVAC Company Leads](https://apify.com/captainhandsome/google-maps-business-search/tasks/phoenix-hvac-company-leads)
- [Dallas Commercial Electrician Leads](https://apify.com/captainhandsome/google-maps-business-search/tasks/dallas-commercial-electrician-leads)
- [Chicago Italian Restaurants & Reviews](https://apify.com/captainhandsome/google-maps-business-search/tasks/chicago-italian-restaurants)

### Glassdoor Jobs
- [Austin Software Engineer Jobs](https://apify.com/captainhandsome/glassdoor-jobs-scraper/tasks/austin-software-engineer-jobs)
- [Remote Product Manager Jobs](https://apify.com/captainhandsome/glassdoor-jobs-scraper/tasks/remote-product-manager-jobs)
- [New York Data Scientist Postings](https://apify.com/captainhandsome/glassdoor-jobs-scraper/tasks/new-york-data-scientist-jobs)

### Airbnb Rentals
- [Nashville Vacation Rental Listings](https://apify.com/captainhandsome/airbnb-listings-search/tasks/nashville-vacation-rentals)
- [Miami Beach Condos & Apartments](https://apify.com/captainhandsome/airbnb-listings-search/tasks/miami-beach-condos)
- [Austin Downtown Rental Market](https://apify.com/captainhandsome/airbnb-listings-search/tasks/austin-airbnb-listings)

### YouTube & Google Play
- [Small Business Marketing Videos](https://apify.com/captainhandsome/youtube-search-scraper/tasks/small-business-marketing-videos)
- [Python Web Scraping Tutorials](https://apify.com/captainhandsome/youtube-search-scraper/tasks/python-web-scraping-tutorials)
- [Instagram 1-Star Play Store Reviews](https://apify.com/captainhandsome/google-play-reviews-scraper/tasks/instagram-one-star-reviews)

---

## Free Sample Datasets

Looking for clean data to benchmark, analyze, or train models? Verified sample bundles with metadata schemas are in [`datasets/`](datasets/):

1. **[Phoenix HVAC Leads](datasets/phoenix_hvac_leads/):** 20 verified HVAC contractor profiles with ratings, addresses, and phone numbers.
2. **[California Solar Contractors](datasets/california_solar_contractors/):** Active C-46 and B licensed solar installers with state verification numbers.
3. **[Austin Software Engineer Postings](datasets/austin_software_jobs/):** Normalized job listings with estimated posting dates and salary ranges.

---

## AI Agent & MCP Integration

All actors in this repository conform to OpenAPI and JSON Schema standards, making them directly callable by AI agents via the Model Context Protocol (MCP):

### Option A: Hosted Apify MCP Server (Claude Desktop / Cursor)

Add this to your `claude_desktop_config.json` or Cursor MCP settings:

```json
{
  "mcpServers": {
    "apify": {
      "command": "npx",
      "args": ["-y", "@apify/mcp-server"],
      "env": {
        "APIFY_TOKEN": "YOUR_APIFY_API_TOKEN"
      }
    }
  }
}
```

### Option B: Local Lightweight Python MCP Server

For local agent workflows without Node.js dependencies, a direct Python MCP server is included:

```bash
export APIFY_TOKEN="your_token_here"
python mcp_server.py
```

Inspect tools and capabilities via [`mcp.json`](mcp.json).

### Agent Prompts That Work Out-of-the-Box:
- *"Search Google Maps for 50 commercial roofers in Atlanta with phone numbers and websites."*
- *"Retrieve Apple and Microsoft Form 10-K filings from SEC EDGAR for the last 2 years."*
- *"Find the 30 newest reviews for Duolingo on Google Play and analyze negative feedback."*

---

## In-Depth Engineering Guides

Technical case studies and problem-solution writeups are located in [`articles/`](articles/):

- **[Bypassing Playwright Headless Pagination Hurdles on Airbnb](articles/airbnb_playwright_pagination_guide.md):** How to solve sticky overlay modal interruptions and viewport boundary clipping in large headless browser crawls.
- **[Extracting & Normalizing Clean Job Posting Dates from Glassdoor](articles/glassdoor_posting_dates_guide.md):** Overcoming relative timestamp drift ("24h", "3d", "30d+") with deterministic parsing and ISO-8601 boundary tracking.

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
- **Issues & Requests:** Please open an issue on this repository or submit a ticket on the respective Apify Actor Store page.

---

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
