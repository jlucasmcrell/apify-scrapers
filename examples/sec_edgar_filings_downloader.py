"""Query and download US SEC EDGAR filings metadata and primary document links.

Requirements:
    pip install apify-client pandas python-dotenv

Usage:
    export APIFY_TOKEN="your_apify_api_token"
    python sec_edgar_filings_downloader.py
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

ACTOR_ID = "captainhandsome/sec-edgar-filings-search"

def fetch_sec_filings(companies: list[str], forms: list[str], max_items: int = 50, output_csv: str = "sec_filings.csv"):
    print(f"[*] Querying SEC EDGAR for companies={companies}, forms={forms}...")
    client = ApifyClient(TOKEN)
    
    run = client.actor(ACTOR_ID).call(run_input={
        "companies": companies,
        "forms": forms,
        "include_amendments": False,
        "max_items": max_items,
    })
    
    if not run or run.get("status") != "SUCCEEDED":
        print(f"[!] Run ended with status: {(run or {}).get('status')}")
        return None

    dataset_id = run["defaultDatasetId"]
    items = list(client.dataset(dataset_id).iterate_items())
    if not items:
        print("[!] No filings returned.")
        return None

    df = pd.DataFrame(items)
    df.to_csv(output_csv, index=False, encoding="utf-8")
    print(f"[+] Exported {len(df)} filings to {output_csv}")
    
    summary_cols = [c for c in ["company_name", "ticker", "form", "filing_date", "filing_url"] if c in df.columns]
    print(df[summary_cols].head())
    return df

if __name__ == "__main__":
    fetch_sec_filings(
        companies=["AAPL", "MSFT", "NVDA"],
        forms=["10-K", "8-K"],
        max_items=25,
        output_csv="big_tech_filings.csv"
    )
