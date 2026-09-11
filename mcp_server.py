import os
import sys
import json
from typing import Any, Dict, List, Optional
import urllib.request
import urllib.error

# MCP server protocol specification for Apify Scrapers Fleet
# Author: Joseph McRell (@jlucasmcrell)
# Registry ID: io.github.jlucasmcrell/apify-scrapers
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

TOOLS_DEFINITION = [
    {
        "name": "google_maps_search",
        "description": (
            "Extract verified local business listings, postal addresses, phone numbers, review ratings, "
            "and websites from Google Maps.\n\n"
            "Behavior: Read-only search operation. Executes synchronously in the cloud via Apify Actor "
            "'captainhandsome/google-maps-business-search' and returns a JSON array of parsed business objects. "
            "Requires a valid APIFY_TOKEN environment variable.\n\n"
            "Usage Guidelines:\n"
            "- When to use: Use when the user requests local commercial directories, trade services, storefronts, "
            "B2B lead generation, or business contact information within specific geographic regions.\n"
            "- When NOT to use: Do not use for corporate SEC filings, residential real estate listings, general web search, "
            "or employment job openings."
        ),
        "inputSchema": {
            "type": "object",
            "properties": {
                "search_query": {
                    "type": "string",
                    "description": "Geographic search query combining business category and market location (e.g. 'HVAC contractors in Phoenix, AZ' or 'Commercial Electricians Dallas TX')."
                },
                "max_results": {
                    "type": "integer",
                    "minimum": 1,
                    "maximum": 100,
                    "default": 10,
                    "description": "Maximum number of business lead records to extract and return. Defaults to 10."
                }
            },
            "required": ["search_query"]
        }
    },
    {
        "name": "glassdoor_jobs_search",
        "description": (
            "Search current employment vacancies, hiring employers, estimated salary bands, and company ratings "
            "from Glassdoor.\n\n"
            "Behavior: Read-only search operation. Executes synchronously via Apify Actor "
            "'captainhandsome/glassdoor-jobs-scraper' and returns a JSON array of job listing objects. "
            "Requires a valid APIFY_TOKEN environment variable.\n\n"
            "Usage Guidelines:\n"
            "- When to use: Use when researching active hiring trends, job openings, compensation ranges, "
            "or employer ratings for specific occupations.\n"
            "- When NOT to use: Do not use for local B2B lead generation, contractor directory lookups, "
            "or corporate regulatory filings."
        ),
        "inputSchema": {
            "type": "object",
            "properties": {
                "job_title": {
                    "type": "string",
                    "description": "Target job title, role, or occupation keyword to search (e.g. 'Software Engineer' or 'Data Analyst')."
                },
                "location": {
                    "type": "string",
                    "default": "",
                    "description": "Geographic location filter for the job search (e.g. 'Austin, TX', 'New York, NY', or 'Remote'). Defaults to all locations if empty."
                },
                "max_results": {
                    "type": "integer",
                    "minimum": 1,
                    "maximum": 100,
                    "default": 10,
                    "description": "Maximum number of job listings to retrieve. Integer between 1 and 100. Defaults to 10."
                }
            },
            "required": ["job_title"]
        }
    },
    {
        "name": "sec_edgar_filings",
        "description": (
            "Retrieve official U.S. Securities and Exchange Commission (SEC EDGAR) regulatory filings "
            "(10-K annual reports, 10-Q quarterly reports, and 8-K material events) by stock ticker or company name.\n\n"
            "Behavior: Read-only data retrieval. Executes synchronously via Apify Actor "
            "'captainhandsome/sec-edgar-filings-search' and returns a JSON array of SEC filing records containing "
            "accession numbers, filing dates, CIK codes, and document URLs. Requires a valid APIFY_TOKEN environment variable.\n\n"
            "Usage Guidelines:\n"
            "- When to use: Use for public corporate financial research, audited annual reports, quarterly financials, "
            "material event disclosures, and regulatory compliance checks.\n"
            "- When NOT to use: Do not use for private company lookups, real-time stock quotes, or local retail directories."
        ),
        "inputSchema": {
            "type": "object",
            "properties": {
                "ticker": {
                    "type": "string",
                    "description": "Standard publicly traded stock ticker symbol or legal company name (e.g. 'AAPL', 'NVDA', or 'Microsoft Corp')."
                },
                "form_type": {
                    "type": "string",
                    "enum": ["10-K", "10-Q", "8-K", "ALL"],
                    "default": "10-K",
                    "description": "SEC form classification: '10-K' for annual reports, '10-Q' for quarterly reports, '8-K' for unscheduled material events, or 'ALL' for any filing."
                },
                "max_results": {
                    "type": "integer",
                    "minimum": 1,
                    "maximum": 50,
                    "default": 5,
                    "description": "Maximum number of chronological filing records to return. Integer between 1 and 50. Defaults to 5."
                }
            },
            "required": ["ticker"]
        }
    },
    {
        "name": "usaspending_contracts",
        "description": (
            "Search United States federal procurement contracts, defense awards, and prime agency obligations "
            "from the official USAspending database.\n\n"
            "Behavior: Read-only procurement search. Executes synchronously via Apify Actor "
            "'captainhandsome/usaspending-federal-awards' and returns a JSON array of federal award records with "
            "recipient names, awarding agencies, obligation amounts, and contract descriptions. Requires a valid APIFY_TOKEN environment variable.\n\n"
            "Usage Guidelines:\n"
            "- When to use: Use for government contracting intelligence, federal budget tracking, defense vendor analysis, "
            "and public sector procurement research.\n"
            "- When NOT to use: Do not use for commercial B2B sales leads, state-level government grants, or SEC equity filings."
        ),
        "inputSchema": {
            "type": "object",
            "properties": {
                "recipient_name": {
                    "type": "string",
                    "description": "Name of the prime contractor, vendor, or recipient entity (e.g. 'Lockheed Martin', 'Palantir Technologies', or 'Boeing')."
                },
                "max_results": {
                    "type": "integer",
                    "minimum": 1,
                    "maximum": 100,
                    "default": 10,
                    "description": "Maximum number of federal contract award records to return. Integer between 1 and 100. Defaults to 10."
                }
            },
            "required": ["recipient_name"]
        }
    },
    {
        "name": "twitch_live_streams",
        "description": (
            "Extract real-time live broadcasting streams, viewer counts, channel metadata, and game categories "
            "from Twitch.\n\n"
            "Behavior: Read-only live broadcast query. Executes synchronously via Apify Actor "
            "'captainhandsome/twitch-live-streams-scraper' and returns a JSON array of active stream objects with "
            "channel name, broadcast title, game category, language, and concurrent viewer numbers. Requires a valid APIFY_TOKEN environment variable.\n\n"
            "Usage Guidelines:\n"
            "- When to use: Use for live gaming intelligence, influencer analytics, esports viewership tracking, "
            "and real-time audience metrics.\n"
            "- When NOT to use: Do not use for video-on-demand archives, YouTube channels, or social media text posts."
        ),
        "inputSchema": {
            "type": "object",
            "properties": {
                "game_name": {
                    "type": "string",
                    "default": "",
                    "description": "Specific game title or category name to filter streams (e.g. 'Fortnite', 'Minecraft', or 'Just Chatting'). Leave empty for top streams across all categories."
                },
                "language": {
                    "type": "string",
                    "default": "en",
                    "description": "ISO 639-1 language code filter for the broadcast (e.g. 'en' for English, 'es' for Spanish, 'fr' for French). Defaults to 'en'."
                },
                "max_results": {
                    "type": "integer",
                    "minimum": 1,
                    "maximum": 100,
                    "default": 10,
                    "description": "Maximum number of live stream channels to return. Integer between 1 and 100. Defaults to 10."
                }
            }
        }
    },
    {
        "name": "airbnb_listings_search",
        "description": (
            "Search vacation rental listings, nightly prices, occupancy ratings, and property classifications "
            "from Airbnb.\n\n"
            "Behavior: Read-only travel and real estate query. Executes synchronously via Apify Actor "
            "'captainhandsome/airbnb-listings-search' and returns a JSON array of rental property records with "
            "title, room type, nightly rate, review scores, and listing URLs. Requires a valid APIFY_TOKEN environment variable.\n\n"
            "Usage Guidelines:\n"
            "- When to use: Use for short-term rental market analysis, hospitality pricing benchmarks, "
            "and travel accommodation rate tracking.\n"
            "- When NOT to use: Do not use for long-term apartment leases, commercial property leases, or MLS home sales."
        ),
        "inputSchema": {
            "type": "object",
            "properties": {
                "location": {
                    "type": "string",
                    "description": "Destination city, region, or market (e.g. 'Austin, TX', 'Miami, FL', or 'Denver, CO')."
                },
                "max_results": {
                    "type": "integer",
                    "minimum": 1,
                    "maximum": 100,
                    "default": 10,
                    "description": "Maximum number of rental properties to retrieve. Integer between 1 and 100. Defaults to 10."
                }
            },
            "required": ["location"]
        }
    }
]

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

def serve_stdio():
    """Cross-platform synchronous stdio loop compatible with Docker, Cursor, Claude Desktop, and Glama introspection."""
    for line in sys.stdin:
        line = line.strip()
        if not line:
            continue
        try:
            req = json.loads(line)
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
                        "version": "1.0.3"
                    }
                }
            }
            sys.stdout.write(json.dumps(res) + "\n")
            sys.stdout.flush()

        elif method == "notifications/initialized":
            continue

        elif method == "ping":
            res = {
                "jsonrpc": "2.0",
                "id": req_id,
                "result": {}
            }
            sys.stdout.write(json.dumps(res) + "\n")
            sys.stdout.flush()

        elif method == "tools/list":
            res = {
                "jsonrpc": "2.0",
                "id": req_id,
                "result": {
                    "tools": TOOLS_DEFINITION
                }
            }
            sys.stdout.write(json.dumps(res) + "\n")
            sys.stdout.flush()

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
                elif tool_name == "twitch_live_streams":
                    game = tool_args.get("game_name", "")
                    lang = tool_args.get("language", "en")
                    limit = int(tool_args.get("max_results", 10))
                    data = run_actor_sync(ACTORS["twitch_streams"], {"game": game, "language": lang, "max_items": limit})
                elif tool_name == "airbnb_listings_search":
                    loc = tool_args.get("location")
                    limit = int(tool_args.get("max_results", 10))
                    data = run_actor_sync(ACTORS["airbnb"], {"location": loc, "max_items": limit})
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
            sys.stdout.write(json.dumps(res) + "\n")
            sys.stdout.flush()

def main():
    serve_stdio()

if __name__ == "__main__":
    main()
