"""Monitor active Twitch streams, viewer counts, and broadcaster usernames by game category.

Requirements:
    pip install apify-client pandas python-dotenv

Usage:
    export APIFY_TOKEN="your_apify_api_token"
    python twitch_live_stream_monitor.py
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

ACTOR_ID = "captainhandsome/twitch-live-streams-scraper"

def monitor_twitch_category(category_slug: str, max_items: int = 30, output_csv: str = "twitch_streams.csv"):
    print(f"[*] Querying active Twitch streams for category '{category_slug}' (limit: {max_items})...")
    client = ApifyClient(TOKEN)
    
    run = client.actor(ACTOR_ID).call(run_input={
        "search_query": category_slug,
        "max_items": max_items,
    })
    
    if not run or run.get("status") != "SUCCEEDED":
        print(f"[!] Run ended with status: {run.get('status')}")
        return None

    dataset_id = run["defaultDatasetId"]
    items = list(client.dataset(dataset_id).iterate_items())
    if not items:
        print("[!] No streams returned.")
        return None

    df = pd.DataFrame(items)
    df.to_csv(output_csv, index=False, encoding="utf-8")
    print(f"[+] Exported {len(df)} live streams to {output_csv}")
    
    summary_cols = [c for c in ["streamer_username", "stream_title", "viewer_count", "game_name", "url"] if c in df.columns]
    print(df[summary_cols].head())
    return df

if __name__ == "__main__":
    monitor_twitch_category(
        category_slug="fortnite",
        max_items=25,
        output_csv="fortnite_streams.csv"
    )
