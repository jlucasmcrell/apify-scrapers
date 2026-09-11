# Make.com (Integromat) Apify Integration Guide

This guide details how to build and deploy automated lead generation and regulatory monitoring pipelines inside **Make.com** using Apify Actors.

---

## Why Make.com?
Make.com is the standard workflow automation engine for B2B marketing agencies, SDR teams, and revenue operations professionals. It offers a visual, no-code canvas that natively connects Apify actors directly to Google Sheets, Airtable, HubSpot, Slack, and PostgreSQL.

---

## Scenario 1: Google Maps Local Business Leads to Google Sheets

### Objective:
Automatically scrape verified business names, telephone numbers, websites, review counts, and physical addresses from Google Maps and append them directly to a Google Sheet without third-party list brokers.

### Blueprint Architecture:
```
[Schedule / On-Demand Trigger]
             
             
   [Apify: Run an Actor and Get Dataset Items]
      - Actor ID: captainhandsome~google-maps-business-search
      - Input JSON:
        {
          "queries": ["HVAC Contractors, Phoenix AZ"],
          "maxItems": 50
        }
             
             
   [Google Sheets: Add a Row]
      - Spreadsheet: Your Target Lead Sheet
      - Sheet: Leads
      - Values:
          - Business Name: {{1.title}}
          - Phone: {{1.phone}}
          - Website: {{1.website}}
          - Rating: {{1.totalScore}}
          - Reviews: {{1.reviewsCount}}
          - Address: {{1.address}}
          - Maps URL: {{1.url}}
```

### 3-Step Setup:
1. In Make.com, click **Create a new scenario**.
2. Click the center **`+`**, search for **Apify**, and select **Run an Actor and Get Dataset Items**:
   - Connection: Add your Apify API Token.
   - Actor: Choose `captainhandsome/google-maps-business-search`.
   - Input: Paste target search queries and max item limits.
3. Add a second module: search for **Google Sheets**, select **Add a Row**, choose your sheet, and map the columns to the Apify dataset fields.
4. Click **Run once** to test, then set the schedule (e.g., Every Monday at 8:00 AM).

---

## Scenario 2: SEC EDGAR 10-K & 8-K Corporate Filings to Slack / Discord Alerts

### Objective:
Monitor corporate filings (10-K annual reports, 8-K material events) in real time and post immediate summary alerts to an investor or research Slack channel.

### Blueprint Architecture:
```
[Clock: Schedule Trigger (Every 4 Hours)]
             
             
   [Apify: Run an Actor and Get Dataset Items]
      - Actor ID: captainhandsome~sec-edgar-filings-search
      - Input JSON:
        {
          "tickers": ["AAPL", "MSFT", "NVDA", "TSLA"],
          "formTypes": ["10-K", "8-K"],
          "maxItems": 10
        }
             
             
   [Slack / Discord: Create a Message]
      - Message Content:
          " New SEC {{1.formType}} Filing: *{{1.companyName}}* ({{1.ticker}})
          Filed Date: {{1.filingDate}}
          Document: {{1.filingUrl}}"
```

---

## Scenario 3: Universal HTTP Webhook Execution (Zero-Module Dependency)

If you prefer not to use the pre-built Apify Make module, you can trigger any of the 30 Apify actors using Make's native **HTTP** module:

- **Module:** `HTTP > Make a request`
- **URL:** `https://api.apify.com/v2/acts/captainhandsome~ACTOR_NAME/run-sync-get-dataset-items?token=YOUR_APIFY_TOKEN`
- **Method:** `POST`
- **Headers:**
  - `Content-Type`: `application/json`
- **Body:** Raw JSON input payload.
- **Parse response:** `Yes`
