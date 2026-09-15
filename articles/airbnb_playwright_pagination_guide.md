---
title: How to Bypass Headless Pagination and Translation Modals on Airbnb with Playwright
published: true
tags: webscraping, python, playwright, automation
canonical_url: https://apify.revenuesystemslabs.com/articles/airbnb_playwright_pagination_guide.html
---

When scraping modern Single Page Applications (SPAs) like Airbnb, standard pagination strategies (`page.click('a[aria-label="Next"]')`) frequently collapse in headless Linux environments (Xvfb / Docker). 

Even if your selectors look completely sound in Chrome DevTools, Playwright will throw errors like:
```text
playwright._impl._errors.TimeoutError: element is outside of the viewport
```
or fail silently when unexpected modal backdrops (translation dialogs, privacy notices, currency popups) intercept user interaction events.

Here is the multi-layered defensive pattern we engineered to reliably paginate through dozens of search pages in production.

---

## The Root Causes

1. **Sticky Footers and Responsive Viewports:** In headless browsers with constrained resolutions, the pagination bar at the bottom of the grid is often overlaid or pushed outside the actionability bounding box.
2. **Translation & Currency Modals:** Airbnb periodically pops a *"Translate reviews and descriptions to English"* or *"Choose currency"* overlay. In headless mode, this modal consumes all click events.
3. **Synthetic Event Shielding:** Clicking the `<a>` tag with standard browser synthetic events doesn't always trigger the Next.js router change if the viewport isn't focused.

---

## Pattern 1: Active Modal Dismissal

Before attempting pagination or scrolling, run an aggressive dismissal loop that catches close buttons, cookie banners, and presses the `Escape` key:

```python
async def dismiss_modals(page):
    selectors = [
        'button[aria-label="Close"]',
        'button[aria-label="Dismiss"]',
        '#onetrust-accept-btn-handler',
        'div[data-testid="modal-container"] button',
    ]
    for sel in selectors:
        try:
            btn = page.locator(sel).first
            if await btn.is_visible():
                await btn.click(timeout=1000)
                await page.wait_for_timeout(300)
        except Exception:
            pass
    try:
        await page.keyboard.press("Escape")
    except Exception:
        pass
```

---

## Pattern 2: Multi-Tiered Pagination Fallback

Instead of relying solely on `.click()`, use a three-tier fallback mechanism:

```python
from urllib.parse import urljoin

async def advance_to_next_page(page):
    await dismiss_modals(page)

    next_btn = page.locator('a[aria-label="Next"]').first
    if not await next_btn.is_visible():
        return False

    # Tier 1: Extract href for direct URL navigation fallback
    next_href = await next_btn.get_attribute("href")

    # Tier 2: Scroll into view and standard click
    try:
        await next_btn.scroll_into_view_if_needed(timeout=2000)
        await next_btn.click(timeout=3000)
        await page.wait_for_load_state("networkidle", timeout=8000)
        return True
    except Exception:
        pass

    # Tier 3: JavaScript evaluate click
    try:
        await next_btn.evaluate("el => el.click()")
        await page.wait_for_load_state("networkidle", timeout=8000)
        return True
    except Exception:
        pass

    # Tier 4: Direct URL navigation fallback (Immune to DOM/viewport obstacles)
    if next_href:
        target_url = urljoin(page.url, next_href)
        await page.goto(target_url, wait_until="networkidle", timeout=15000)
        return True

    return False
```

If modals intercept the click, or sticky footers keep the link outside the headless viewport, **Tier 4 (direct URL navigation fallback)** completely bypasses the DOM layer and forces the browser to load the paginated state directly.

---

## Production Cloud Implementation

If you don't want to maintain headless Playwright clusters, rotating residential proxies, and DOM selector manifests yourself, this entire logic is packaged and maintained as a serverless actor on Apify:

- **Actor:** [captainhandsome/airbnb-listings-search](https://apify.com/captainhandsome/airbnb-listings-search)
- **Open-Source Examples:** [jlucasmcrell/apify-scrapers on GitHub](https://github.com/jlucasmcrell/apify-scrapers)

You can run it programmatically via Python in 4 lines:

```python
from apify_client import ApifyClient

client = ApifyClient("YOUR_APIFY_TOKEN")
run = client.actor("captainhandsome/airbnb-listings-search").call(run_input={
    "location": "Austin, TX",
    "max_items": 50
})

listings = list(client.dataset(run["defaultDatasetId"]).iterate_items())
print(f"Extracted {len(listings)} listings reliably.")
```
