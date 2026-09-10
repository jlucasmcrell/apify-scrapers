# Reddit & Developer Community Engagement Scripts

Objective, value-first copy-paste responses for relevant technical subreddits (`r/webscraping`, `r/leadgeneration`, `r/dataengineering`, `r/SideProject`).

---

## 1. `r/webscraping`: Responding to "How to paginate dynamic sites / Airbnb without getting blocked or missing pages?"

**Thread context:** User asking why their Playwright / Puppeteer script skips pages, errors out on `click()`, or gets trapped in modals.

**Response Template:**
> Most pagination failures on single-page apps like Airbnb aren't anti-bot blocksthey are actionability viewport collisions in headless Linux.
> 
> Three things usually happen:
> 1. **Modal backdrops:** Airbnb injects translation prompts or currency dialogs that eat the synthetic click event. Inject an explicit dismissal loop (hitting `Escape` and querying `button[aria-label="Close"]`) before touching pagination.
> 2. **Outside Viewport:** Headless viewports often leave the sticky footer / pagination bar below the screen fold. Standard `.click()` times out.
> 3. **The Clean Fix:** Don't rely exclusively on `.click()`. Instead, inspect the `<a aria-label="Next">` element, extract the raw `href`, and use `page.goto(urljoin(page.url, next_href))` as a hard fallback. Direct URL navigation completely bypasses sticky headers and modal obstacles.
> 
> We open-sourced the complete Playwright fallback pattern and an architectural walkthrough here if you want to inspect the implementation: https://github.com/jlucasmcrell/apify-scrapers/blob/master/articles/airbnb_playwright_pagination_guide.md

---

## 2. `r/leadgeneration` / `r/coldemail`: Responding to "Cheapest way to get verified local business leads with phones and websites?"

**Thread context:** Users asking how to avoid paying $50+/mo for Apollo or Outscraper to get Google Maps business leads.

**Response Template:**
> If you just need clean local business lists (contractors, dentists, HVAC, restaurants) without paying recurring SaaS subscription fees, the most cost-effective path is running pay-per-result extraction directly via Apify's API.
> 
> For example, extraction runs cost fractions of a cent per lead without requiring your own proxy setup. You can even pipe them directly into Google Sheets using n8n or Make:
> - Scraper: https://apify.com/captainhandsome/google-maps-business-search
> - Pre-made n8n template to Google Sheets: https://github.com/jlucasmcrell/apify-scrapers/tree/master/workflows
> 
> The dataset exports clean business name, direct phone number, full street address, star rating, review count, website domain, and verified place URL.

---

## 3. `r/SideProject` / `r/IndieHackers`: "Built a self-healing fleet of 25+ public data scrapers with zero GPU contention"

**Thread title:** Built a 25-actor public data scraper fleet that runs for pennies and heals its own selectors

**Body Template:**
> Hey everyone, wanted to share an architecture write-up on a daemon setup I built.
> 
> **The Problem:** Scrapers are notoriously brittle. You write a Playwright parser for job boards or public registries, and within 3 weeks DOM changes break your CSS selectors, or modals break your pagination.
> 
> **The Architecture:**
> 1. **Serverless Engine:** Packaged the scrapers as Pay-Per-Event (PPE) actors on Apify ($0.0002 base event price) covering public corporate filings (SEC EDGAR), state contractor licenses, job boards (Glassdoor, LinkedIn), and local business data.
> 2. **Self-Healing Selectors:** When a selector returns empty nodes, an automated probe inspects candidate DOM attributes (data-testid, aria-labels, semantic parent anchors) and recalibrates the manifest without manual code intervention.
> 3. **AI Agent Tooling:** Wrapped all scrapers in Model Context Protocol (MCP) so Claude Desktop and Cursor can query live web datasets as local tools in JSON-RPC format.
> 
> We open-sourced the client SDK examples, MCP server, and automation templates here:
> https://github.com/jlucasmcrell/apify-scrapers
> 
> Happy to answer questions about Playwright pagination fallbacks, SEC EDGAR normalization, or Apify's Pay-Per-Event economics!
