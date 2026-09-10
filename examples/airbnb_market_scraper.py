"""Extract vacation rental listings, prices, ratings, and coordinates from Airbnb.

Requirements:
    pip install apify-client pandas python-dotenv

Usage:
    export APIFY_TOKEN="your_apify_api_token"
    python airbnb_market_scraper.py
"""

import os
import sys
from dotenv import load_dotenv
from apify_client import ApifyClient
import pandas as pd

load_dotenv()

TOKEN = os.getenv("APIFY_TOKEN")
if not TOKEN:
    print("Error: APIFY_TOKEN environment variable not set.")
    sys.exit(1)

ACTOR_ID = "captainhandsome/airbnb-listings-search"

def scrape_airbnb_market(location: str, max_items: int = 50, output_csv: str = "airbnb_listings.csv"):
    print(f"[*] Extracting Airbnb listings for '{location}' (limit: {max_items})...")
    client = ApifyClient(TOKEN)
    
    run = client.actor(ACTOR_ID).call(run_input={
        "location": location,
        "max_items": max_items,
    })
    
    if not run or run.get("status") != "SUCCEEDED":
        print(f"[!] Run ended with status: {run.get('status')}")
        return None

    dataset_id = run["defaultDatasetId"]
    items = list(client.dataset(dataset_id).iterate_items())
    if not items:
        print("[!] No listings returned.")
        return None

    df = pd.DataFrame(items)
    df.to_csv(output_csv, index=False, encoding="utf-8")
    print(f"[+] Exported {len(df)} listings to {output_csv}")
    
    summary_cols = [c for c in ["title", "room_type", "price", "rating", "reviews_count", "url"] if c in df.columns]
    print(df[summary_cols].head())
    return df

if __name__ == "__main__":
    scrape_airbnb_market(
        location="Nashville, Tennessee",
        max_items=30,
        output_csv="nashville_airbnb.csv"
    )
