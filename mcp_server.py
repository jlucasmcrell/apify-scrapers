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
    "alabama_business": "captainhandsome/al-business-entity-search",
    "california_contractor_license": "captainhandsome/ca-contractor-license-search",
    "clinical_trials": "captainhandsome/clinical-trials-search",
    "epa_facility": "captainhandsome/epa-echo-facility-search",
    "fec_campaign_finance": "captainhandsome/fec-campaign-finance-search",
    "florida_new_filings": "captainhandsome/fl-sos-new-filings",
    "florida_officer": "captainhandsome/fl-sunbiz-officer-search",
    "french_company": "captainhandsome/french-company-search",
    "google_play_reviews": "captainhandsome/google-play-reviews-scraper",
    "linkedin_jobs": "captainhandsome/linkedin-public-jobs-search",
    "openfda": "captainhandsome/openfda-search",
    "us_business_entity": "captainhandsome/us-business-entity-search",
    "us_contractor_license": "captainhandsome/us-contractor-license-search",
    "youtube_video": "captainhandsome/youtube-search-scraper",
}

TOOLS_DEFINITION = [
    {
        "name": "google_maps_search",
        "title": "Google Maps Local Business and B2B Lead Extractor",
        "description": "Extract verified commercial business listings, postal addresses, phone numbers, customer review ratings, and canonical websites from Google Maps.\n\nBehavioral Transparency:\n- Execution: Network call executed synchronously in the cloud via Apify Actor 'captainhandsome/google-maps-business-search'.\n- Side Effects: Strictly read-only; does not modify external databases, accounts, or state.\n- Authentication: Requires APIFY_TOKEN environment variable.\n- Latency & Limits: Typical run duration is 15-45 seconds; timeout capped at 120 seconds.\n\nUsage Guidelines:\n- When to use: Use when the user requests local commercial directories, trade contractors, physical retail storefronts, or B2B regional sales leads.\n- When NOT to use: Do not use for employment job listings, corporate regulatory filings, federal procurement awards, or short-term vacation rentals.\n- Named alternatives: Use 'glassdoor_jobs_search' for employer vacancies, 'sec_edgar_filings' for corporate SEC disclosures, 'usaspending_contracts' for government awards, or 'airbnb_listings_search' for vacation rentals.",
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
            "required": [
                "search_query"
            ]
        },
        "outputSchema": {
            "type": "object",
            "properties": {
                "results": {
                    "type": "array",
                    "description": "Collection of verified commercial business entity records extracted from Google Maps.",
                    "items": {
                        "type": "object",
                        "properties": {
                            "title": {
                                "type": "string",
                                "description": "Trading name or legal corporate title of the business."
                            },
                            "phone": {
                                "type": "string",
                                "description": "Primary commercial telephone number with regional area code."
                            },
                            "website": {
                                "type": "string",
                                "description": "Canonical HTTP/HTTPS business website or landing page."
                            },
                            "address": {
                                "type": "string",
                                "description": "Full formatted postal street address including city, state, and ZIP."
                            },
                            "totalScore": {
                                "type": "number",
                                "description": "Aggregate customer review rating on a 1.0 to 5.0 scale."
                            },
                            "reviewsCount": {
                                "type": "integer",
                                "description": "Total count of public Google reviews submitted by customers."
                            },
                            "categoryName": {
                                "type": "string",
                                "description": "Primary industry classification or business trade category."
                            },
                            "url": {
                                "type": "string",
                                "description": "Direct canonical Google Maps place URL."
                            }
                        },
                        "required": [
                            "title",
                            "address"
                        ]
                    }
                }
            },
            "required": [
                "results"
            ]
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
        "description": "Search active employment vacancies, hiring employers, estimated compensation bands, and corporate ratings from Glassdoor.\n\nBehavioral Transparency:\n- Execution: Network call executed synchronously in the cloud via Apify Actor 'captainhandsome/glassdoor-jobs-scraper'.\n- Side Effects: Strictly read-only; does not modify external accounts or submit applications.\n- Authentication: Requires APIFY_TOKEN environment variable.\n- Latency & Limits: Typical run duration is 15-40 seconds; timeout capped at 120 seconds.\n\nUsage Guidelines:\n- When to use: Use when researching active job openings, hiring trends, employer compensation ranges, or workplace ratings for specific professions.\n- When NOT to use: Do not use for local commercial lead generation, corporate financial filings, or live video streaming.\n- Named alternatives: Use 'google_maps_search' for commercial trade directories, 'sec_edgar_filings' for SEC corporate filings, or 'usaspending_contracts' for federal prime contractor records.",
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
            "required": [
                "job_title"
            ]
        },
        "outputSchema": {
            "type": "object",
            "properties": {
                "results": {
                    "type": "array",
                    "description": "Collection of active employment job postings extracted from Glassdoor.",
                    "items": {
                        "type": "object",
                        "properties": {
                            "jobTitle": {
                                "type": "string",
                                "description": "Official employment position or vacancy title."
                            },
                            "companyName": {
                                "type": "string",
                                "description": "Name of the recruiting employer or corporate entity."
                            },
                            "location": {
                                "type": "string",
                                "description": "Geographic workplace location or remote designation."
                            },
                            "salaryEstimate": {
                                "type": "string",
                                "description": "Estimated annual or hourly compensation range when published."
                            },
                            "rating": {
                                "type": "number",
                                "description": "Employer workplace review rating on a 1.0 to 5.0 scale."
                            },
                            "jobUrl": {
                                "type": "string",
                                "description": "Direct canonical URL to the employment application posting."
                            }
                        },
                        "required": [
                            "jobTitle",
                            "companyName"
                        ]
                    }
                }
            },
            "required": [
                "results"
            ]
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
        "description": "Retrieve official United States Securities and Exchange Commission (SEC EDGAR) regulatory filings including 10-K annual reports, 10-Q quarterly reports, and 8-K material events.\n\nBehavioral Transparency:\n- Execution: Network call executed synchronously in the cloud via Apify Actor 'captainhandsome/sec-edgar-filings-search'.\n- Side Effects: Strictly read-only; queries public federal securities disclosures.\n- Authentication: Requires APIFY_TOKEN environment variable.\n- Latency & Limits: Typical run duration is 10-30 seconds; timeout capped at 120 seconds.\n\nUsage Guidelines:\n- When to use: Use for public corporate financial statements, audited balance sheets, executive compensation disclosures, and regulatory material event filings.\n- When NOT to use: Do not use for private non-public company intelligence, real-time stock prices, or local trade vendor lists.\n- Named alternatives: Use 'usaspending_contracts' for federal procurement contracts, 'google_maps_search' for local commercial entities, or 'glassdoor_jobs_search' for hiring trends.",
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
                    "enum": [
                        "10-K",
                        "10-Q",
                        "8-K",
                        "ALL"
                    ],
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
            "required": [
                "ticker"
            ]
        },
        "outputSchema": {
            "type": "object",
            "properties": {
                "results": {
                    "type": "array",
                    "description": "Collection of official SEC EDGAR corporate regulatory filing disclosures.",
                    "items": {
                        "type": "object",
                        "properties": {
                            "formType": {
                                "type": "string",
                                "description": "Regulatory filing form designation code (e.g. 10-K, 10-Q, 8-K)."
                            },
                            "filingDate": {
                                "type": "string",
                                "description": "Official chronological submission date in YYYY-MM-DD format."
                            },
                            "accessionNumber": {
                                "type": "string",
                                "description": "Unique SEC EDGAR document accession identifier."
                            },
                            "companyName": {
                                "type": "string",
                                "description": "Official registered legal name of the filing corporation."
                            },
                            "cik": {
                                "type": "string",
                                "description": "Central Index Key (CIK) ten-digit company identifier assigned by the SEC."
                            },
                            "documentUrl": {
                                "type": "string",
                                "description": "Canonical HTTPS link to the full filing disclosure on SEC.gov."
                            }
                        },
                        "required": [
                            "formType",
                            "filingDate",
                            "documentUrl"
                        ]
                    }
                }
            },
            "required": [
                "results"
            ]
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
        "description": "Search United States federal procurement contracts, defense department awards, and prime agency obligations from the official USAspending database.\n\nBehavioral Transparency:\n- Execution: Network call executed synchronously in the cloud via Apify Actor 'captainhandsome/usaspending-federal-awards'.\n- Side Effects: Strictly read-only; queries public federal procurement databases.\n- Authentication: Requires APIFY_TOKEN environment variable.\n- Latency & Limits: Typical run duration is 10-35 seconds; timeout capped at 120 seconds.\n\nUsage Guidelines:\n- When to use: Use for government contracting intelligence, prime federal vendor tracking, defense obligation amounts, and public procurement research.\n- When NOT to use: Do not use for commercial retail leads, corporate equity SEC filings, or consumer vacation pricing.\n- Named alternatives: Use 'sec_edgar_filings' for corporate 10-K annual reports, 'google_maps_search' for private commercial trade vendors, or 'glassdoor_jobs_search' for company hiring data.",
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
            "required": [
                "recipient_name"
            ]
        },
        "outputSchema": {
            "type": "object",
            "properties": {
                "results": {
                    "type": "array",
                    "description": "Collection of official federal contract and award obligation records.",
                    "items": {
                        "type": "object",
                        "properties": {
                            "recipientName": {
                                "type": "string",
                                "description": "Legal business or institutional name of the award recipient."
                            },
                            "awardingAgency": {
                                "type": "string",
                                "description": "Federal department or agency authorizing the procurement contract."
                            },
                            "obligationAmount": {
                                "type": "number",
                                "description": "Total monetary obligation amount funded by the federal government in USD."
                            },
                            "awardDescription": {
                                "type": "string",
                                "description": "Executive summary statement of the contracted goods or defense services."
                            },
                            "awardDate": {
                                "type": "string",
                                "description": "Action signing date in YYYY-MM-DD format."
                            },
                            "contractId": {
                                "type": "string",
                                "description": "Unique federal procurement award ID (PIID or FAIN)."
                            }
                        },
                        "required": [
                            "recipientName",
                            "obligationAmount"
                        ]
                    }
                }
            },
            "required": [
                "results"
            ]
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
        "description": "Extract real-time live broadcasting streams, viewer counts, channel metadata, and game categories from Twitch.\n\nBehavioral Transparency:\n- Execution: Network call executed synchronously in the cloud via Apify Actor 'captainhandsome/twitch-live-streams-scraper'.\n- Side Effects: Strictly read-only; queries active public Twitch broadcasts.\n- Authentication: Requires APIFY_TOKEN environment variable.\n- Latency & Limits: Typical run duration is 10-25 seconds; timeout capped at 120 seconds.\n\nUsage Guidelines:\n- When to use: Use for live video broadcasting metrics, concurrent esports viewership tracking, influencer intelligence, and gaming category analysis.\n- When NOT to use: Do not use for recorded video-on-demand archives, YouTube channels, or employment job boards.\n- Named alternatives: Use 'glassdoor_jobs_search' for corporate hiring data, 'google_maps_search' for local retail directories, or 'airbnb_listings_search' for travel pricing.",
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
            "type": "object",
            "properties": {
                "results": {
                    "type": "array",
                    "description": "Collection of active real-time Twitch stream broadcast records.",
                    "items": {
                        "type": "object",
                        "properties": {
                            "channelName": {
                                "type": "string",
                                "description": "Twitch username or broadcaster channel handle."
                            },
                            "streamTitle": {
                                "type": "string",
                                "description": "Broadcaster headline title for the active live session."
                            },
                            "gameName": {
                                "type": "string",
                                "description": "Primary game title or stream category."
                            },
                            "viewerCount": {
                                "type": "integer",
                                "description": "Number of concurrent live spectators actively watching the stream."
                            },
                            "language": {
                                "type": "string",
                                "description": "Language code of the broadcast."
                            },
                            "streamUrl": {
                                "type": "string",
                                "description": "Canonical HTTPS stream link to the live broadcast channel."
                            }
                        },
                        "required": [
                            "channelName",
                            "viewerCount"
                        ]
                    }
                }
            },
            "required": [
                "results"
            ]
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
        "description": "Search vacation rental listings, nightly prices, occupancy ratings, and property classifications from Airbnb.\n\nBehavioral Transparency:\n- Execution: Network call executed synchronously in the cloud via Apify Actor 'captainhandsome/airbnb-listings-search'.\n- Side Effects: Strictly read-only; queries public hospitality and vacation listings.\n- Authentication: Requires APIFY_TOKEN environment variable.\n- Latency & Limits: Typical run duration is 15-40 seconds; timeout capped at 120 seconds.\n\nUsage Guidelines:\n- When to use: Use for short-term vacation rental market research, hospitality pricing comparisons, and regional accommodation rate benchmarking.\n- When NOT to use: Do not use for long-term residential apartment leases, MLS residential home sales, or commercial office leasing.\n- Named alternatives: Use 'google_maps_search' for hotel and lodging business contacts, 'glassdoor_jobs_search' for hospitality employment, or 'sec_edgar_filings' for public REIT financial filings.",
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
            "required": [
                "location"
            ]
        },
        "outputSchema": {
            "type": "object",
            "properties": {
                "results": {
                    "type": "array",
                    "description": "Collection of short-term vacation rental property listings extracted from Airbnb.",
                    "items": {
                        "type": "object",
                        "properties": {
                            "listingName": {
                                "type": "string",
                                "description": "Headline property title or host description."
                            },
                            "roomType": {
                                "type": "string",
                                "description": "Accommodation category (e.g. Entire home, Private room, Hotel room)."
                            },
                            "pricePerNight": {
                                "type": "string",
                                "description": "Nightly accommodation tariff rate in local currency."
                            },
                            "rating": {
                                "type": "number",
                                "description": "Aggregate guest cleanliness and satisfaction score on a 1.0 to 5.0 scale."
                            },
                            "reviewCount": {
                                "type": "integer",
                                "description": "Total number of verified guest reviews posted for the property."
                            },
                            "listingUrl": {
                                "type": "string",
                                "description": "Canonical HTTPS link to the Airbnb listing reservation page."
                            }
                        },
                        "required": [
                            "listingName",
                            "pricePerNight"
                        ]
                    }
                }
            },
            "required": [
                "results"
            ]
        },
        "annotations": {
            "readOnlyHint": True,
            "destructiveHint": False,
            "idempotentHint": True,
            "openWorldHint": True
        }
    },
    {'name': 'alabama_business_search', 'title': 'Alabama Business Entity Registry Search', 'description': "Search official Alabama Secretary of State business-entity records by company name, returning entity ID, legal name, entity type, registry status, and location.\n\nBehavioral Transparency:\n- Execution: Network call executed synchronously in the cloud via Apify Actor 'captainhandsome/al-business-entity-search'.\n- Side Effects: Strictly read-only; queries the public Alabama Secretary of State registry.\n- Authentication: Requires APIFY_TOKEN environment variable.\n- Latency & Limits: Typical run duration is 10-30 seconds without detail pages, longer with include_details enabled; timeout capped at 120 seconds.\n\nUsage Guidelines:\n- When to use: Use when verifying an Alabama-registered LLC or corporation, checking entity status, or building a lead list of Alabama businesses by name.\n- When NOT to use: Do not use for Florida, California, or nationwide multi-state lookups, for contractor licensing, or for company officers/registered-agent name searches.\n- Named alternatives: Use 'us_business_entity_search' for a combined Florida/Alabama/Iowa/Wisconsin lookup, 'florida_new_filings_search' for Florida entities, or 'california_contractor_license_search'/'us_contractor_license_search' for contractor licences.", 'inputSchema': {'type': 'object', 'properties': {'search_query': {'type': 'string', 'minLength': 2, 'description': "Full or partial Alabama business name to search (e.g. 'SMITH' or 'Smith Services LLC')."}, 'max_results': {'type': 'integer', 'minimum': 1, 'maximum': 1000, 'default': 10, 'description': 'Maximum number of entity records to return and bill. Defaults to 10.'}, 'include_details': {'type': 'boolean', 'default': False, 'description': "When true, opens each result's detail page to add formation date, registered agent, and registered/principal addresses. Slower; leave off for a fast name-and-status lookup."}}, 'required': ['search_query']}, 'outputSchema': {'type': 'object', 'properties': {'results': {'type': 'array', 'description': 'Collection of Alabama business-entity records matching the search query.', 'items': {'type': 'object', 'properties': {'entity_id': {'type': 'string', 'description': 'Alabama public entity identifier.'}, 'entity_name': {'type': 'string', 'description': 'Business name displayed by the Alabama public registry.'}, 'entity_type': {'type': ['string', 'null'], 'description': 'Registry classification, such as LLC or corporation, when present.'}, 'status': {'type': ['string', 'null'], 'description': 'Current registry status when present (e.g. Exists, Dissolved, Revoked).'}, 'location': {'type': ['string', 'null'], 'description': 'Registry location text when present.'}, 'formation_date': {'type': ['string', 'null'], 'description': 'Date the entity was formed, from the detail record (requires include_details).'}, 'registered_agent': {'type': ['string', 'null'], 'description': "Name of the entity's registered agent (requires include_details)."}, 'principal_address': {'type': ['string', 'null'], 'description': 'Principal place of business, where the state records one (requires include_details).'}}, 'required': ['entity_id', 'entity_name']}}}, 'required': ['results']}, 'annotations': {'readOnlyHint': True, 'destructiveHint': False, 'idempotentHint': True, 'openWorldHint': True}},
    {'name': 'california_contractor_license_search', 'title': 'California CSLB Contractor License Search', 'description': "Search public California Contractors State License Board (CSLB) records by contractor or business name, returning license number, status, city, and name type.\n\nBehavioral Transparency:\n- Execution: Network call executed synchronously in the cloud via Apify Actor 'captainhandsome/ca-contractor-license-search'.\n- Side Effects: Strictly read-only; queries the public CSLB license lookup.\n- Authentication: Requires APIFY_TOKEN environment variable.\n- Latency & Limits: Typical run duration is 10-30 seconds without detail pages, longer with include_details enabled; timeout capped at 120 seconds.\n\nUsage Guidelines:\n- When to use: Use for subcontractor vetting, contractor license verification, or lead building against California licensed contractors and businesses.\n- When NOT to use: Do not use for Oregon-only licence lookups (use 'us_contractor_license_search' with states=['oregon']), business entity/registry searches, or non-contractor trades.\n- Named alternatives: Use 'us_contractor_license_search' to search California and Oregon in one call, or 'alabama_business_search'/'florida_new_filings_search'/'us_business_entity_search' for general business-entity registries rather than contractor licences.", 'inputSchema': {'type': 'object', 'properties': {'search_query': {'type': 'string', 'minLength': 2, 'description': "Full or partial contractor or business name to search in California CSLB records (e.g. 'SMITH' or 'Smith Construction')."}, 'max_results': {'type': 'integer', 'minimum': 1, 'maximum': 1000, 'default': 10, 'description': 'Maximum number of licence records to return and bill. Defaults to 10.'}, 'include_details': {'type': 'boolean', 'default': False, 'description': "When true, opens each licence's CSLB detail page to add issue/expiration dates, business address and phone, classifications, bonding, and workers' comp status. Slower; leave off for a fast name-and-status lookup."}}, 'required': ['search_query']}, 'outputSchema': {'type': 'object', 'properties': {'results': {'type': 'array', 'description': 'Collection of California contractor-license records matching the search query.', 'items': {'type': 'object', 'properties': {'contractor_name': {'type': 'string', 'description': 'Contractor or business name shown in the CSLB result.'}, 'license_number': {'type': 'string', 'description': 'California CSLB contractor-license number.'}, 'name_type': {'type': ['string', 'null'], 'description': 'CSLB classification for the displayed name when present (e.g. print, previous).'}, 'city': {'type': ['string', 'null'], 'description': 'California city displayed for the license record.'}, 'status': {'type': ['string', 'null'], 'description': 'Current license status displayed by CSLB (e.g. Active, Expired).'}, 'business_entity': {'type': ['string', 'null'], 'description': 'Legal form CSLB holds for the licensee, from the licence detail page (requires include_details).'}, 'issue_date': {'type': ['string', 'null'], 'description': 'Date CSLB issued the licence (requires include_details).'}, 'expire_date': {'type': ['string', 'null'], 'description': 'Date the licence expires (requires include_details).'}}, 'required': ['contractor_name', 'license_number']}}}, 'required': ['results']}, 'annotations': {'readOnlyHint': True, 'destructiveHint': False, 'idempotentHint': True, 'openWorldHint': True}},
    {'name': 'clinical_trials_search', 'title': 'ClinicalTrials.gov Study Search', 'description': "Search the official ClinicalTrials.gov registry for interventional and observational studies by condition, intervention, sponsor, or free-text keyword. Returns recruitment status, phase, enrollment, sponsor, and site location detail for each matching study.\n\nBehavioral Transparency:\n- Execution: Network call executed synchronously in the cloud via Apify Actor 'captainhandsome/clinical-trials-search'.\n- Side Effects: Strictly read-only; queries the public ClinicalTrials.gov API v2, no login or write access.\n- Authentication: Requires APIFY_TOKEN environment variable.\n- Latency & Limits: Typical run duration is 10-30 seconds; timeout capped at 120 seconds.\n\nUsage Guidelines:\n- When to use: Use for medical research surveillance, competitive drug-pipeline tracking, patient-recruitment intelligence, or sponsor and trial-portfolio analysis.\n- When NOT to use: Do not use for FDA drug/device approvals or adverse-event data, environmental compliance records, campaign finance, or corporate registry lookups.\n- Named alternatives: Use 'openfda_search' for FDA drug and device safety/approval data, 'epa_facility_search' for environmental compliance, 'fec_campaign_finance_search' for political campaign funding, or 'french_company_search' for the French corporate registry.", 'inputSchema': {'type': 'object', 'properties': {'condition': {'type': 'string', 'minLength': 2, 'description': "Keywords, condition, intervention, sponsor name, or other free-text search expression accepted by ClinicalTrials.gov (e.g. 'Alzheimer disease', 'semaglutide', 'Mayo Clinic')."}, 'status': {'type': 'string', 'enum': ['RECRUITING', 'NOT_YET_RECRUITING', 'ACTIVE_NOT_RECRUITING', 'COMPLETED', 'TERMINATED', 'WITHDRAWN', 'SUSPENDED', 'ENROLLING_BY_INVITATION', 'UNKNOWN'], 'description': 'Optional overall recruitment status filter. Omit to return studies in any status.'}, 'max_results': {'type': 'integer', 'minimum': 1, 'maximum': 100, 'default': 10, 'description': 'Maximum number of study records to retrieve. Defaults to 10.'}}, 'required': ['condition']}, 'outputSchema': {'type': 'object', 'properties': {'results': {'type': 'array', 'description': 'Collection of ClinicalTrials.gov study records matching the search.', 'items': {'type': 'object', 'properties': {'nct_id': {'type': 'string', 'description': 'Unique ClinicalTrials.gov study identifier.'}, 'title': {'type': 'string', 'description': 'Brief public title of the study.'}, 'status': {'type': 'string', 'description': 'Current overall recruitment status, e.g. RECRUITING or COMPLETED.'}, 'phase': {'type': 'string', 'description': 'Trial phase, e.g. PHASE1, PHASE2, PHASE3.'}, 'conditions': {'type': 'string', 'description': 'Comma-separated medical conditions the study addresses.'}, 'sponsor': {'type': 'string', 'description': 'Lead sponsor organization name.'}, 'enrollment': {'type': 'integer', 'description': 'Actual or estimated participant enrollment count.'}, 'url': {'type': 'string', 'description': 'Canonical public ClinicalTrials.gov page for this study.'}}, 'required': ['nct_id', 'title']}}}, 'required': ['results']}, 'annotations': {'readOnlyHint': True, 'destructiveHint': False, 'idempotentHint': True, 'openWorldHint': True}},
    {'name': 'epa_facility_search', 'title': 'EPA ECHO Facility Compliance Search', 'description': "Search the official EPA ECHO service for US regulated facilities by state, city, ZIP, facility name, or NAICS code, and export compliance status, inspection, and penalty data. By default only facilities currently showing a violation are returned (the Actor's violations_only filter defaults to true).\n\nBehavioral Transparency:\n- Execution: Network call executed synchronously in the cloud via Apify Actor 'captainhandsome/epa-echo-facility-search'.\n- Side Effects: Strictly read-only; queries the public EPA ECHO service, no API key or login required.\n- Authentication: Requires APIFY_TOKEN environment variable.\n- Latency & Limits: Typical run duration is 10-35 seconds; timeout capped at 120 seconds.\n\nUsage Guidelines:\n- When to use: Use for environmental compliance due diligence, regulatory risk screening of a facility or region, industry-wide (NAICS) violation surveys, or enforcement/penalty history lookups.\n- When NOT to use: Do not use for corporate registry, campaign finance, clinical trial, or FDA drug/device data.\n- Named alternatives: Use 'clinical_trials_search' for medical studies, 'openfda_search' for FDA drug/device data, 'fec_campaign_finance_search' for political funding, or 'french_company_search' for the French corporate registry.", 'inputSchema': {'type': 'object', 'properties': {'state': {'type': 'string', 'minLength': 2, 'maxLength': 2, 'description': "Two-letter US state code to search within (e.g. 'RI', 'CA')."}, 'facility_name': {'type': 'string', 'description': 'Substring to match against the facility name.'}, 'naics_code': {'type': 'string', 'description': "Industry NAICS code to filter by, e.g. '327910'."}, 'program': {'type': 'string', 'enum': ['A', 'W', 'S', 'R'], 'description': "Environmental program to filter by: 'A' Clean Air Act, 'W' Clean Water Act, 'S' Safe Drinking Water Act, 'R' RCRA hazardous waste. Defaults to 'A' (Clean Air Act) when omitted."}, 'max_results': {'type': 'integer', 'minimum': 1, 'maximum': 100, 'default': 10, 'description': 'Maximum number of facility records to retrieve. Defaults to 10.'}}, 'required': ['state']}, 'outputSchema': {'type': 'object', 'properties': {'results': {'type': 'array', 'description': 'Collection of EPA-regulated facility records with compliance detail.', 'items': {'type': 'object', 'properties': {'registry_id': {'type': 'string', 'description': 'EPA Facility Registry Service ID, the stable key for this facility.'}, 'name': {'type': 'string', 'description': 'Facility name as registered with EPA.'}, 'city': {'type': 'string', 'description': 'Facility city.'}, 'state': {'type': 'string', 'description': 'Two-letter state code.'}, 'naics_codes': {'type': 'string', 'description': 'Space-separated NAICS industry codes for the facility.'}, 'compliance_status': {'type': 'string', 'description': "Overall current compliance status, e.g. 'Violation Identified'."}, 'total_penalties': {'type': 'number', 'description': 'Total dollar amount of penalties assessed against the facility.'}, 'url': {'type': 'string', 'description': 'Direct link to the EPA ECHO detailed facility report.'}}, 'required': ['registry_id', 'name']}}}, 'required': ['results']}, 'annotations': {'readOnlyHint': True, 'destructiveHint': False, 'idempotentHint': True, 'openWorldHint': True}},
    {'name': 'fec_campaign_finance_search', 'title': 'FEC Campaign Finance Search', 'description': "Search the US Federal Election Commission's public register of federal candidates, committees/PACs, or individual campaign contributions. A single call returns one record type only, selected with data_type, because candidates, committees, and contributions carry genuinely different fields.\n\nBehavioral Transparency:\n- Execution: Network call executed synchronously in the cloud via Apify Actor 'captainhandsome/fec-campaign-finance-search'.\n- Side Effects: Strictly read-only; queries the FEC's own public API, no login or API key required.\n- Authentication: Requires APIFY_TOKEN environment variable.\n- Latency & Limits: Typical run duration is 10-30 seconds; timeout capped at 120 seconds.\n\nUsage Guidelines:\n- When to use: Use for political campaign research, candidate and PAC vetting, donor/contribution geography and industry analysis, or election-cycle fundraising tracking.\n- When NOT to use: Do not use for corporate SEC filings, environmental compliance, clinical trials, or FDA drug/device data. Contributor street addresses are never returned (deliberately excluded upstream).\n- Named alternatives: Use 'french_company_search' for French corporate registry data, 'epa_facility_search' for environmental compliance, 'clinical_trials_search' for medical studies, or 'openfda_search' for FDA drug/device data.", 'inputSchema': {'type': 'object', 'properties': {'data_type': {'type': 'string', 'enum': ['candidates', 'committees', 'contributions'], 'default': 'candidates', 'description': "Which register to search: federal candidates, committees and PACs, or individual contributions. Defaults to 'candidates'."}, 'name': {'type': 'string', 'description': 'Candidate, committee, or contributor name to search for, depending on data_type.'}, 'state': {'type': 'string', 'description': "Two-letter state code. For contributions this filters the contributor's state, not the recipient's."}, 'party': {'type': 'string', 'description': "Three-letter party code, e.g. 'DEM', 'REP', 'LIB'. Applies to candidates only."}, 'office': {'type': 'string', 'enum': ['H', 'S', 'P'], 'description': "Office sought: 'H' House, 'S' Senate, 'P' President. Applies to candidates only."}, 'max_results': {'type': 'integer', 'minimum': 1, 'maximum': 100, 'default': 10, 'description': 'Maximum number of records to retrieve. Defaults to 10.'}}, 'required': []}, 'outputSchema': {'type': 'object', 'properties': {'results': {'type': 'array', 'description': 'Collection of FEC candidate, committee, or contribution records.', 'items': {'type': 'object', 'properties': {'record_type': {'type': 'string', 'description': 'Which search produced this row: candidate, committee, or contribution.'}, 'id': {'type': 'string', 'description': 'FEC identifier for the row (candidate ID, committee ID, or transaction sub_id).'}, 'name': {'type': 'string', 'description': 'Registered name of the candidate or committee. Null on contribution rows.'}, 'party': {'type': 'string', 'description': 'Full party name as filed.'}, 'office': {'type': 'string', 'description': 'Office sought, expanded to a readable label. Candidate rows only.'}, 'state': {'type': 'string', 'description': 'Two-letter state code relevant to the record.'}, 'district': {'type': 'string', 'description': 'Congressional district. House candidates only.'}, 'url': {'type': 'string', 'description': 'Canonical FEC.gov URL for the record.'}}, 'required': ['record_type', 'id']}}}, 'required': ['results']}, 'annotations': {'readOnlyHint': True, 'destructiveHint': False, 'idempotentHint': True, 'openWorldHint': True}},
    {'name': 'florida_new_filings_search', 'title': 'Florida Sunbiz Business Entity Search', 'description': "Search the Florida Division of Corporations (Sunbiz) business registry by company name, returning entity name, document number, status, and entity type.\n\nBehavioral Transparency:\n- Execution: Network call executed synchronously in the cloud via Apify Actor 'captainhandsome/fl-sos-new-filings'.\n- Side Effects: Strictly read-only; queries the public Sunbiz search pages.\n- Authentication: Requires APIFY_TOKEN environment variable.\n- Latency & Limits: Typical run duration is 10-30 seconds without detail pages, longer with include_details enabled; timeout capped at 120 seconds.\n\nUsage Guidelines:\n- When to use: Use for Florida LLC/corporation lookup by company name, due-diligence checks, or monitoring new Florida business filings.\n- When NOT to use: Do not use to search by a person's or officer's name (use 'florida_officer_search' instead), for other states, or for contractor licences.\n- Named alternatives: Use 'florida_officer_search' to find companies tied to a person or registered agent, 'us_business_entity_search' for a multi-state lookup that includes Florida, or 'alabama_business_search' for Alabama-only records.", 'inputSchema': {'type': 'object', 'properties': {'search_query': {'type': 'string', 'minLength': 2, 'description': "Full or partial Florida business name to search on Sunbiz (e.g. 'SMITH' or 'Smith Services LLC')."}, 'max_results': {'type': 'integer', 'minimum': 1, 'maximum': 1000, 'default': 10, 'description': 'Maximum number of entity records to return and bill. Defaults to 10.'}, 'include_details': {'type': 'boolean', 'default': False, 'description': "When true, opens each result's Sunbiz detail page to add date filed, FEI/EIN, registered agent, principal/mailing addresses, officers, and annual-report history. Slower; leave off for a fast name-and-status lookup."}}, 'required': ['search_query']}, 'outputSchema': {'type': 'object', 'properties': {'results': {'type': 'array', 'description': 'Collection of Florida Sunbiz business-entity records matching the search query.', 'items': {'type': 'object', 'properties': {'entity_name': {'type': 'string', 'description': 'Legal entity name displayed in the Sunbiz result.'}, 'document_number': {'type': 'string', 'description': 'Florida Division of Corporations document number.'}, 'status': {'type': ['string', 'null'], 'description': 'Entity status displayed in the Sunbiz result (e.g. Active, Inactive).'}, 'entity_type': {'type': ['string', 'null'], 'description': 'Florida registry classification, such as a domestic or foreign LLC or corporation.'}, 'date_filed': {'type': ['string', 'null'], 'description': 'Date the entity was filed with the Florida Division of Corporations (requires include_details).'}, 'fei_ein': {'type': ['string', 'null'], 'description': 'Federal employer identification number on file with the state, where recorded (requires include_details).'}, 'registered_agent': {'type': ['string', 'null'], 'description': "Name of the entity's Florida registered agent (requires include_details)."}, 'principal_address': {'type': ['string', 'null'], 'description': 'Principal place of business on file with the state (requires include_details).'}}, 'required': ['entity_name', 'document_number']}}}, 'required': ['results']}, 'annotations': {'readOnlyHint': True, 'destructiveHint': False, 'idempotentHint': True, 'openWorldHint': True}},
    {'name': 'florida_officer_search', 'title': 'Florida Sunbiz Officer and Registered Agent Search', 'description': "Search the Florida Sunbiz registry by an officer, director, or registered-agent name and return every Florida company tied to that person, with entity name and document number.\n\nBehavioral Transparency:\n- Execution: Network call executed synchronously in the cloud via Apify Actor 'captainhandsome/fl-sunbiz-officer-search'.\n- Side Effects: Strictly read-only; queries the public Sunbiz search pages.\n- Authentication: Requires APIFY_TOKEN environment variable.\n- Latency & Limits: Typical run duration is 10-30 seconds without detail pages, longer with include_details enabled (one extra page load per matched company); timeout capped at 120 seconds.\n\nUsage Guidelines:\n- When to use: Use to find every Florida company associated with a specific person's name (officer, director, or registered agent), for background research or ownership mapping.\n- When NOT to use: Do not use to search by company name (use 'florida_new_filings_search' instead), for other states, or for contractor licences.\n- Named alternatives: Use 'florida_new_filings_search' to look up a Florida company by its own name, or 'us_business_entity_search' for a multi-state company-name lookup.", 'inputSchema': {'type': 'object', 'properties': {'search_query': {'type': 'string', 'minLength': 2, 'description': "Full or partial officer, director, or registered-agent person name to search on Sunbiz (e.g. 'SMITH' or 'Smith, John')."}, 'max_results': {'type': 'integer', 'minimum': 1, 'maximum': 1000, 'default': 10, 'description': 'Maximum number of officer-to-entity records to return and bill. Defaults to 10.'}, 'include_details': {'type': 'boolean', 'default': False, 'description': "When true, opens each matched company's Sunbiz detail page to add status, filing date, FEI/EIN, addresses, the full officer list, and annual-report history. Slower; leave off for a fast person-to-company lookup."}}, 'required': ['search_query']}, 'outputSchema': {'type': 'object', 'properties': {'results': {'type': 'array', 'description': 'Collection of Florida officer/registered-agent-to-entity records matching the search query.', 'items': {'type': 'object', 'properties': {'officer_name': {'type': 'string', 'description': 'Officer or registered-agent name shown in Sunbiz.'}, 'entity_name': {'type': 'string', 'description': 'Florida business entity linked to the officer or agent.'}, 'document_number': {'type': ['string', 'null'], 'description': 'Florida Division of Corporations document number.'}, 'detail_url': {'type': ['string', 'null'], 'description': "Direct link to the company's Sunbiz detail page for audit against the state registry."}, 'entity_type': {'type': ['string', 'null'], 'description': 'Registry classification, such as Florida LLC or Foreign Profit Corporation (requires include_details).'}, 'status': {'type': ['string', 'null'], 'description': 'Current Florida registration status, normally ACTIVE or INACTIVE (requires include_details).'}, 'date_filed': {'type': ['string', 'null'], 'description': 'Date the entity was first filed with the Florida Division of Corporations (requires include_details).'}, 'principal_address': {'type': ['string', 'null'], 'description': 'Principal place of business on file (requires include_details).'}}, 'required': ['officer_name', 'entity_name']}}}, 'required': ['results']}, 'annotations': {'readOnlyHint': True, 'destructiveHint': False, 'idempotentHint': True, 'openWorldHint': True}},
    {'name': 'french_company_search', 'title': 'French Company Registry Search (SIRENE)', 'description': "Search France's official company register (SIRENE/INSEE) by name, activity, department, or postal code, and export SIREN/SIRET identifiers, legal status, headquarters address, workforce, revenue, and officers.\n\nBehavioral Transparency:\n- Execution: Network call executed synchronously in the cloud via Apify Actor 'captainhandsome/french-company-search'.\n- Side Effects: Strictly read-only; queries the French public company-data API backed by the SIRENE register, no login or API key required.\n- Authentication: Requires APIFY_TOKEN environment variable.\n- Latency & Limits: Typical run duration is 10-30 seconds; timeout capped at 120 seconds.\n\nUsage Guidelines:\n- When to use: Use for French corporate due diligence, company/officer lookups, industry (NAF) or regional market surveys, or B2B vendor verification in France.\n- When NOT to use: Do not use for US environmental compliance, US campaign finance, clinical trials, or FDA drug/device data.\n- Named alternatives: Use 'fec_campaign_finance_search' for US political funding, 'epa_facility_search' for environmental compliance, 'clinical_trials_search' for medical studies, or 'openfda_search' for FDA drug/device data.", 'inputSchema': {'type': 'object', 'properties': {'query': {'type': 'string', 'minLength': 2, 'description': "Company name, trade name, or keyword to search for (e.g. 'boulangerie', 'Airbus')."}, 'department': {'type': 'string', 'description': "French department code to filter by, e.g. '75' or '13'."}, 'naf_code': {'type': 'string', 'description': "French NAF/APE economic activity code to filter by, e.g. '62.01Z'."}, 'active_only': {'type': 'boolean', 'default': True, 'description': 'Return only companies currently marked active. Defaults to true.'}, 'max_results': {'type': 'integer', 'minimum': 1, 'maximum': 100, 'default': 10, 'description': 'Maximum number of company records to retrieve. Defaults to 10.'}}, 'required': ['query']}, 'outputSchema': {'type': 'object', 'properties': {'results': {'type': 'array', 'description': 'Collection of French company records from the SIRENE register.', 'items': {'type': 'object', 'properties': {'siren': {'type': 'string', 'description': '9-digit SIREN company identifier.'}, 'name': {'type': 'string', 'description': 'Organization or company name as published by the source.'}, 'legal_name': {'type': 'string', 'description': 'Registered legal name of the company.'}, 'status': {'type': 'string', 'description': "Current company status, e.g. 'active'."}, 'naf_code': {'type': 'string', 'description': 'Main NAF/APE economic activity code.'}, 'hq_city': {'type': 'string', 'description': 'Headquarters city.'}, 'employees': {'type': 'string', 'description': 'Company-wide workforce size band.'}, 'revenue': {'type': 'number', 'description': 'Most recently reported annual revenue.'}}, 'required': ['siren', 'name']}}}, 'required': ['results']}, 'annotations': {'readOnlyHint': True, 'destructiveHint': False, 'idempotentHint': True, 'openWorldHint': True}},
    {'name': 'google_play_reviews_search', 'title': 'Google Play App Reviews Search', 'description': "Extract public Google Play Store reviews for one or more Android apps, including star rating, review text, reviewer name, developer replies, and app-level metadata (rating breakdown, installs, category, developer).\n\nBehavioral Transparency:\n- Execution: Network call executed synchronously in the cloud via Apify Actor 'captainhandsome/google-play-reviews-scraper'.\n- Side Effects: Strictly read-only; does not modify any Google Play account, app listing, or review.\n- Authentication: Requires APIFY_TOKEN environment variable.\n- Latency & Limits: Typical run duration is 15-45 seconds per app; timeout capped at 120 seconds.\n\nUsage Guidelines:\n- When to use: Use for app-store sentiment research, competitor review monitoring, feature/complaint mining, or tracking developer response rates across one or more Android apps.\n- When NOT to use: Do not use for iOS App Store reviews, general web search, or employment/job data.\n- Named alternatives: Use 'linkedin_jobs_search' for hiring/job listings or 'youtube_video_search' for video content discovery; neither covers app-store review data.", 'inputSchema': {'type': 'object', 'properties': {'app_ids': {'type': 'array', 'items': {'type': 'string'}, 'minItems': 1, 'maxItems': 25, 'description': "Android package IDs or full Google Play app URLs to pull reviews for, up to 25 (e.g. ['com.spotify.music', 'com.google.android.youtube'])."}, 'max_results': {'type': 'integer', 'minimum': 1, 'maximum': 200, 'default': 25, 'description': 'Maximum number of review records to return per app. Defaults to 25.'}, 'scores': {'type': 'array', 'items': {'type': 'integer', 'minimum': 1, 'maximum': 5}, 'description': 'Optional star-rating filter (1-5). Keep only reviews matching any of these ratings, e.g. [1, 2] for negative reviews. Omit to return all ratings.'}, 'keywords': {'type': 'array', 'items': {'type': 'string'}, 'description': 'Optional list of words or phrases; keep only reviews whose text contains any of them (case-insensitive). Omit to skip this filter.'}, 'recent_days': {'type': 'integer', 'minimum': 1, 'description': 'Optional recency filter: keep only reviews posted within this many days of now (e.g. 30). Omit to return reviews of any age.'}}, 'required': ['app_ids']}, 'outputSchema': {'type': 'object', 'properties': {'results': {'type': 'array', 'description': 'Collection of Google Play review records extracted for the requested app(s).', 'items': {'type': 'object', 'properties': {'app_id': {'type': 'string', 'description': 'Android package identifier for the reviewed app.'}, 'app_title': {'type': ['string', 'null'], 'description': 'Display name of the reviewed app on Google Play.'}, 'user_name': {'type': ['string', 'null'], 'description': 'Public reviewer display name.'}, 'score': {'type': ['integer', 'null'], 'description': 'Integer star rating from one to five.'}, 'text': {'type': ['string', 'null'], 'description': 'Full public review body.'}, 'reviewed_at': {'type': ['string', 'null'], 'description': 'ISO 8601 timestamp when the review was posted.'}, 'thumbs_up': {'type': ['integer', 'null'], 'description': 'Number of users who marked the review helpful.'}, 'developer_reply': {'type': ['string', 'null'], 'description': 'Public developer response text when present.'}}, 'required': ['app_id', 'text']}}}, 'required': ['results']}, 'annotations': {'readOnlyHint': True, 'destructiveHint': False, 'idempotentHint': True, 'openWorldHint': True}},
    {'name': 'linkedin_jobs_search', 'title': 'LinkedIn Public Job Listings Search', 'description': "Search public LinkedIn job postings by keyword and location without logging in, returning role title, hiring company, location, posting date, and job URL.\n\nBehavioral Transparency:\n- Execution: Network call executed synchronously in the cloud via Apify Actor 'captainhandsome/linkedin-public-jobs-search'.\n- Side Effects: Strictly read-only; does not log in, apply to jobs, or modify any LinkedIn account.\n- Authentication: Requires APIFY_TOKEN environment variable.\n- Latency & Limits: Typical run duration is 15-40 seconds; timeout capped at 120 seconds.\n\nUsage Guidelines:\n- When to use: Use for hiring-trend research, talent-market mapping, competitor headcount signals, or sourcing public job openings by role and location.\n- When NOT to use: Do not use for LinkedIn people/profile search, private candidate data, or submitting job applications.\n- Named alternatives: Use 'glassdoor_jobs_search' for Glassdoor's own listings and employer ratings, or 'google_play_reviews_search'/'youtube_video_search' for app-review or video data instead of hiring data.", 'inputSchema': {'type': 'object', 'properties': {'search_query': {'type': 'string', 'minLength': 2, 'description': "Job title, skill, or keyword to search in public LinkedIn job listings (e.g. 'data engineer' or 'registered nurse')."}, 'location': {'type': 'string', 'default': '', 'description': "City, region, or country used to localize results (e.g. 'Seattle, WA'). Defaults to all locations if empty."}, 'max_results': {'type': 'integer', 'minimum': 1, 'maximum': 200, 'default': 10, 'description': 'Maximum number of job listings to retrieve. Defaults to 10.'}, 'include_details': {'type': 'boolean', 'default': False, 'description': 'When true, opens each job posting to add seniority level, employment type, job function, industries, applicant count, and full job description. Costs one extra request per job, so runs take noticeably longer. Defaults to false.'}}, 'required': ['search_query']}, 'outputSchema': {'type': 'object', 'properties': {'results': {'type': 'array', 'description': 'Collection of public LinkedIn job listing records.', 'items': {'type': 'object', 'properties': {'title': {'type': ['string', 'null'], 'description': 'Job posting title.'}, 'company': {'type': ['string', 'null'], 'description': 'Hiring company name.'}, 'location': {'type': ['string', 'null'], 'description': 'Workplace location as displayed on the posting.'}, 'url': {'type': ['string', 'null'], 'description': 'Direct canonical URL to the job listing.'}, 'posted_at': {'type': ['string', 'null'], 'description': 'Source-provided job posting date.'}, 'posted_at_timestamp': {'type': ['string', 'null'], 'description': 'posted_at parsed into a UTC ISO 8601 timestamp, when recognizable.'}, 'job_id': {'type': ['string', 'null'], 'description': 'Numeric LinkedIn job posting ID, stable across runs.'}, 'company_url': {'type': ['string', 'null'], 'description': "URL of the hiring organization's LinkedIn page."}}, 'required': ['title', 'company', 'url']}}}, 'required': ['results']}, 'annotations': {'readOnlyHint': True, 'destructiveHint': False, 'idempotentHint': True, 'openWorldHint': True}},
    {'name': 'openfda_search', 'title': 'openFDA Drug and Device Search', 'description': "Search official openFDA datasets for drug labels, drug approvals (Drugs@FDA), adverse events (FAERS), and drug, device, or food recalls. Returns normalized, flat records through one consistent interface.\n\nBehavioral Transparency:\n- Execution: Network call executed synchronously in the cloud via Apify Actor 'captainhandsome/openfda-search'.\n- Side Effects: Strictly read-only; queries the public openFDA API, no API key or login required.\n- Authentication: Requires APIFY_TOKEN environment variable.\n- Latency & Limits: Typical run duration is 10-30 seconds; timeout capped at 120 seconds.\n\nUsage Guidelines:\n- When to use: Use for drug/device safety surveillance, regulatory approval history, adverse-event monitoring, or recall tracking.\n- When NOT to use: Do not use for clinical trial recruitment data (use 'clinical_trials_search'), environmental compliance, campaign finance, or corporate registry lookups.\n- Named alternatives: Use 'clinical_trials_search' for ClinicalTrials.gov study data, 'epa_facility_search' for environmental compliance, 'fec_campaign_finance_search' for political funding, or 'french_company_search' for the French corporate registry.", 'inputSchema': {'type': 'object', 'properties': {'dataset': {'type': 'string', 'enum': ['drug_label', 'drug_approval', 'drug_event', 'drug_recall', 'device_recall', 'food_recall'], 'default': 'drug_approval', 'description': "Which openFDA dataset to search. Defaults to 'drug_approval'."}, 'search': {'type': 'string', 'minLength': 2, 'description': 'openFDA query. A plain word works (e.g. \'semaglutide\'), or target a field, e.g. \'openfda.manufacturer_name:"Pfizer"\'.'}, 'include_details': {'type': 'boolean', 'default': False, 'description': "Also look up each result's product NDC to add labeler, marketing category, and DEA schedule. Costs one extra request per 20 records. Defaults to false."}, 'max_results': {'type': 'integer', 'minimum': 1, 'maximum': 100, 'default': 10, 'description': 'Maximum number of records to retrieve. Defaults to 10.'}}, 'required': ['search']}, 'outputSchema': {'type': 'object', 'properties': {'results': {'type': 'array', 'description': 'Collection of openFDA records matching the search.', 'items': {'type': 'object', 'properties': {'dataset': {'type': 'string', 'description': 'Which openFDA dataset produced this row.'}, 'id': {'type': 'string', 'description': 'Primary identifier for the row (SPL id, application number, safety report id, or recall number).'}, 'brand_name': {'type': 'string', 'description': 'FDA-reported brand or proprietary name.'}, 'generic_name': {'type': 'string', 'description': 'FDA-reported generic or nonproprietary name.'}, 'manufacturer': {'type': 'string', 'description': 'FDA-reported manufacturer name.'}, 'substance': {'type': 'string', 'description': 'Active substance names, comma separated.'}, 'route': {'type': 'string', 'description': 'Route(s) of administration, comma separated.'}, 'application_number': {'type': 'string', 'description': 'FDA application number (NDA, ANDA, or BLA) the product is marketed under.'}}, 'required': ['dataset', 'id']}}}, 'required': ['results']}, 'annotations': {'readOnlyHint': True, 'destructiveHint': False, 'idempotentHint': True, 'openWorldHint': True}},
    {'name': 'us_business_entity_search', 'title': 'US Multi-State Business Entity Search', 'description': "Search public Secretary of State business registries across Florida, Alabama, Iowa, and Wisconsin in one call, returning a normalized, source-tagged record per state match.\n\nBehavioral Transparency:\n- Execution: Network call executed synchronously in the cloud via Apify Actor 'captainhandsome/us-business-entity-search'.\n- Side Effects: Strictly read-only; queries public state business registries.\n- Authentication: Requires APIFY_TOKEN environment variable.\n- Latency & Limits: Typical run duration is 15-45 seconds without detail pages, longer with include_details enabled and with more states selected; timeout capped at 120 seconds.\n\nUsage Guidelines:\n- When to use: Use when a company name lookup should span multiple states at once, or when the entity's state of registration is unknown among Florida, Alabama, Iowa, or Wisconsin.\n- When NOT to use: Do not use for a single known state where a dedicated tool exists and is faster (e.g. 'alabama_business_search' or 'florida_new_filings_search'), for states outside this coverage, for officer/person-name lookups (use 'florida_officer_search'), or for contractor licences.\n- Named alternatives: Use 'alabama_business_search' or 'florida_new_filings_search' for a single-state lookup, 'florida_officer_search' for a person-to-company search, or 'us_contractor_license_search'/'california_contractor_license_search' for licensed contractors rather than general business entities.", 'inputSchema': {'type': 'object', 'properties': {'search_query': {'type': 'string', 'minLength': 2, 'description': "Full or partial business name to search across the selected state registries (e.g. 'SMITH' or 'Smith Services LLC')."}, 'states': {'type': 'array', 'items': {'type': 'string', 'enum': ['florida', 'alabama', 'iowa', 'wisconsin']}, 'minItems': 1, 'uniqueItems': True, 'default': ['florida', 'alabama', 'iowa', 'wisconsin'], 'description': 'State registries to search. Defaults to all four supported states; narrow this to speed up a run when the state is already known.'}, 'max_results': {'type': 'integer', 'minimum': 1, 'maximum': 2000, 'default': 10, 'description': 'Maximum number of normalized entity records to return and bill across all selected states. Defaults to 10.'}, 'include_details': {'type': 'boolean', 'default': False, 'description': "When true, opens each result's detail page to add formation date, registered agent, officers, and both address blocks. Adds one request per record and per state; leave off for a fast lookup."}}, 'required': ['search_query']}, 'outputSchema': {'type': 'object', 'properties': {'results': {'type': 'array', 'description': 'Collection of normalized, source-tagged business-entity records matching the search query.', 'items': {'type': 'object', 'properties': {'source': {'type': ['string', 'null'], 'description': 'State registry that produced the record (florida, alabama, iowa, or wisconsin).'}, 'entity_name': {'type': ['string', 'null'], 'description': 'Legal entity name displayed by the source registry.'}, 'entity_id': {'type': ['string', 'null'], 'description': 'Public document, filing, or entity identifier from the source registry.'}, 'status': {'type': ['string', 'null'], 'description': 'Registry status when available.'}, 'entity_type': {'type': ['string', 'null'], 'description': 'Registry entity classification when available.'}, 'location': {'type': ['string', 'null'], 'description': 'Registry location text when available.'}, 'date_filed': {'type': ['string', 'null'], 'description': 'Date the entity was filed, when the source registry records one.'}, 'registered_agent': {'type': ['string', 'null'], 'description': "Name of the entity's registered agent, where recorded (requires include_details on most sources)."}}, 'required': ['source', 'entity_name']}}}, 'required': ['results']}, 'annotations': {'readOnlyHint': True, 'destructiveHint': False, 'idempotentHint': True, 'openWorldHint': True}},
    {'name': 'us_contractor_license_search', 'title': 'US Multi-State Contractor License Search', 'description': "Search California CSLB and Oregon CCB contractor-license records from one call by business, qualifier, or person name, returning a normalized, source-tagged record per state match.\n\nBehavioral Transparency:\n- Execution: Network call executed synchronously in the cloud via Apify Actor 'captainhandsome/us-contractor-license-search'.\n- Side Effects: Strictly read-only; queries public state contractor-license boards.\n- Authentication: Requires APIFY_TOKEN environment variable.\n- Latency & Limits: Typical run duration is 15-45 seconds without detail pages, longer with include_details enabled and with more states selected; timeout capped at 120 seconds.\n\nUsage Guidelines:\n- When to use: Use for contractor vetting or lead building across California and Oregon in one call, or when it is not yet known which of the two states holds the licence.\n- When NOT to use: Do not use for a single known state where a dedicated tool is faster (e.g. 'california_contractor_license_search'), for states outside California/Oregon, or for general business-entity (non-licence) registry lookups.\n- Named alternatives: Use 'california_contractor_license_search' for a California-only lookup, or 'alabama_business_search'/'florida_new_filings_search'/'us_business_entity_search' for general business-entity registries rather than contractor licences.", 'inputSchema': {'type': 'object', 'properties': {'search_query': {'type': 'string', 'minLength': 2, 'description': "Business, qualifier, or person name to look up in the selected contractor-license registries (e.g. 'SMITH' or 'Smith Construction')."}, 'states': {'type': 'array', 'items': {'type': 'string', 'enum': ['california', 'oregon']}, 'minItems': 1, 'uniqueItems': True, 'default': ['california', 'oregon'], 'description': 'State licence sources to search. Defaults to both California and Oregon; narrow this to speed up a run when the state is already known.'}, 'max_results': {'type': 'integer', 'minimum': 1, 'maximum': 10000, 'default': 10, 'description': 'Maximum number of licence records to return and bill across all selected states. Defaults to 10.'}, 'include_details': {'type': 'boolean', 'default': False, 'description': "When true, opens each licence's detail page to add bonding, insurance, workers' compensation, classifications, disciplinary history, and issue/expiry dates. Adds one request per record; leave off for a fast lookup."}}, 'required': ['search_query']}, 'outputSchema': {'type': 'object', 'properties': {'results': {'type': 'array', 'description': 'Collection of normalized, source-tagged contractor-license records matching the search query.', 'items': {'type': 'object', 'properties': {'source': {'type': ['string', 'null'], 'description': 'State licence registry that produced the record (california or oregon).'}, 'business_name': {'type': ['string', 'null'], 'description': 'Business name value returned by the upstream source.'}, 'contractor_name': {'type': ['string', 'null'], 'description': 'Contractor or business name shown in the result.'}, 'license_number': {'type': ['string', 'null'], 'description': 'Public registry license identifier.'}, 'status': {'type': ['string', 'null'], 'description': 'Current status reported by the source registry.'}, 'city': {'type': ['string', 'null'], 'description': 'City displayed for the license record.'}, 'name_type': {'type': ['string', 'null'], 'description': 'Structured name-type value returned by the upstream source.'}, 'business_entity': {'type': ['string', 'null'], 'description': 'Legal form held for the licensee, from the licence detail page (requires include_details).'}}, 'required': ['source']}}}, 'required': ['results']}, 'annotations': {'readOnlyHint': True, 'destructiveHint': False, 'idempotentHint': True, 'openWorldHint': True}},
    {'name': 'youtube_video_search', 'title': 'YouTube Video Search', 'description': "Search public YouTube videos by keyword, returning title, channel, canonical video URL, view count, duration, and publish date - no YouTube Data API quota required.\n\nBehavioral Transparency:\n- Execution: Network call executed synchronously in the cloud via Apify Actor 'captainhandsome/youtube-search-scraper'.\n- Side Effects: Strictly read-only; does not modify any YouTube account, subscription, or playlist.\n- Authentication: Requires APIFY_TOKEN environment variable.\n- Latency & Limits: Typical run duration is 10-30 seconds; timeout capped at 120 seconds.\n\nUsage Guidelines:\n- When to use: Use for content research, competitor video monitoring, trend discovery, or building a list of videos on a topic.\n- When NOT to use: Do not use for retrieving a video's transcript/captions, channel analytics dashboards, or non-YouTube platforms.\n- Named alternatives: Use 'google_play_reviews_search' for app-store sentiment or 'linkedin_jobs_search' for job-market data; neither covers video content.", 'inputSchema': {'type': 'object', 'properties': {'search_query': {'type': 'string', 'minLength': 2, 'description': "Keyword or phrase to search for on YouTube (e.g. 'small business marketing')."}, 'max_results': {'type': 'integer', 'minimum': 1, 'maximum': 500, 'default': 25, 'description': 'Maximum number of unique video records to return. Defaults to 25.'}}, 'required': ['search_query']}, 'outputSchema': {'type': 'object', 'properties': {'results': {'type': 'array', 'description': 'Collection of YouTube video search result records.', 'items': {'type': 'object', 'properties': {'title': {'type': ['string', 'null'], 'description': 'Public title of the video.'}, 'video_url': {'type': ['string', 'null'], 'description': 'Canonical YouTube watch-page URL.'}, 'channel_name': {'type': ['string', 'null'], 'description': 'Public name of the channel that published the video.'}, 'channel_url': {'type': ['string', 'null'], 'description': 'Public YouTube channel URL when available.'}, 'views': {'type': ['string', 'null'], 'description': 'Human-readable view count displayed in search results.'}, 'view_count': {'type': ['integer', 'null'], 'description': "'views' parsed into a number, handling K/M/B suffixes and comma grouping."}, 'published': {'type': ['string', 'null'], 'description': "Relative publication age displayed in search results (e.g. '2 years ago')."}, 'duration': {'type': ['string', 'null'], 'description': 'Displayed video duration in clock format.'}}, 'required': ['title', 'video_url']}}}, 'required': ['results']}, 'annotations': {'readOnlyHint': True, 'destructiveHint': False, 'idempotentHint': True, 'openWorldHint': True}},
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
                        "version": "1.0.6"
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
                # Every key below must exist in the target Actor's input_schema.json.
                # Apify IGNORES unknown input keys rather than rejecting them, so a
                # wrong name does not fail - the Actor silently runs on its DEFAULT
                # input and returns confident, irrelevant data. Five of these six
                # tools were doing exactly that (2026-09-13): google_maps sent
                # "search_terms", glassdoor sent "keyword"/"max_results", sec_edgar
                # sent "company_or_ticker"/"form_type", usaspending sent
                # "recipient_search_text", twitch sent "game"/"language" - none of
                # which the Actors accept. Verify against the live schema before
                # adding or renaming anything here.
                if tool_name == "google_maps_search":
                    query = tool_args.get("search_query")
                    loc = tool_args.get("location", "")
                    limit = int(tool_args.get("max_results", 10))
                    # location MUST be sent even when empty: the Actor defaults it to
                    # "New York, NY", which would otherwise be appended to the caller's
                    # query and silently relocate every search.
                    data = run_actor_sync(ACTORS["google_maps"],
                                          {"search_query": query, "location": loc, "max_items": limit})
                elif tool_name == "glassdoor_jobs_search":
                    title = tool_args.get("job_title")
                    loc = tool_args.get("location", "")
                    limit = int(tool_args.get("max_results", 10))
                    data = run_actor_sync(ACTORS["glassdoor_jobs"],
                                          {"search_query": title, "location": loc, "max_items": limit})
                elif tool_name == "sec_edgar_filings":
                    ticker = tool_args.get("ticker")
                    form = tool_args.get("form_type", "10-K")
                    limit = int(tool_args.get("max_results", 5))
                    # forms is an ARRAY on the Actor, not a bare string.
                    data = run_actor_sync(ACTORS["sec_edgar"],
                                          {"company": ticker, "forms": [form] if form else None,
                                           "max_items": limit})
                elif tool_name == "usaspending_contracts":
                    rec = tool_args.get("recipient_name")
                    limit = int(tool_args.get("max_results", 10))
                    data = run_actor_sync(ACTORS["usaspending"],
                                          {"award_type": "contracts", "keywords": rec, "max_items": limit})
                elif tool_name == "twitch_live_streams":
                    game = tool_args.get("game_name", "")
                    limit = int(tool_args.get("max_results", 10))
                    # The Actor has no language input; "language" was silently dropped
                    # and is intentionally not forwarded rather than faked.
                    data = run_actor_sync(ACTORS["twitch_streams"],
                                          {"search_query": game, "max_items": limit})
                elif tool_name == "airbnb_listings_search":
                    loc = tool_args.get("location")
                    limit = int(tool_args.get("max_results", 10))
                    data = run_actor_sync(ACTORS["airbnb"], {"location": loc, "max_items": limit})
                elif tool_name == "alabama_business_search":
                    _search_query = tool_args.get("search_query")
                    _max_results = tool_args.get("max_results", 10)
                    _include_details = tool_args.get("include_details", False)
                    _payload = {"max_items": min(int(_max_results or 10), 100), "include_details": _include_details}
                    if _search_query is not None: _payload["search_terms"] = [_search_query] if not isinstance(_search_query, list) else _search_query
                    data = run_actor_sync(ACTORS["alabama_business"], _payload)
                elif tool_name == "california_contractor_license_search":
                    _search_query = tool_args.get("search_query")
                    _max_results = tool_args.get("max_results", 10)
                    _include_details = tool_args.get("include_details", False)
                    _payload = {"max_items": min(int(_max_results or 10), 100), "include_details": _include_details}
                    if _search_query is not None: _payload["search_terms"] = [_search_query] if not isinstance(_search_query, list) else _search_query
                    data = run_actor_sync(ACTORS["california_contractor_license"], _payload)
                elif tool_name == "clinical_trials_search":
                    _condition = tool_args.get("condition")
                    _status = tool_args.get("status")
                    _max_results = tool_args.get("max_results", 10)
                    _payload = {"max_items": min(int(_max_results or 10), 100)}
                    if _condition is not None: _payload["query"] = _condition
                    if _status is not None: _payload["status"] = [_status] if not isinstance(_status, list) else _status
                    data = run_actor_sync(ACTORS["clinical_trials"], _payload)
                elif tool_name == "epa_facility_search":
                    _state = tool_args.get("state")
                    _facility_name = tool_args.get("facility_name")
                    _naics_code = tool_args.get("naics_code")
                    _program = tool_args.get("program")
                    _max_results = tool_args.get("max_results", 10)
                    _payload = {"max_items": min(int(_max_results or 10), 100)}
                    if _state is not None: _payload["state"] = _state
                    if _facility_name is not None: _payload["facility_name"] = _facility_name
                    if _naics_code is not None: _payload["naics_code"] = _naics_code
                    if _program is not None: _payload["program"] = _program
                    data = run_actor_sync(ACTORS["epa_facility"], _payload)
                elif tool_name == "fec_campaign_finance_search":
                    _data_type = tool_args.get("data_type", 'candidates')
                    _name = tool_args.get("name")
                    _state = tool_args.get("state")
                    _party = tool_args.get("party")
                    _office = tool_args.get("office")
                    _max_results = tool_args.get("max_results", 10)
                    _payload = {"data_type": _data_type, "max_items": min(int(_max_results or 10), 100)}
                    if _name is not None: _payload["name"] = _name
                    if _state is not None: _payload["state"] = _state
                    if _party is not None: _payload["party"] = _party
                    if _office is not None: _payload["office"] = _office
                    data = run_actor_sync(ACTORS["fec_campaign_finance"], _payload)
                elif tool_name == "florida_new_filings_search":
                    _search_query = tool_args.get("search_query")
                    _max_results = tool_args.get("max_results", 10)
                    _include_details = tool_args.get("include_details", False)
                    _payload = {"max_items": min(int(_max_results or 10), 100), "include_details": _include_details}
                    if _search_query is not None: _payload["start_urls"] = ["https://search.sunbiz.org/Inquiry/CorporationSearch/SearchResults?inquiryType=EntityName&searchTerm=" + urllib.parse.quote(str(_search_query))]
                    data = run_actor_sync(ACTORS["florida_new_filings"], _payload)
                elif tool_name == "florida_officer_search":
                    _search_query = tool_args.get("search_query")
                    _max_results = tool_args.get("max_results", 10)
                    _include_details = tool_args.get("include_details", False)
                    _payload = {"max_items": min(int(_max_results or 10), 100), "include_details": _include_details}
                    if _search_query is not None: _payload["start_urls"] = ["https://search.sunbiz.org/Inquiry/CorporationSearch/SearchResults?inquiryType=OfficerRegisteredAgentName&searchTerm=" + urllib.parse.quote(str(_search_query))]
                    data = run_actor_sync(ACTORS["florida_officer"], _payload)
                elif tool_name == "french_company_search":
                    _query = tool_args.get("query")
                    _department = tool_args.get("department")
                    _naf_code = tool_args.get("naf_code")
                    _active_only = tool_args.get("active_only", True)
                    _max_results = tool_args.get("max_results", 10)
                    _payload = {"active_only": _active_only, "max_items": min(int(_max_results or 10), 100)}
                    if _query is not None: _payload["query"] = _query
                    if _department is not None: _payload["department"] = _department
                    if _naf_code is not None: _payload["naf_code"] = _naf_code
                    data = run_actor_sync(ACTORS["french_company"], _payload)
                elif tool_name == "google_play_reviews_search":
                    _app_ids = tool_args.get("app_ids")
                    _max_results = tool_args.get("max_results", 25)
                    _scores = tool_args.get("scores")
                    _keywords = tool_args.get("keywords")
                    _recent_days = tool_args.get("recent_days")
                    _payload = {"max_items": min(int(_max_results or 10), 100)}
                    if _app_ids is not None: _payload["app_ids"] = _app_ids
                    if _scores is not None: _payload["scores"] = [str(x) for x in (_scores if isinstance(_scores, list) else [_scores])]
                    if _keywords is not None: _payload["keywords"] = _keywords
                    if _recent_days is not None: _payload["recent_days"] = int(_recent_days)
                    data = run_actor_sync(ACTORS["google_play_reviews"], _payload)
                elif tool_name == "linkedin_jobs_search":
                    _search_query = tool_args.get("search_query")
                    _location = tool_args.get("location", '')
                    _max_results = tool_args.get("max_results", 10)
                    _include_details = tool_args.get("include_details", False)
                    _payload = {"location": _location, "max_items": min(int(_max_results or 10), 100), "include_details": _include_details}
                    if _search_query is not None: _payload["search_query"] = _search_query
                    data = run_actor_sync(ACTORS["linkedin_jobs"], _payload)
                elif tool_name == "openfda_search":
                    _dataset = tool_args.get("dataset", 'drug_approval')
                    _search = tool_args.get("search")
                    _include_details = tool_args.get("include_details", False)
                    _max_results = tool_args.get("max_results", 10)
                    _payload = {"dataset": _dataset, "include_details": _include_details, "max_items": min(int(_max_results or 10), 100)}
                    if _search is not None: _payload["search"] = _search
                    data = run_actor_sync(ACTORS["openfda"], _payload)
                elif tool_name == "us_business_entity_search":
                    _search_query = tool_args.get("search_query")
                    _states = tool_args.get("states", ['florida', 'alabama', 'iowa', 'wisconsin'])
                    _max_results = tool_args.get("max_results", 10)
                    _include_details = tool_args.get("include_details", False)
                    _payload = {"sources": _states, "max_items": min(int(_max_results or 10), 100), "include_details": _include_details}
                    if _search_query is not None: _payload["search_terms"] = [_search_query] if not isinstance(_search_query, list) else _search_query
                    data = run_actor_sync(ACTORS["us_business_entity"], _payload)
                elif tool_name == "us_contractor_license_search":
                    _search_query = tool_args.get("search_query")
                    _states = tool_args.get("states", ['california', 'oregon'])
                    _max_results = tool_args.get("max_results", 10)
                    _include_details = tool_args.get("include_details", False)
                    _payload = {"sources": _states, "max_items": min(int(_max_results or 10), 100), "include_details": _include_details}
                    if _search_query is not None: _payload["search_terms"] = [_search_query] if not isinstance(_search_query, list) else _search_query
                    data = run_actor_sync(ACTORS["us_contractor_license"], _payload)
                elif tool_name == "youtube_video_search":
                    _search_query = tool_args.get("search_query")
                    _max_results = tool_args.get("max_results", 25)
                    _payload = {"max_items": min(int(_max_results or 10), 100)}
                    if _search_query is not None: _payload["search_query"] = _search_query
                    data = run_actor_sync(ACTORS["youtube_video"], _payload)
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
