import sys
import json
import time
import urllib.request
import urllib.error
import os

sys.path.insert(0, "G:/apify-fleet")
from dotenv import load_dotenv

load_dotenv("G:/apify-fleet/.env")
TOKEN = os.environ.get("APIFY_TOKEN")
if not TOKEN:
    raise SystemExit("APIFY_TOKEN not found in env")

ACTOR = sys.argv[1]  # e.g. clinical-trials-search
PAYLOAD = json.loads(sys.argv[2])

BASE = "https://api.apify.com/v2"
clean_id = f"captainhandsome~{ACTOR}"


def req(method, url, data=None):
    body = json.dumps(data).encode("utf-8") if data is not None else None
    r = urllib.request.Request(url, data=body, method=method,
                                headers={"Content-Type": "application/json"})
    try:
        with urllib.request.urlopen(r, timeout=130) as resp:
            return json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        err = e.read().decode("utf-8", errors="ignore")
        print(f"HTTP {e.code}: {err}", file=sys.stderr)
        raise


start_url = f"{BASE}/acts/{clean_id}/runs?token={TOKEN}&build=latest&timeout=120"
run = req("POST", start_url, PAYLOAD)
run_id = run["data"]["id"]
print(f"RUN_ID={run_id}")

status_url = f"{BASE}/actor-runs/{run_id}?token={TOKEN}"
for i in range(60):
    time.sleep(3)
    r = req("GET", status_url)
    status = r["data"]["status"]
    if status in ("SUCCEEDED", "FAILED", "ABORTED", "TIMED-OUT"):
        break
print(f"STATUS={status}")

if status != "SUCCEEDED":
    print(json.dumps(r["data"], indent=2))
    sys.exit(1)

dataset_id = r["data"]["defaultDatasetId"]
items_url = f"{BASE}/datasets/{dataset_id}/items?token={TOKEN}&clean=true"
items = req("GET", items_url)
print(f"ITEM_COUNT={len(items)}")
print(json.dumps(items, indent=2)[:6000])
