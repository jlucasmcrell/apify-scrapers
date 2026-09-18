---
layout: default
title: "n8n workflow templates"
permalink: /workflows/
description: "Six importable n8n workflows that run Apify public-data Actors on a schedule and write rows to Sheets or Slack."
---

# Production Workflow Automation Templates (n8n, Make, Zapier)

Ready-to-import visual workflow templates for automating lead extraction, filing alerts, and market intelligence using Apify actors.

> **Upgraded 2026-09-18.** The first version of these templates was rejected by the n8n template
> library as "too basic" (4 nodes, no in-canvas documentation, no branching, no error handling).
> They have been rebuilt to the bar measured from 27 published templates in the same categories:
> median **10 distinct node types**, and **100% of them carry a sticky note** on the canvas.
>
> Each template now ships with a documentation note, a single **Configure search** node (the one
> place to edit), an explicit **Any records returned?** branch, a **Drop rows with no identifier**
> guard, retry on the Apify call, and a failure branch that alerts instead of ending silently.
> Persistent duplicate suppression is unchanged — it was already correct.
>
> **Verified, not assumed:** every file imports into a real n8n instance (`n8n import:workflow`)
> and executes. Running the graph in n8n resolves every node type and, with no credential present,
> takes the failure branch to **Alert on failure** exactly as designed.
>
> Submit in this order — measured competition in the n8n library, same day: `grants.gov` **0**
> competing templates, `nhtsa recall` **1**, `sec edgar` **2**, versus `apify google sheets` **226**
> and `google maps leads` **50**. The empty categories are the ones that get found.

---

## 1. Google Maps Leads to Google Sheets (`n8n_google_maps_to_sheets.json`)

Automatically extract business leads (name, phone number, physical address, star rating, total reviews, website domain, and Google Maps URL) on a recurring schedule, suppress previously seen place IDs, and append new leads to a Google Sheet.

### How to Import & Run in n8n:
1. Open your n8n workspace (self-hosted or n8n Cloud).
2. Click **Add Workflow** -> **Import from File...** (or copy-paste the JSON).
3. Select `workflows/n8n_google_maps_to_sheets.json`.
4. Open **Configure search** and set `search_query` (plus `max_items` if you want a different ceiling) — that is the only node you need to edit.
5. Configure credentials:
   - **Apify API:** create a Header Auth credential named `Apify` with header name `Authorization` and value `Bearer YOUR_APIFY_TOKEN` (Apify Console -> Settings -> Integrations).
   - **Google Sheets:** authenticate your Google OAuth or Service Account in the Google Sheets node, and paste your target `Document ID` and `Sheet Name`.
6. Run the workflow or activate the weekly trigger.

- **Underlying Actor:** [captainhandsome/google-maps-business-search](https://apify.com/captainhandsome/google-maps-business-search)
- **Preconfigured Public Task:** [Find HVAC Company Leads in Phoenix](https://apify.com/captainhandsome/google-maps-business-search/examples/phoenix-hvac-company-leads)

---

## 2. Real-Time SEC EDGAR Filing Alerts (`n8n_sec_edgar_to_slack.json`)

Monitor corporate disclosures (10-K annual reports, 10-Q quarterly reports, and 8-K unscheduled material events) across target tickers (e.g. `AAPL`, `NVDA`, `TSLA`, `MSFT`), suppress previously seen accession numbers, and post new filings to a Slack or Discord webhook.

### How to Import & Run in n8n:
1. Open n8n, click **Import from File...**, and select `workflows/n8n_sec_edgar_to_slack.json`.
2. Configure credentials:
   - Add your Apify API Token in header `Authorization: Bearer YOUR_APIFY_TOKEN`.
   - Replace `YOUR_SLACK_OR_DISCORD_WEBHOOK_URL` with your Slack Incoming Webhook or Discord channel webhook URL.
3. Activate the trigger (runs every 4 hours or customizable).

- **Underlying Actor:** [captainhandsome/sec-edgar-filings-search](https://apify.com/captainhandsome/sec-edgar-filings-search)
- **Preconfigured Public Task:** [Apple and Microsoft Recent 10-K Filings](https://apify.com/captainhandsome/sec-edgar-filings-search/examples/apple-microsoft-10k-filings)

---

## 3. Daily Competitor News Alerts

Import n8n_google_news_competitor_monitor.json to monitor Google News every 24 hours, retain up to 1,000 previously seen article URLs in n8n workflow data, and send only new coverage to Slack or Discord.

Configure an Apify HTTP Header Auth credential and replace YOUR_SLACK_OR_DISCORD_WEBHOOK_URL. Edit the example OpenAI OR Anthropic query for your own brands.

- **Underlying Actor:** [captainhandsome/google-news-search](https://apify.com/captainhandsome/google-news-search)
- **Preconfigured Public Task:** [Monitor Competitor Brand News](https://apify.com/captainhandsome/google-news-search/examples/competitor-brand-news-monitor)

---

## 4. Daily Grants.gov Opportunity Alerts

Import n8n_grants_gov_opportunity_monitor.json to search posted Grants.gov opportunities every 24 hours, suppress previously seen opportunity numbers, and send new funding links to Slack or Discord.

Configure an Apify HTTP Header Auth credential and replace YOUR_SLACK_OR_DISCORD_WEBHOOK_URL. Edit the example small-business innovation query for your target program.

- **Underlying Actor:** [captainhandsome/grants-gov-opportunity-search](https://apify.com/captainhandsome/grants-gov-opportunity-search)
- **Preconfigured Public Task:** [Find Open Small Business Innovation Grants](https://apify.com/captainhandsome/grants-gov-opportunity-search/examples/open-small-business-innovation-grants)

---

## 5. Daily TED European Tender Alerts

Import n8n_ted_eu_tender_monitor.json to search official TED procurement notices every 24 hours, suppress previously seen publication numbers, and send new tender links to Slack or Discord.

Configure an Apify HTTP Header Auth credential and replace YOUR_SLACK_OR_DISCORD_WEBHOOK_URL. Edit the example renewable-energy query for your target market.

- **Underlying Actor:** [captainhandsome/ted-eu-tender-search](https://apify.com/captainhandsome/ted-eu-tender-search)
- **Preconfigured Public Task:** [Find European Renewable Energy Tenders](https://apify.com/captainhandsome/ted-eu-tender-search/examples/european-renewable-energy-tenders)

---

## 6. Daily NHTSA Vehicle Recall Alerts

Import `n8n_nhtsa_vehicle_recall_monitor.json` to check a year, make, and model every 24 hours, retain up to 2,000 previously seen campaign-and-vehicle combinations, and send only newly observed recalls to Slack or Discord.

Configure an Apify HTTP Header Auth credential and replace `YOUR_SLACK_OR_DISCORD_WEBHOOK_URL`. Edit the example 2020 Honda Civic input for the vehicle or fleet you want to monitor.

- **Underlying Actor:** [captainhandsome/nhtsa-vehicle-recall-search](https://apify.com/captainhandsome/nhtsa-vehicle-recall-search)
- **Preconfigured Public Task:** [Check 2020 Honda Civic Safety Recalls](https://apify.com/captainhandsome/nhtsa-vehicle-recall-search/examples/2020-honda-civic-recalls)

---

## 7. Zapier & Make.com Webhook Quick Recipe

If you are using **Zapier** or **Make.com** instead of n8n:

1. **Create Webhook Trigger:** In Zapier/Make, create a **Catch Hook** or **Custom Webhook** trigger module. Copy the webhook URL.
2. **Attach to Apify Actor:**
   - In Apify Console, go to your Actor or Task (e.g. `captainhandsome/google-maps-business-search`).
   - Click the **Integrations** tab -> **Webhooks**.
   - Select event: `Run succeeded` (`ACTOR.RUN.SUCCEEDED`).
   - Paste your Zapier/Make webhook URL.
3. **Handle Payload:**
   - When the scraper finishes, Apify posts the run payload to your webhook with `resource.defaultDatasetId`.
   - In Zapier/Make, add an HTTP GET step to `https://api.apify.com/v2/datasets/{{defaultDatasetId}}/items?clean=true&format=json`.
   - Map the resulting items directly into HubSpot, Salesforce, Airtable, or Notion.
