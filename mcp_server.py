import os
import sys
import json
import asyncio
from typing import Any, Dict, List, Optional
import urllib.request
import urllib.error

# MCP server protocol specification for Apify Scrapers Fleet
# Author: Joseph McRell (@jlucasmcrell)
# Tools provided:
# 1. google_maps_search: Extract B2B leads, businesses, phone numbers, ratings
# 2. glassdoor_jobs_search: Extract job postings with normalized posting dates
# 3. sec_edgar_filings: Query SEC 10-K, 10-Q, 8-K filings by ticker/company
# 4. usaspending_contracts: Search federal awards, defense contracts, prime obligations
# 5. twitch_live_streams: Live stream monitoring by game or language
# 6. airbnb_listings_search: Real estate & short-term rental market rates

APIFY_API_BASE = "https://api.apify.com/v2"

ACTORS = {
    "google_maps": "captainhandsome/google-maps-business-search",
    "glassdoor_jobs": "captainhandsome/glassdoor-jobs-scraper",
    "sec_edgar": "captainhandsome/sec-edgar-filings-search",
    "usaspending": "captainhandsome/usaspending-federal-awards",
    "twitch_streams": "captainhandsome/twitch-live-streams-scraper",
    "airbnb": "captainhandsome/airbnb-listings-search",
}

def get_token() -> str:
    token = os.environ.get("APIFY_TOKEN")
    if not token:
        raise ValueError("APIFY_TOKEN environment variable is required to run Apify tools.")
    return token

def run_actor_sync(actor_id: str, run_input: Dict[str, Any], timeout_secs: int = 120) -> List[Dict[str, Any]]:
    """Runs an Apify actor synchronously and returns the output dataset items."""
    token = get_token()
    clean_id = actor_id.replace("/", "~")
    url = f"{APIFY_API_BASE}/acts/{clean_id}/run-sync-get-dataset-items?token={token}&timeout={timeout_secs}"
    
    payload = json.dumps(run_input).encode("utf-8")
    req = urllib.request.Request(
        url,
        data=payload,
        headers={"Content-Type": "application/json"},
        method="POST"
    )
    
    try:
        with urllib.request.urlopen(req, timeout=timeout_secs + 10) as response:
            data = json.loads(response.read().decode("utf-8"))
            return data
    except urllib.error.HTTPError as e:
        err_msg = e.read().decode("utf-8", errors="ignore")
        raise RuntimeError(f"Apify API error ({e.code}): {err_msg}")
    except Exception as e:
        raise RuntimeError(f"Actor run failed: {str(e)}")

# Standard JSON-RPC MCP server loop (stdio)
async def handle_stdio():
    reader = asyncio.StreamReader()
    protocol = asyncio.StreamReaderProtocol(reader)
    loop = asyncio.get_event_loop()
    await loop.connect_read_pipe(lambda: protocol, sys.stdin)
    writer = sys.stdout

    while True:
        line = await reader.readline()
        if not line:
            break
        try:
            req = json.loads(line.decode("utf-8"))
        except Exception:
            continue

        req_id = req.get("id")
        method = req.get("method")
        params = req.get("params", {})

        if method == "initialize":
            res = {
                "jsonrpc": "2.0",
                "id": req_id,
                "result": {
                    "protocolVersion": "2024-11-05",
                    "capabilities": {"tools": {}},
                    "serverInfo": {
                        "name": "apify-scrapers-mcp",
                        "version": "1.0.0"
                    }
                }
            }
            writer.write(json.dumps(res) + "\n")
            writer.flush()

        elif method == "tools/list":
            res = {
                "jsonrpc": "2.0",
                "id": req_id,
                "result": {
                    "tools": [
                        {
                            "name": "google_maps_search",
                            "description": "Extract verified business leads, addresses, ratings, and phone numbers from Google Maps. Backed by captainhandsome/google-maps-business-search.",
                            "inputSchema": {
                                "type": "object",
                                "properties": {
                                    "search_query": {"type": "string", "description": "e.g. 'HVAC contractors in Phoenix, AZ'"},
                                    "max_results": {"type": "integer", "default": 10, "description": "Number of leads to retrieve (1-100)"}
                                },
                                "required": ["search_query"]
                            }
                        },
                        {
                            "name": "glassdoor_jobs_search",
                            "description": "Scrape Glassdoor job openings with canonical listing URLs and normalized posting dates. Backed by captainhandsome/glassdoor-jobs-scraper.",
                            "inputSchema": {
                                "type": "object",
                                "properties": {
                                    "job_title": {"type": "string", "description": "e.g. 'Software Engineer'"},
                                    "location": {"type": "string", "description": "e.g. 'Austin, TX' or 'Remote'"},
                                    "max_results": {"type": "integer", "default": 10}
                                },
                                "required": ["job_title"]
                            }
                        },
                        {
                            "name": "sec_edgar_filings",
                            "description": "Retrieve corporate SEC filings (10-K, 10-Q, 8-K) by company name or stock ticker. Backed by captainhandsome/sec-edgar-filings-search.",
                            "inputSchema": {
                                "type": "object",
                                "properties": {
                                    "ticker": {"type": "string", "description": "e.g. 'AAPL' or 'NVDA'"},
                                    "form_type": {"type": "string", "default": "10-K", "description": "10-K, 10-Q, or 8-K"},
                                    "max_results": {"type": "integer", "default": 5}
                                },
                                "required": ["ticker"]
                            }
                        },
                        {
                            "name": "usaspending_contracts",
                            "description": "Search US federal procurement, defense awards, and prime agency obligations. Backed by captainhandsome/usaspending-federal-awards.",
                            "inputSchema": {
                                "type": "object",
                                "properties": {
                                    "recipient_name": {"type": "string", "description": "e.g. 'Lockheed Martin' or 'Palantir'"},
                                    "max_results": {"type": "integer", "default": 10}
                                },
                                "required": ["recipient_name"]
                            }
                        }
                    ]
                }
            }
            writer.write(json.dumps(res) + "\n")
            writer.flush()

        elif method == "tools/call":
            tool_name = params.get("name")
            tool_args = params.get("arguments", {})
            try:
                if tool_name == "google_maps_search":
                    query = tool_args.get("search_query")
                    limit = int(tool_args.get("max_results", 10))
                    data = run_actor_sync(ACTORS["google_maps"], {"search_terms": [query], "max_items": limit})
                elif tool_name == "glassdoor_jobs_search":
                    title = tool_args.get("job_title")
                    loc = tool_args.get("location", "")
                    limit = int(tool_args.get("max_results", 10))
                    data = run_actor_sync(ACTORS["glassdoor_jobs"], {"keyword": title, "location": loc, "max_results": limit})
                elif tool_name == "sec_edgar_filings":
                    ticker = tool_args.get("ticker")
                    form = tool_args.get("form_type", "10-K")
                    limit = int(tool_args.get("max_results", 5))
                    data = run_actor_sync(ACTORS["sec_edgar"], {"company_or_ticker": ticker, "form_type": form, "max_items": limit})
                elif tool_name == "usaspending_contracts":
                    rec = tool_args.get("recipient_name")
                    limit = int(tool_args.get("max_results", 10))
                    data = run_actor_sync(ACTORS["usaspending"], {"award_type": "contracts", "recipient_search_text": rec, "max_items": limit})
                else:
                    raise ValueError(f"Unknown tool: {tool_name}")

                res = {
                    "jsonrpc": "2.0",
                    "id": req_id,
                    "result": {
                        "content": [
                            {"type": "text", "text": json.dumps(data, indent=2)}
                        ]
                    }
                }
            except Exception as err:
                res = {
                    "jsonrpc": "2.0",
                    "id": req_id,
                    "error": {
                        "code": -32603,
                        "message": str(err)
                    }
                }
            writer.write(json.dumps(res) + "\n")
            writer.flush()

if __name__ == "__main__":
    asyncio.run(handle_stdio())
