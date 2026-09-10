"""Extract federal prime contracts, recipient vendors, and obligation amounts from USAspending.

Requirements:
    pip install apify-client pandas python-dotenv

Usage:
    export APIFY_TOKEN="your_apify_api_token"
    python usaspending_defense_awards.py
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

ACTOR_ID = "captainhandsome/usaspending-federal-awards"

def fetch_federal_contracts(keywords: str, award_type: str = "contracts", max_items: int = 50, output_csv: str = "federal_contracts.csv"):
    print(f"[*] Querying USAspending for keywords='{keywords}' (type={award_type})...")
    client = ApifyClient(TOKEN)
    
    run = client.actor(ACTOR_ID).call(run_input={
        "award_type": award_type,
        "keywords": keywords,
        "max_items": max_items,
    })
    
    if not run or run.get("status") != "SUCCEEDED":
        print(f"[!] Run ended with status: {run.get('status')}")
        return None

    dataset_id = run["defaultDatasetId"]
    items = list(client.dataset(dataset_id).iterate_items())
    if not items:
        print("[!] No contract records returned.")
        return None

    df = pd.DataFrame(items)
    df.to_csv(output_csv, index=False, encoding="utf-8")
    print(f"[+] Exported {len(df)} records to {output_csv}")
    
    summary_cols = [c for c in ["recipient_name", "award_amount", "awarding_agency", "description", "start_date"] if c in df.columns]
    print(df[summary_cols].head())
    return df

if __name__ == "__main__":
    fetch_federal_contracts(
        keywords="Lockheed",
        award_type="contracts",
        max_items=25,
        output_csv="lockheed_contracts.csv"
    )
