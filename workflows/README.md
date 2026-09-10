# Production Workflow Automation Templates (n8n, Make, Zapier)

Ready-to-import visual workflow templates for automating lead extraction, filing alerts, and market intelligence using Apify actors.

---

## 1. Google Maps Leads to Google Sheets (`n8n_google_maps_to_sheets.json`)

Automatically extract business leads (name, phone number, physical address, star rating, total reviews, website domain, and Google Maps URL) on a recurring schedule and append them directly to a Google Sheet.

### How to Import & Run in n8n:
1. Open your n8n workspace (self-hosted or n8n Cloud).
2. Click **Add Workflow** -> **Import from File...** (or copy-paste the JSON).
3. Select `workflows/n8n_google_maps_to_sheets.json`.
4. Configure credentials:
   - **Apify API:** In the HTTP Request node, add your Apify token as header `Authorization: Bearer YOUR_APIFY_TOKEN`.
   - **Google Sheets:** Authenticate your Google OAuth or Service Account in the Google Sheets node, and paste your target `Document ID` and `Sheet Name`.
5. Run the workflow or activate the weekly trigger.

- **Underlying Actor:** [captainhandsome/google-maps-business-search](https://apify.com/captainhandsome/google-maps-business-search)
- **Preconfigured Public Task:** [captainhandsome/phoenix-hvac-company-leads](https://apify.com/captainhandsome/phoenix-hvac-company-leads)

---

## 2. Real-Time SEC EDGAR Filing Alerts (`n8n_sec_edgar_to_slack.json`)

Monitor corporate disclosures (10-K annual reports, 10-Q quarterly reports, and 8-K unscheduled material events) across target tickers (e.g. `AAPL`, `NVDA`, `TSLA`, `MSFT`) and post formatted notifications to a Slack or Discord webhook.

### How to Import & Run in n8n:
1. Open n8n, click **Import from File...**, and select `workflows/n8n_sec_edgar_to_slack.json`.
2. Configure credentials:
   - Add your Apify API Token in header `Authorization: Bearer YOUR_APIFY_TOKEN`.
   - Replace `YOUR_SLACK_OR_DISCORD_WEBHOOK_URL` with your Slack Incoming Webhook or Discord channel webhook URL.
3. Activate the trigger (runs every 4 hours or customizable).

- **Underlying Actor:** [captainhandsome/sec-edgar-filings-search](https://apify.com/captainhandsome/sec-edgar-filings-search)
- **Preconfigured Public Task:** [captainhandsome/apple-microsoft-recent-10k](https://apify.com/captainhandsome/apple-microsoft-recent-10k)

---

## 3. Zapier & Make.com Webhook Quick Recipe

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
