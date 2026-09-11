# 1-Click Google Sheets Lead Extractor (No-Code Marketer Guide)

Automated B2B lead generation directly inside Google Sheets using the Apify API.

No Python, no Docker, and no server configuration needed. Perfect for sales teams, cold outreach agencies, and growth marketers.

---

## Method 1: The Instant 1-Formula Approach (Easiest)

If you have already executed a run on Apify Store (or want to pull an active public task), you can pull live leads into Google Sheets with **one formula**:

```excel
=IMPORTDATA("https://api.apify.com/v2/datasets/DATASET_ID/items?format=csv&token=YOUR_APIFY_TOKEN")
```

### How to use it:
1. Open a blank [Google Sheet](https://sheets.new).
2. Replace `DATASET_ID` with the dataset ID from your Actor run.
3. Replace `YOUR_APIFY_TOKEN` with your personal token from [Apify Console](https://console.apify.com/account#/integrations).
4. Hit **Enter**. Google Sheets will parse the CSV and populate the columns (`Business Name`, `Phone`, `Website`, `Rating`, `Address`).

---

## Method 2: The "Interactive Lead Machine" Menu (1-Click Fresh Searches)

This method adds a native **"Lead Machine"** menu bar directly inside your Google Sheet. You type a niche (e.g. `Roofing Contractors`) and city (e.g. `Denver, CO`), click **Fetch Fresh Leads**, and the sheet calls Apify and fills rows automatically.

### 2-Minute Setup:

#### Step 1: Create the Sheets Layout
1. Open a new Google Sheet and name it **Lead Extractor Template**.
2. Create two tabs at the bottom:
   - **Settings**
   - **Leads**

In the **Settings** tab, set up this simple key-value table:

| Cell | Label / Value | Description |
| :--- | :--- | :--- |
| **A1** | `Apify API Token` | Label |
| **B1** | `YOUR_APIFY_TOKEN` | Paste your token from [Apify Settings](https://console.apify.com/account#/integrations) |
| **A2** | `Search Term` | Label |
| **B2** | `HVAC Contractors` | Any industry or business category |
| **A3** | `Location` | Label |
| **B3** | `Phoenix, AZ` | Any city, state, or postal code |
| **A4** | `Max Results` | Label |
| **B4** | `50` | Number of leads to extract (e.g. 25, 50, 100) |

#### Step 2: Paste the Apps Script
1. In Google Sheets, click **Extensions > Apps Script**.
2. Delete any code in the editor (`function myFunction() { ... }`).
3. Open `google_apps_script_enricher.js` from this folder, copy all code, and paste it into the editor.
4. Click the **Save** disk icon.

#### Step 3: Run Your First Search
1. Return to your Google Sheet and refresh the browser page.
2. A new menu named **Lead Machine** will appear next to *Help*.
3. Click **Lead Machine > Fetch Fresh Leads**.
4. (First time only) Google will prompt: *"Authorization Required"*. Click **Continue**, choose your Google account, click **Advanced**, and click **Go to Untitled script (unsafe)** -> **Allow**. (This is standard Google security when a sheet makes external HTTP web requests).
5. The sheet will query Apify synchronously, extract fresh business profiles, and write them into the **Leads** tab.

---

## Method 3: Clay.com Webhook Integration (For Outbound Agencies)

If you use **Clay** for cold outreach:

1. Add a new column in your Clay table: **Enrich via HTTP API**.
2. Set Method to `POST`.
3. Set URL to:
   ```text
   https://api.apify.com/v2/acts/captainhandsome~googlemaps/run-sync-get-dataset-items?token=YOUR_APIFY_TOKEN
   ```
4. Set Headers:
   - `Content-Type`: `application/json`
5. Set Body:
   ```json
   {
     "searchQueries": ["{{Domain}} in {{City}}"],
     "maxResultsPerQuery": 1
   }
   ```
6. Map the returned JSON fields (`phone`, `rating`, `reviewsCount`, `address`) directly to your Clay columns.

---

## Recommended Live Tools on Apify Store

- **Google Maps Local Business Leads:** [`captainhandsome/googlemaps`](https://apify.com/captainhandsome/googlemaps)
- **Glassdoor Jobs & Hiring Intelligence:** [`captainhandsome/glassdoor-jobs-scraper`](https://apify.com/captainhandsome/glassdoor-jobs-scraper)
- **California Contractor License Search:** [`captainhandsome/california-contractors-license-search`](https://apify.com/captainhandsome/california-contractors-license-search)
- **Airbnb Rental Listings & Pricing:** [`captainhandsome/airbnb-scraper`](https://apify.com/captainhandsome/airbnb-scraper)
