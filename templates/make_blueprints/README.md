# Make.com (Integromat) Apify Integration Blueprints

Make.com scenario blueprints for sending Apify Actor results to Google Sheets or a Slack incoming webhook. Configure connections, inputs, and destinations before running. Apify and Make usage charges may apply.

---

## Ready-to-Import Blueprints in This Folder

| Scenario | Public Make Template | Blueprint File | Description |
| :--- | :--- | :--- | :--- |
| **Google Maps Local Leads** | Gallery approval pending | [`google_maps_leads_to_sheets_blueprint.json`](./google_maps_leads_to_sheets_blueprint.json) | Scrapes commercial businesses, phones, addresses, ratings directly to Google Sheets. |
| **Google News Results** | Gallery approval pending | [`google_news_to_sheets_blueprint.json`](./google_news_to_sheets_blueprint.json) | Exports headlines, publishers, timestamps, article links, and snippets into Sheets. |
| **Grants.gov Opportunities** | Gallery approval pending | [`grants_gov_to_sheets_blueprint.json`](./grants_gov_to_sheets_blueprint.json) | Exports federal funding opportunities, deadlines, award amounts, contacts, and links. |
| **TED EU Tenders** | Gallery approval pending | [`ted_eu_tenders_to_sheets_blueprint.json`](./ted_eu_tenders_to_sheets_blueprint.json) | Exports European procurement notices, buyers, deadlines, values, and source documents. |
| **NHTSA Vehicle Recalls** | Gallery approval pending | [`nhtsa_recalls_to_sheets_blueprint.json`](./nhtsa_recalls_to_sheets_blueprint.json) | Exports official vehicle recall campaigns, defects, warnings, affected units, and remedies. |
| **SEC EDGAR 10-K & 8-K Filings** | Gallery approval pending | [`sec_edgar_to_slack_blueprint.json`](./sec_edgar_to_slack_blueprint.json) | Sends retrieved SEC filing records to a Slack incoming webhook when run. |
| **California Contractor Licenses** | Gallery approval pending | [`california_contractors_to_sheets_blueprint.json`](./california_contractors_to_sheets_blueprint.json) | Extracts verified state contractor licenses, bond statuses, and corporate entities into Sheets. |
| **Glassdoor Active Job Postings** | Gallery approval pending | [`glassdoor_jobs_to_sheets_blueprint.json`](./glassdoor_jobs_to_sheets_blueprint.json) | Tracks tech hiring, salary estimates, and company ratings into a live spreadsheet. |

Make gallery approval is pending. Download the blueprint files below to configure a scenario yourself; public gallery links are not yet verified.

---

## How to Import a Blueprint Into Make.com

1. Open your [Make.com Dashboard](https://make.com) and click **Create a new scenario**.
2. On the bottom canvas toolbar, click the **`...` (More)** menu icon.
3. Click **`Import Blueprint`** and upload any of the `.json` files from this directory.
4. The complete scenario appears on your canvas with all modules and field mappings pre-wired.
5. Click **Module 1 (Apify)** to select your Apify API Token.
6. Configure Module 2 with the same Apify connection.
7. In Google Sheets, select your connection, spreadsheet, and tab. Match the headers to the mapped fields. Use **Raw** input and **Insert rows**. For SEC, configure your own Slack incoming webhook URL.
8. Review the Actor input and expected usage cost, then click **Run once** to test.

### SEC duplicate prevention

Before running the SEC blueprint, create a Make data store with a `sent_at` field of type **Date**. Select that same store in both Data store modules (4 and 5). Use a separate store for each independently notified Slack destination. The store and its history are not included in a blueprint import.

The workflow checks each filing's `accession_number`, skips recorded filings, and saves a receipt only after Slack succeeds. Keep **Sequential processing** enabled and HTTP error handling enabled. Do not run multiple scenario copies against the same store concurrently. Failed deliveries remain eligible for retry.

The first run sends the matching filings it finds, including older filings. History persists until you remove records or change stores; a full store requires attention. This is not an exactly-once guarantee: a timeout or interruption after Slack accepts a message but before the receipt is saved can still cause a repeat. Check Slack before manually replaying an ambiguous failure.

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
