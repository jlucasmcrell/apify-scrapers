"""Export Google Maps business leads to a clean CSV file using Apify.

Requirements:
    pip install apify-client pandas python-dotenv

Usage:
    export APIFY_TOKEN="your_apify_api_token"
    python google_maps_leads_to_csv.py
"""

import os
import sys
from pathlib import Path
from dotenv import load_dotenv
from apify_client import ApifyClient
import pandas as pd

load_dotenv()

TOKEN = os.getenv("APIFY_TOKEN")
if not TOKEN:
    print("Error: APIFY_TOKEN environment variable not set.")
    print("Sign up at https://apify.com and copy your API token from Account Settings > Integrations.")
    sys.exit(1)

ACTOR_ID = "captainhandsome/google-maps-business-search"

def extract_google_maps_leads(query: str, location: str, max_items: int = 50, output_csv: str = "leads.csv"):
    print(f"[*] Calling {ACTOR_ID} for query='{query}' in '{location}' (limit: {max_items})...")
    client = ApifyClient(TOKEN)
    
    run = client.actor(ACTOR_ID).call(run_input={
        "search_query": query,
        "location": location,
        "max_items": max_items,
        "include_details": True,
    })
    
    if not run or run.get("status") != "SUCCEEDED":
        print(f"[!] Run failed or was aborted: {run}")
        return None

    dataset_id = run["defaultDatasetId"]
    print(f"[*] Run SUCCEEDED. Fetching records from dataset {dataset_id}...")
    
    items = list(client.dataset(dataset_id).iterate_items())
    if not items:
        print("[!] No records returned.")
        return None

    df = pd.DataFrame(items)
    # Reorder display columns if present
    preferred_cols = [
        "name", "category", "phone", "website", "rating", "review_count",
        "full_address", "city", "state", "postal_code", "latitude", "longitude", "url"
    ]
    existing_cols = [c for c in preferred_cols if c in df.columns]
    remaining_cols = [c for c in df.columns if c not in preferred_cols]
    df = df[existing_cols + remaining_cols]

    df.to_csv(output_csv, index=False, encoding="utf-8")
    print(f"[+] Successfully exported {len(df)} leads to {output_csv}")
    print(df[["name", "phone", "website", "rating"]].head())
    return df

if __name__ == "__main__":
    extract_google_maps_leads(
        query="commercial electricians",
        location="Dallas, Texas",
        max_items=25,
        output_csv="dallas_electricians.csv"
    )
