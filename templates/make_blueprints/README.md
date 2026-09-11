# Make.com (Integromat) Apify Integration Blueprints

Pre-built, 1-click **Make.com scenario blueprints** that connect production Apify actors to Google Sheets, CRMs, Slack, and webhooks with zero custom code.

---

## Ready-to-Import Blueprints in This Folder

| Scenario | Blueprint File | Description |
| :--- | :--- | :--- |
| **Google Maps Local Leads** | [`google_maps_leads_to_sheets_blueprint.json`](./google_maps_leads_to_sheets_blueprint.json) | Scrapes commercial businesses, phones, addresses, ratings directly to Google Sheets. |
| **SEC EDGAR 10-K & 8-K Filings** | [`sec_edgar_to_slack_blueprint.json`](./sec_edgar_to_slack_blueprint.json) | Real-time regulatory disclosure monitor pushing alerts directly to Slack/Discord/Webhook. |
| **California Contractor Licenses** | [`california_contractors_to_sheets_blueprint.json`](./california_contractors_to_sheets_blueprint.json) | Extracts verified state contractor licenses, bond statuses, and corporate entities into Sheets. |
| **Glassdoor Active Job Postings** | [`glassdoor_jobs_to_sheets_blueprint.json`](./glassdoor_jobs_to_sheets_blueprint.json) | Tracks tech hiring, salary estimates, and company ratings into a live spreadsheet. |

---

## How to Import a Blueprint Into Make.com (60 Seconds)

1. Open your [Make.com Dashboard](https://make.com) and click **Create a new scenario**.
2. On the bottom canvas toolbar, click the **`...` (More)** menu icon.
3. Click **`Import Blueprint`** and upload any of the `.json` files from this directory.
4. The complete scenario appears on your canvas with all modules and field mappings pre-wired.
5. Click **Module 1 (Apify)** to select your Apify API Token.
6. Click the destination module (Google Sheets or Slack) to authorize your account.
7. Click **Run once** to test.

---

## Native Apify Mapping Architecture (The Dataset ID Pattern)

When chaining Make's official **Apify: Run an Actor** and **Apify: Get Dataset Items** modules:

- In Module 2 (*Get Dataset Items*), map the **Dataset ID** using:
  ```text
  {{1.data.options.defaultDatasetId}}
  ```
  *(or `{{1.defaultDatasetId}}` depending on synchronous execution mode).*

- In the destination module (e.g. Google Sheets), dataset records are accessed directly via the clean output schema:
  - `{{2.title}}` or `{{2.name}}`
  - `{{2.phone}}`
  - `{{2.website}}`
  - `{{2.address}}`
  - `{{2.totalScore}}` or `{{2.rating}}`
