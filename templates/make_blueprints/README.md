# Make.com (Integromat) Apify Integration Blueprints

Pre-built, 1-click **Make.com scenario blueprints** that connect production Apify actors to Google Sheets, CRMs, Slack, and webhooks with zero custom code.

---

## Ready-to-Import Blueprints in This Folder

| Scenario | Public Make Template | Blueprint File | Description |
| :--- | :--- | :--- | :--- |
| **Google Maps Local Leads** | [Use template](https://www.make.com/en/templates/19727-google-maps-leads-to-google-sheets-with-apify) | [`google_maps_leads_to_sheets_blueprint.json`](./google_maps_leads_to_sheets_blueprint.json) | Scrapes commercial businesses, phones, addresses, ratings directly to Google Sheets. |
| **Google News Results** | [Use template](https://www.make.com/en/templates/19731-export-google-news-results-to-google-sheets-with-apify) | [`google_news_to_sheets_blueprint.json`](./google_news_to_sheets_blueprint.json) | Exports headlines, publishers, timestamps, article links, and snippets into Sheets. |
| **Grants.gov Opportunities** | [Use template](https://www.make.com/en/templates/19732-export-grants-gov-opportunities-to-google-sheets-with-apify) | [`grants_gov_to_sheets_blueprint.json`](./grants_gov_to_sheets_blueprint.json) | Exports federal funding opportunities, deadlines, award amounts, contacts, and links. |
| **TED EU Tenders** | [Use template](https://www.make.com/en/templates/19733-export-ted-eu-tenders-to-google-sheets-with-apify) | [`ted_eu_tenders_to_sheets_blueprint.json`](./ted_eu_tenders_to_sheets_blueprint.json) | Exports European procurement notices, buyers, deadlines, values, and source documents. |
| **NHTSA Vehicle Recalls** | [Use template](https://www.make.com/en/templates/19734-export-nhtsa-vehicle-recalls-to-google-sheets-with-apify) | [`nhtsa_recalls_to_sheets_blueprint.json`](./nhtsa_recalls_to_sheets_blueprint.json) | Exports official vehicle recall campaigns, defects, warnings, affected units, and remedies. |
| **SEC EDGAR 10-K & 8-K Filings** | [Use template](https://www.make.com/en/templates/19730-sec-edgar-filing-alerts-to-slack-with-apify) | [`sec_edgar_to_slack_blueprint.json`](./sec_edgar_to_slack_blueprint.json) | Real-time regulatory disclosure monitor pushing alerts directly to Slack/Discord/Webhook. |
| **California Contractor Licenses** | [Use template](https://www.make.com/en/templates/19729-california-contractor-licenses-to-google-sheets-with-apify) | [`california_contractors_to_sheets_blueprint.json`](./california_contractors_to_sheets_blueprint.json) | Extracts verified state contractor licenses, bond statuses, and corporate entities into Sheets. |
| **Glassdoor Active Job Postings** | [Use template](https://www.make.com/en/templates/19728-glassdoor-jobs-to-google-sheets-with-apify) | [`glassdoor_jobs_to_sheets_blueprint.json`](./glassdoor_jobs_to_sheets_blueprint.json) | Tracks tech hiring, salary estimates, and company ratings into a live spreadsheet. |

The public templates are usable by direct link. Make gallery approval is pending.

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

- In Module 2 (*Get Dataset Items*), map the **Dataset ID** directly to the root bundle property:
  ```text
  {{1.defaultDatasetId}}
  ```
  *(Note: Map the top-level `1. defaultDatasetId`, NOT the nested options dictionary under `data.options`).*

- In the destination module (e.g. Google Sheets), dataset records are accessed directly via the clean output schema:
  - `{{2.title}}` or `{{2.name}}`
  - `{{2.phone}}`
  - `{{2.website}}`
  - `{{2.address}}`
  - `{{2.totalScore}}` or `{{2.rating}}`
