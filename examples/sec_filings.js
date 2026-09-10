/**
 * Extract SEC EDGAR filings metadata using Apify Client for JavaScript.
 *
 * Installation:
 *   npm install apify-client
 *
 * Usage:
 *   export APIFY_TOKEN="your_apify_api_token"
 *   node sec_filings.js
 */

import { ApifyClient } from 'apify-client';

const token = process.env.APIFY_TOKEN;
if (!token) {
  console.error('Error: APIFY_TOKEN environment variable not set.');
  process.exit(1);
}

const client = new ApifyClient({ token });

async function main() {
  console.log('Querying captainhandsome/sec-edgar-filings-search...');
  
  const run = await client.actor('captainhandsome/sec-edgar-filings-search').call({
    companies: ['AAPL', 'MSFT', 'NVDA'],
    forms: ['10-K'],
    max_items: 15,
  });

  console.log(`Run finished with status: ${run.status}`);
  const { items } = await client.dataset(run.defaultDatasetId).listItems();
  
  console.log(`Retrieved ${items.length} SEC filings:`);
  items.slice(0, 5).forEach((filing, i) => {
    console.log(`${i + 1}. [${filing.ticker}] ${filing.form} (${filing.filing_date}) - Doc: ${filing.primary_document_url}`);
  });
}

main().catch(console.error);
