# Production Workflow Automation Templates (n8n, Make, Zapier)

Ready-to-import visual workflow templates for automating lead extraction, filing alerts, and market intelligence using Apify actors.

---

## 1. Google Maps Leads to Google Sheets (`n8n_google_maps_to_sheets.json`)

Automatically extract business leads (name, phone number, physical address, star rating, total reviews, website domain, and Google Maps URL) on a recurring schedule, suppress previously seen place IDs, and append new leads to a Google Sheet.

### How to Import & Run in n8n:
1. Open your n8n workspace (self-hosted or n8n Cloud).
2. Click **Add Workflow** -> **Import from File...** (or copy-paste the JSON).
3. Select `workflows/n8n_google_maps_to_sheets.json`.
4. Configure credentials:
   - **Apify API:** In the HTTP Request node, add your Apify token as header `Authorization: Bearer YOUR_APIFY_TOKEN`.
   - **Google Sheets:** Authenticate your Google OAuth or Service Account in the Google Sheets node, and paste your target `Document ID` and `Sheet Name`.
5. Run the workflow or activate the weekly trigger.

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

## 6. Zapier & Make.com Webhook Quick Recipe

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
