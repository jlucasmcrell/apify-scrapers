"""Extract job listings, employer ratings, salaries, and canonical URLs from Glassdoor.

Requirements:
    pip install apify-client pandas python-dotenv

Usage:
    export APIFY_TOKEN="your_apify_api_token"
    python glassdoor_jobs_tracker.py
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

ACTOR_ID = "captainhandsome/glassdoor-jobs-scraper"

def search_glassdoor_jobs(query: str, location: str, max_items: int = 30, output_csv: str = "glassdoor_jobs.csv"):
    print(f"[*] Scraping Glassdoor for query='{query}' in '{location}'...")
    client = ApifyClient(TOKEN)
    
    run = client.actor(ACTOR_ID).call(run_input={
        "search_query": query,
        "location": location,
        "max_items": max_items,
    })
    
    if not run or run.get("status") != "SUCCEEDED":
        print(f"[!] Run ended with status: {run.get('status')}")
        return None

    dataset_id = run["defaultDatasetId"]
    items = list(client.dataset(dataset_id).iterate_items())
    if not items:
        print("[!] No jobs returned.")
        return None

    df = pd.DataFrame(items)
    df.to_csv(output_csv, index=False, encoding="utf-8")
    print(f"[+] Exported {len(df)} jobs to {output_csv}")
    
    summary_cols = [c for c in ["job_title", "employer", "location", "salary", "rating", "job_url"] if c in df.columns]
    print(df[summary_cols].head())
    return df

if __name__ == "__main__":
    search_glassdoor_jobs(
        query="Machine Learning Engineer",
        location="Austin, Texas",
        max_items=20,
        output_csv="austin_ml_jobs.csv"
    )
