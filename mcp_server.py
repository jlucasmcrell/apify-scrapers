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
        "title": "Google Maps Local Business and B2B Lead Extractor",
        "description": (
            "Extract verified commercial business listings, postal addresses, phone numbers, "
            "customer review ratings, and canonical websites from Google Maps.\n\n"
            "Behavioral Transparency:\n"
            "- Execution: Network call executed synchronously in the cloud via Apify Actor 'captainhandsome/google-maps-business-search'.\n"
            "- Side Effects: Strictly read-only; does not modify external databases, accounts, or state.\n"
            "- Authentication: Requires APIFY_TOKEN environment variable.\n"
            "- Latency & Limits: Typical run duration is 15-45 seconds; timeout capped at 120 seconds.\n\n"
            "Usage Guidelines:\n"
            "- When to use: Use when the user requests local commercial directories, trade contractors, "
            "physical retail storefronts, or B2B regional sales leads.\n"
            "- When NOT to use: Do not use for employment job listings, corporate regulatory filings, "
            "federal procurement awards, or short-term vacation rentals.\n"
            "- Named alternatives: Use 'glassdoor_jobs_search' for employer vacancies, 'sec_edgar_filings' "
            "for corporate SEC disclosures, 'usaspending_contracts' for government awards, or "
            "'airbnb_listings_search' for vacation rentals."
        ),
        "inputSchema": {
            "type": "object",
            "properties": {
                "search_query": {
                    "type": "string",
                    "minLength": 3,
                    "description": "Geographic search query combining target trade category and municipal market location (e.g. 'HVAC contractors in Phoenix, AZ' or 'Commercial Electricians Dallas TX')."
                },
                "max_results": {
                    "type": "integer",
                    "minimum": 1,
                    "maximum": 100,
                    "default": 10,
                    "description": "Maximum count of business lead records to extract and return. Defaults to 10."
                }
            },
            "required": ["search_query"]
        },
        "outputSchema": {
            "type": "array",
            "description": "Collection of verified commercial business entity records extracted from Google Maps.",
            "items": {
                "type": "object",
                "properties": {
                    "title": {"type": "string", "description": "Trading name or legal corporate title of the business."},
                    "phone": {"type": "string", "description": "Primary commercial telephone number with regional area code."},
                    "website": {"type": "string", "description": "Canonical HTTP/HTTPS business website or landing page."},
                    "address": {"type": "string", "description": "Full formatted postal street address including city, state, and ZIP."},
                    "totalScore": {"type": "number", "description": "Aggregate customer review rating on a 1.0 to 5.0 scale."},
                    "reviewsCount": {"type": "integer", "description": "Total count of public Google reviews submitted by customers."},
                    "categoryName": {"type": "string", "description": "Primary industry classification or business trade category."},
                    "url": {"type": "string", "description": "Direct canonical Google Maps place URL."}
                },
                "required": ["title", "address"]
            }
        },
        "annotations": {
            "readOnlyHint": True,
            "destructiveHint": False,
            "idempotentHint": True,
            "openWorldHint": True
        }
    },
    {
        "name": "glassdoor_jobs_search",
        "title": "Glassdoor Active Job Postings and Salary Search",
        "description": (
            "Search active employment vacancies, hiring employers, estimated compensation bands, "
            "and corporate ratings from Glassdoor.\n\n"
            "Behavioral Transparency:\n"
            "- Execution: Network call executed synchronously in the cloud via Apify Actor 'captainhandsome/glassdoor-jobs-scraper'.\n"
            "- Side Effects: Strictly read-only; does not modify external accounts or submit applications.\n"
            "- Authentication: Requires APIFY_TOKEN environment variable.\n"
            "- Latency & Limits: Typical run duration is 15-40 seconds; timeout capped at 120 seconds.\n\n"
            "Usage Guidelines:\n"
            "- When to use: Use when researching active job openings, hiring trends, employer compensation ranges, "
            "or workplace ratings for specific professions.\n"
            "- When NOT to use: Do not use for local commercial lead generation, corporate financial filings, "
            "or live video streaming.\n"
            "- Named alternatives: Use 'google_maps_search' for commercial trade directories, 'sec_edgar_filings' "
            "for SEC corporate filings, or 'usaspending_contracts' for federal prime contractor records."
        ),
        "inputSchema": {
            "type": "object",
            "properties": {
                "job_title": {
                    "type": "string",
                    "minLength": 2,
                    "description": "Target job title, professional role, or occupational keyword (e.g. 'Software Engineer', 'Data Analyst', or 'DevOps Architect')."
                },
                "location": {
                    "type": "string",
                    "default": "",
                    "description": "Geographic municipality, metropolitan area, or 'Remote' filter (e.g. 'Austin, TX' or 'New York, NY'). Defaults to all locations if empty."
                },
                "max_results": {
                    "type": "integer",
                    "minimum": 1,
                    "maximum": 100,
                    "default": 10,
                    "description": "Maximum number of active job listings to retrieve. Integer between 1 and 100. Defaults to 10."
                }
            },
            "required": ["job_title"]
        },
        "outputSchema": {
            "type": "array",
            "description": "Collection of active employment job postings extracted from Glassdoor.",
            "items": {
                "type": "object",
                "properties": {
                    "jobTitle": {"type": "string", "description": "Official employment position or vacancy title."},
                    "companyName": {"type": "string", "description": "Name of the recruiting employer or corporate entity."},
                    "location": {"type": "string", "description": "Geographic workplace location or remote designation."},
                    "salaryEstimate": {"type": "string", "description": "Estimated annual or hourly compensation range when published."},
                    "rating": {"type": "number", "description": "Employer workplace review rating on a 1.0 to 5.0 scale."},
                    "jobUrl": {"type": "string", "description": "Direct canonical URL to the employment application posting."}
                },
                "required": ["jobTitle", "companyName"]
            }
        },
        "annotations": {
            "readOnlyHint": True,
            "destructiveHint": False,
            "idempotentHint": True,
            "openWorldHint": True
        }
    },
    {
        "name": "sec_edgar_filings",
        "title": "SEC EDGAR Public Corporate Filings Retrieval",
        "description": (
            "Retrieve official United States Securities and Exchange Commission (SEC EDGAR) regulatory filings "
            "including 10-K annual reports, 10-Q quarterly reports, and 8-K material events.\n\n"
            "Behavioral Transparency:\n"
            "- Execution: Network call executed synchronously in the cloud via Apify Actor 'captainhandsome/sec-edgar-filings-search'.\n"
            "- Side Effects: Strictly read-only; queries public federal securities disclosures.\n"
            "- Authentication: Requires APIFY_TOKEN environment variable.\n"
            "- Latency & Limits: Typical run duration is 10-30 seconds; timeout capped at 120 seconds.\n\n"
            "Usage Guidelines:\n"
            "- When to use: Use for public corporate financial statements, audited balance sheets, executive "
            "compensation disclosures, and regulatory material event filings.\n"
            "- When NOT to use: Do not use for private non-public company intelligence, real-time stock prices, "
            "or local trade vendor lists.\n"
            "- Named alternatives: Use 'usaspending_contracts' for federal procurement contracts, "
            "'google_maps_search' for local commercial entities, or 'glassdoor_jobs_search' for hiring trends."
        ),
        "inputSchema": {
            "type": "object",
            "properties": {
                "ticker": {
                    "type": "string",
                    "minLength": 1,
                    "description": "Public stock ticker symbol or official company name (e.g. 'AAPL', 'NVDA', or 'Tesla Inc')."
                },
                "form_type": {
                    "type": "string",
                    "enum": ["10-K", "10-Q", "8-K", "ALL"],
                    "default": "10-K",
                    "description": "SEC form classification: '10-K' for annual reports, '10-Q' for quarterly reports, '8-K' for material events, or 'ALL' for any filing."
                },
                "max_results": {
                    "type": "integer",
                    "minimum": 1,
                    "maximum": 50,
                    "default": 5,
                    "description": "Maximum count of chronological filing records to retrieve. Defaults to 5."
                }
            },
            "required": ["ticker"]
        },
        "outputSchema": {
            "type": "array",
            "description": "Collection of official SEC EDGAR corporate regulatory filing disclosures.",
            "items": {
                "type": "object",
                "properties": {
                    "formType": {"type": "string", "description": "Regulatory filing form designation code (e.g. 10-K, 10-Q, 8-K)."},
                    "filingDate": {"type": "string", "description": "Official chronological submission date in YYYY-MM-DD format."},
                    "accessionNumber": {"type": "string", "description": "Unique SEC EDGAR document accession identifier."},
                    "companyName": {"type": "string", "description": "Official registered legal name of the filing corporation."},
                    "cik": {"type": "string", "description": "Central Index Key (CIK) ten-digit company identifier assigned by the SEC."},
                    "documentUrl": {"type": "string", "description": "Canonical HTTPS link to the full filing disclosure on SEC.gov."}
                },
                "required": ["formType", "filingDate", "documentUrl"]
            }
        },
        "annotations": {
            "readOnlyHint": True,
            "destructiveHint": False,
            "idempotentHint": True,
            "openWorldHint": True
        }
    },
    {
        "name": "usaspending_contracts",
        "title": "USAspending Federal Procurement and Defense Awards Search",
        "description": (
            "Search United States federal procurement contracts, defense department awards, and "
            "prime agency obligations from the official USAspending database.\n\n"
            "Behavioral Transparency:\n"
            "- Execution: Network call executed synchronously in the cloud via Apify Actor 'captainhandsome/usaspending-federal-awards'.\n"
            "- Side Effects: Strictly read-only; queries public federal procurement databases.\n"
            "- Authentication: Requires APIFY_TOKEN environment variable.\n"
            "- Latency & Limits: Typical run duration is 10-35 seconds; timeout capped at 120 seconds.\n\n"
            "Usage Guidelines:\n"
            "- When to use: Use for government contracting intelligence, prime federal vendor tracking, "
            "defense obligation amounts, and public procurement research.\n"
            "- When NOT to use: Do not use for commercial retail leads, corporate equity SEC filings, "
            "or consumer vacation pricing.\n"
            "- Named alternatives: Use 'sec_edgar_filings' for corporate 10-K annual reports, 'google_maps_search' "
            "for private commercial trade vendors, or 'glassdoor_jobs_search' for company hiring data."
        ),
        "inputSchema": {
            "type": "object",
            "properties": {
                "recipient_name": {
                    "type": "string",
                    "minLength": 2,
                    "description": "Legal entity name of the prime contractor, corporate vendor, or recipient institution (e.g. 'Lockheed Martin', 'Palantir Technologies', or 'Boeing')."
                },
                "max_results": {
                    "type": "integer",
                    "minimum": 1,
                    "maximum": 100,
                    "default": 10,
                    "description": "Maximum number of federal contract award records to retrieve. Defaults to 10."
                }
            },
            "required": ["recipient_name"]
        },
        "outputSchema": {
            "type": "array",
            "description": "Collection of official federal contract and award obligation records.",
            "items": {
                "type": "object",
                "properties": {
                    "recipientName": {"type": "string", "description": "Legal business or institutional name of the award recipient."},
                    "awardingAgency": {"type": "string", "description": "Federal department or agency authorizing the procurement contract."},
                    "obligationAmount": {"type": "number", "description": "Total monetary obligation amount funded by the federal government in USD."},
                    "awardDescription": {"type": "string", "description": "Executive summary statement of the contracted goods or defense services."},
                    "awardDate": {"type": "string", "description": "Action signing date in YYYY-MM-DD format."},
                    "contractId": {"type": "string", "description": "Unique federal procurement award ID (PIID or FAIN)."}
                },
                "required": ["recipientName", "obligationAmount"]
            }
        },
        "annotations": {
            "readOnlyHint": True,
            "destructiveHint": False,
            "idempotentHint": True,
            "openWorldHint": True
        }
    },
    {
        "name": "twitch_live_streams",
        "title": "Twitch Real-Time Live Stream Intelligence and Viewership",
        "description": (
            "Extract real-time live broadcasting streams, viewer counts, channel metadata, "
            "and game categories from Twitch.\n\n"
            "Behavioral Transparency:\n"
            "- Execution: Network call executed synchronously in the cloud via Apify Actor 'captainhandsome/twitch-live-streams-scraper'.\n"
            "- Side Effects: Strictly read-only; queries active public Twitch broadcasts.\n"
            "- Authentication: Requires APIFY_TOKEN environment variable.\n"
            "- Latency & Limits: Typical run duration is 10-25 seconds; timeout capped at 120 seconds.\n\n"
            "Usage Guidelines:\n"
            "- When to use: Use for live video broadcasting metrics, concurrent esports viewership tracking, "
            "influencer intelligence, and gaming category analysis.\n"
            "- When NOT to use: Do not use for recorded video-on-demand archives, YouTube channels, "
            "or employment job boards.\n"
            "- Named alternatives: Use 'glassdoor_jobs_search' for corporate hiring data, 'google_maps_search' "
            "for local retail directories, or 'airbnb_listings_search' for travel pricing."
        ),
        "inputSchema": {
            "type": "object",
            "properties": {
                "game_name": {
                    "type": "string",
                    "default": "",
                    "description": "Specific video game title or streaming category filter (e.g. 'Fortnite', 'Minecraft', or 'Just Chatting'). Leave empty for top streams across all categories."
                },
                "language": {
                    "type": "string",
                    "default": "en",
                    "description": "ISO 639-1 language code filter for the live broadcast (e.g. 'en' for English, 'es' for Spanish, 'fr' for French). Defaults to 'en'."
                },
                "max_results": {
                    "type": "integer",
                    "minimum": 1,
                    "maximum": 100,
                    "default": 10,
                    "description": "Maximum number of live stream channels to return. Integer between 1 and 100. Defaults to 10."
                }
            }
        },
        "outputSchema": {
            "type": "array",
            "description": "Collection of active real-time Twitch stream broadcast records.",
            "items": {
                "type": "object",
                "properties": {
                    "channelName": {"type": "string", "description": "Twitch username or broadcaster channel handle."},
                    "streamTitle": {"type": "string", "description": "Broadcaster headline title for the active live session."},
                    "gameName": {"type": "string", "description": "Primary game title or stream category."},
                    "viewerCount": {"type": "integer", "description": "Number of concurrent live spectators actively watching the stream."},
                    "language": {"type": "string", "description": "Language code of the broadcast."},
                    "streamUrl": {"type": "string", "description": "Canonical HTTPS stream link to the live broadcast channel."}
                },
                "required": ["channelName", "viewerCount"]
            }
        },
        "annotations": {
            "readOnlyHint": True,
            "destructiveHint": False,
            "idempotentHint": True,
            "openWorldHint": True
        }
    },
    {
        "name": "airbnb_listings_search",
        "title": "Airbnb Short-Term Rental Rates and Property Search",
        "description": (
            "Search vacation rental listings, nightly prices, occupancy ratings, and "
            "property classifications from Airbnb.\n\n"
            "Behavioral Transparency:\n"
            "- Execution: Network call executed synchronously in the cloud via Apify Actor 'captainhandsome/airbnb-listings-search'.\n"
            "- Side Effects: Strictly read-only; queries public hospitality and vacation listings.\n"
            "- Authentication: Requires APIFY_TOKEN environment variable.\n"
            "- Latency & Limits: Typical run duration is 15-40 seconds; timeout capped at 120 seconds.\n\n"
            "Usage Guidelines:\n"
            "- When to use: Use for short-term vacation rental market research, hospitality pricing comparisons, "
            "and regional accommodation rate benchmarking.\n"
            "- When NOT to use: Do not use for long-term residential apartment leases, MLS residential home sales, "
            "or commercial office leasing.\n"
            "- Named alternatives: Use 'google_maps_search' for hotel and lodging business contacts, "
            "'glassdoor_jobs_search' for hospitality employment, or 'sec_edgar_filings' for public REIT financial filings."
        ),
        "inputSchema": {
            "type": "object",
            "properties": {
                "location": {
                    "type": "string",
                    "minLength": 2,
                    "description": "Destination metropolitan city, tourist region, or geographic market (e.g. 'Austin, TX', 'Miami, FL', or 'Denver, CO')."
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
        },
        "outputSchema": {
            "type": "array",
            "description": "Collection of short-term vacation rental property listings extracted from Airbnb.",
            "items": {
                "type": "object",
                "properties": {
                    "listingName": {"type": "string", "description": "Headline property title or host description."},
                    "roomType": {"type": "string", "description": "Accommodation category (e.g. Entire home, Private room, Hotel room)."},
                    "pricePerNight": {"type": "string", "description": "Nightly accommodation tariff rate in local currency."},
                    "rating": {"type": "number", "description": "Aggregate guest cleanliness and satisfaction score on a 1.0 to 5.0 scale."},
                    "reviewCount": {"type": "integer", "description": "Total number of verified guest reviews posted for the property."},
                    "listingUrl": {"type": "string", "description": "Canonical HTTPS link to the Airbnb listing reservation page."}
                },
                "required": ["listingName", "pricePerNight"]
            }
        },
        "annotations": {
            "readOnlyHint": True,
            "destructiveHint": False,
            "idempotentHint": True,
            "openWorldHint": True
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


PROMPTS_DEFINITION = [
    {
        "name": "b2b_lead_search",
        "description": "Extract verified B2B leads, trade contractors, and local business contacts from Google Maps.",
        "arguments": [
            {
                "name": "search_query",
                "description": "Target trade category and location (e.g. 'HVAC contractors in Phoenix AZ' or 'Commercial Electricians Dallas TX')",
                "required": True
            },
            {
                "name": "max_results",
                "description": "Number of leads to retrieve (default 10, max 100)",
                "required": False
            }
        ]
    },
    {
        "name": "sec_filing_analysis",
        "description": "Retrieve official SEC EDGAR 10-K, 10-Q, or 8-K regulatory filings for public companies.",
        "arguments": [
            {
                "name": "ticker",
                "description": "Stock ticker symbol (e.g. AAPL, MSFT, NVDA, TSLA)",
                "required": True
            },
            {
                "name": "form_type",
                "description": "Filing form type (10-K, 10-Q, 8-K). Defaults to 10-K.",
                "required": False
            }
        ]
    },
    {
        "name": "federal_procurement_audit",
        "description": "Search federal contract awards and prime obligations awarded to a recipient on USAspending.",
        "arguments": [
            {
                "name": "recipient_name",
                "description": "Corporate prime contractor or vendor name (e.g. 'Lockheed Martin', 'Palantir')",
                "required": True
            }
        ]
    }
]

RESOURCES_DEFINITION = [
    {
        "uri": "apify://actors/catalog",
        "name": "Apify Scrapers Fleet Catalog",
        "description": "Complete directory of backed Apify actors, capabilities, endpoints, and input parameters.",
        "mimeType": "application/json"
    },
    {
        "uri": "apify://docs/authentication",
        "name": "Apify MCP Authentication Guide",
        "description": "Setup guide for APIFY_TOKEN credentials, rate limits, and cloud execution.",
        "mimeType": "text/markdown"
    }
]


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
                    "capabilities": {
                        "tools": {"listChanged": False},
                        "prompts": {"listChanged": False},
                        "resources": {"subscribe": False, "listChanged": False}
                    },
                    "serverInfo": {
                        "name": "apify-scrapers-mcp",
                        "version": "1.0.5"
                    },
                    "instructions": (
                        "Apify Scrapers MCP provides enterprise-grade data extraction tools for "
                        "B2B leads (Google Maps), employment vacancies (Glassdoor), corporate regulatory "
                        "filings (SEC EDGAR), federal procurement obligations (USAspending), live streaming "
                        "analytics (Twitch), and vacation rental pricing (Airbnb). All tools run synchronously "
                        "in the cloud via dedicated Apify actors and require an APIFY_TOKEN environment variable."
                    )
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

        elif method == "prompts/list":
            res = {
                "jsonrpc": "2.0",
                "id": req_id,
                "result": {
                    "prompts": PROMPTS_DEFINITION
                }
            }
            sys.stdout.write(json.dumps(res) + "\n")
            sys.stdout.flush()

        elif method == "prompts/get":
            p_name = params.get("name")
            p_args = params.get("arguments", {})
            res = {
                "jsonrpc": "2.0",
                "id": req_id,
                "result": {
                    "description": f"Workflow template for {p_name}",
                    "messages": [
                        {
                            "role": "user",
                            "content": {
                                "type": "text",
                                "text": f"Execute data extraction workflow for {p_name} with parameters: {json.dumps(p_args)}"
                            }
                        }
                    ]
                }
            }
            sys.stdout.write(json.dumps(res) + "\n")
            sys.stdout.flush()

        elif method == "resources/list":
            res = {
                "jsonrpc": "2.0",
                "id": req_id,
                "result": {
                    "resources": RESOURCES_DEFINITION
                }
            }
            sys.stdout.write(json.dumps(res) + "\n")
            sys.stdout.flush()

        elif method == "resources/read":
            uri = params.get("uri", "")
            if uri == "apify://actors/catalog":
                content = json.dumps({"actors": ACTORS, "maintainer": "jlucasmcrell", "registry": "io.github.jlucasmcrell/apify-scrapers"}, indent=2)
                mime = "application/json"
            else:
                content = "# Apify MCP Authentication\n\nSet APIFY_TOKEN environment variable with your personal token from console.apify.com."
                mime = "text/markdown"
            res = {
                "jsonrpc": "2.0",
                "id": req_id,
                "result": {
                    "contents": [
                        {
                            "uri": uri,
                            "mimeType": mime,
                            "text": content
                        }
                    ]
                }
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
