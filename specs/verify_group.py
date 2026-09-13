"""Live verification for the commercial-group MCP tool specs.

Runs each Actor with a small example payload, polls to completion, fetches
dataset items, and checks a relevance token appears. Read-only against the
Actors; writes nothing back to G:\\apify-fleet or G:\\apify-scrapers.
"""
from __future__ import annotations

import json
import os
import sys
import time
from pathlib import Path

import httpx
from dotenv import load_dotenv

FLEET_ROOT = Path(r"G:\apify-fleet")
BASE = "https://api.apify.com/v2"
OWNER = "captainhandsome"

CASES = [
    {
        "actor": "google-play-reviews-scraper",
        "payload": {"app_ids": ["com.spotify.music"], "max_items": 3},
        "token": "spotify",
    },
    {
        "actor": "linkedin-public-jobs-search",
        "payload": {"search_query": "data engineer", "location": "Seattle, WA", "max_items": 3},
        "token": "seattle",
    },
    {
        "actor": "youtube-search-scraper",
        "payload": {"search_query": "sourdough starter", "max_items": 3},
        "token": "sourdough",
    },
]


def run_one(client: httpx.Client, actor: str, payload: dict, token: str) -> dict:
    r = client.post(f"{BASE}/acts/{OWNER}~{actor}/runs",
                     params={"build": "latest", "timeout": 120}, json=payload)
    if r.status_code >= 400:
        return {"actor": actor, "ok": False, "error": f"start rejected {r.status_code}: {r.text[:300]}"}
    rid = r.json()["data"]["id"]
    deadline = time.monotonic() + 150
    run = {}
    while time.monotonic() < deadline:
        time.sleep(4)
        run = client.get(f"{BASE}/actor-runs/{rid}").json()["data"]
        if run["status"] not in ("READY", "RUNNING"):
            break

    result = {"actor": actor, "run_id": rid, "status": run.get("status"), "exit": run.get("exitCode")}
    if run.get("status") != "SUCCEEDED":
        result["ok"] = False
        result["error"] = f"status={run.get('status')} exit={run.get('exitCode')}"
        return result

    ds = run.get("defaultDatasetId")
    items = []
    if ds:
        items = client.get(f"{BASE}/datasets/{ds}/items", params={"clean": "true", "limit": 10}).json()
    result["items"] = len(items)
    if not items:
        result["ok"] = False
        result["error"] = "empty dataset"
        return result
    blob = json.dumps(items).lower()
    result["token"] = token
    result["relevant"] = token.lower() in blob
    result["ok"] = result["relevant"]
    if not result["ok"]:
        result["error"] = f"token {token!r} not found in output"
        result["sample"] = items[0]
    return result


def main() -> int:
    load_dotenv(FLEET_ROOT / ".env")
    client = httpx.Client(headers={"Authorization": f"Bearer {os.environ['APIFY_TOKEN']}"}, timeout=90)
    results = []
    for case in CASES:
        res = run_one(client, case["actor"], case["payload"], case["token"])
        results.append(res)
        flag = "OK  " if res.get("ok") else "FAIL"
        print(f"{flag} {case['actor']:32} run_id={res.get('run_id')} items={res.get('items')} "
              f"status={res.get('status')} token={case['token']!r} relevant={res.get('relevant')}")
        if not res.get("ok"):
            print(f"       error: {res.get('error')}")
    out = Path(__file__).parent / "_verify_results.json"
    out.write_text(json.dumps(results, indent=2), encoding="utf-8")
    good = sum(1 for r in results if r.get("ok"))
    print(f"\n{good}/{len(results)} verified -> {out}")
    return 0 if good == len(results) else 1


if __name__ == "__main__":
    raise SystemExit(main())
