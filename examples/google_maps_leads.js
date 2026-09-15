/**
 * Extract Google Maps business leads using Apify Client for JavaScript.
 *
 * Installation:
 *   npm install apify-client
 *
 * Usage:
 *   export APIFY_TOKEN="your_apify_api_token"
 *   node google_maps_leads.js
 */

import { ApifyClient } from 'apify-client';

const token = process.env.APIFY_TOKEN;
if (!token) {
  console.error('Error: APIFY_TOKEN environment variable not set.');
  process.exit(1);
}

const client = new ApifyClient({ token });

async function main() {
  console.log('Calling captainhandsome/google-maps-business-search...');
  
  const run = await client.actor('captainhandsome/google-maps-business-search').call({
    search_query: 'commercial electricians',
    location: 'Dallas, Texas',
    max_items: 20,
    include_details: true,
  });

  if (!run || run.status !== 'SUCCEEDED') throw new Error('Actor run did not succeed');
  console.log(`Run finished with status: ${run.status}`);
  const items = [];
  for (let offset = 0; ; offset += 1000) {
    const page = await client.dataset(run.defaultDatasetId).listItems({ offset, limit: 1000 });
    items.push(...page.items);
    if (page.items.length < 1000) break;
  }
  
  console.log(`Retrieved ${items.length} records:`);
  items.slice(0, 5).forEach((lead, i) => {
    console.log(`${i + 1}. ${lead.name} | Phone: ${lead.phone || 'N/A'} | Rating: ${lead.rating} (${lead.reviews_count} reviews) | Web: ${lead.website || 'N/A'}`);
  });
}

main().catch((error) => { console.error(error.message); process.exitCode = 1; });
