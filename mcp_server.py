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
    "cms_healthcare_provider": "captainhandsome/cms-healthcare-provider-search",
    "europe_pmc_paper": "captainhandsome/europe-pmc-paper-search",
    "gleif_lei": "captainhandsome/gleif-lei-search",
    "tech_stack_detector": "captainhandsome/tech-stack-detector",
    "us_census_geocoder": "captainhandsome/us-census-geocoder",
    "grants_gov_opportunity": "captainhandsome/grants-gov-opportunity-search",
    "nhtsa_vehicle_recall": "captainhandsome/nhtsa-vehicle-recall-search",
    "ofac_sanctions": "captainhandsome/ofac-sanctions-search",
    "sec_form_4_insider_transactions": "captainhandsome/sec-form-4-insider-transactions",
    "ted_eu_tender": "captainhandsome/ted-eu-tender-search",
    "google_autocomplete_keywords": "captainhandsome/google-autocomplete-keyword-suggestions",
    "google_news": "captainhandsome/google-news-search",
    "cve_vulnerability_intelligence": "captainhandsome/nvd-cisa-vulnerability-intelligence",
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
    {'name': 'cms_healthcare_provider_search', 'title': 'CMS Healthcare Provider Search', 'description': "Search official CMS Provider Data Catalog directories for Medicare-certified hospitals, nursing homes, home health agencies, hospices, dialysis facilities, long-term care hospitals, and inpatient rehab facilities. Returns normalized facility records (identity, ownership, capacity, and star ratings) across all seven provider types through one consistent row shape.\n\nBehavioral Transparency:\n- Execution: Network call executed synchronously in the cloud via Apify Actor 'captainhandsome/cms-healthcare-provider-search'.\n- Side Effects: Strictly read-only; queries the public CMS Provider Data Catalog API, no API key or login required.\n- Authentication: Requires APIFY_TOKEN environment variable.\n- Latency & Limits: Typical run duration is 10-30 seconds; timeout capped at 120 seconds.\n\nUsage Guidelines:\n- When to use: Use for healthcare facility due diligence, star-rating and quality comparisons, nursing-home staffing/inspection/fines research, or building a location-bounded list of Medicare-certified providers.\n- When NOT to use: Do not use for clinical trial recruitment data, environmental compliance, campaign finance, corporate registry lookups, or contractor licensing.\n- Named alternatives: Use 'clinical_trials_search' for ClinicalTrials.gov study data, 'epa_facility_search' for environmental compliance, 'us_business_entity_search' or 'us_contractor_license_search' for corporate/contractor registries, or 'europe_pmc_paper_search' for biomedical literature.", 'inputSchema': {'type': 'object', 'properties': {'provider_types': {'type': 'array', 'items': {'type': 'string', 'enum': ['hospital', 'nursing_home', 'home_health', 'hospice', 'dialysis', 'long_term_care_hospital', 'inpatient_rehab']}, 'description': "One or more CMS provider-directory types to search, e.g. ['hospital'] or ['nursing_home', 'hospice']. Omit to search hospitals only, the Actor's own fallback."}, 'state': {'type': 'string', 'minLength': 2, 'maxLength': 2, 'description': "Two-letter US state or territory abbreviation to search within, e.g. 'TX'."}, 'city': {'type': 'string', 'description': "City name to filter by, matched exactly (case-insensitive, not a substring), e.g. 'Houston'."}, 'zip': {'type': 'string', 'description': "Five-digit US ZIP code to filter by, e.g. '77030'."}, 'county': {'type': 'string', 'description': "County name to filter by, matched exactly (case-insensitive), e.g. 'Harris'."}, 'name_contains': {'type': 'string', 'description': "Case-insensitive substring to match against the provider or facility name, e.g. 'Memorial'."}, 'max_results': {'type': 'integer', 'minimum': 1, 'maximum': 100, 'default': 10, 'description': 'Maximum number of provider records to retrieve and bill. Defaults to 10.'}}, 'required': ['state']}, 'outputSchema': {'type': 'object', 'properties': {'results': {'type': 'array', 'description': 'Collection of normalized Medicare-certified provider records matching the search.', 'items': {'type': 'object', 'properties': {'provider_type': {'type': ['string', 'null'], 'description': 'Which CMS directory this row came from (hospital, nursing_home, home_health, hospice, dialysis, long_term_care_hospital, or inpatient_rehab).'}, 'ccn': {'type': ['string', 'null'], 'description': 'CMS Certification Number, the stable identifier for the provider (hospitals use their facility ID here).'}, 'name': {'type': ['string', 'null'], 'description': 'Facility or provider name as published by CMS.'}, 'address': {'type': ['string', 'null'], 'description': 'Public street address reported by CMS.'}, 'city': {'type': ['string', 'null'], 'description': 'City reported for the record.'}, 'state': {'type': ['string', 'null'], 'description': 'Two-letter US state or territory abbreviation.'}, 'zip': {'type': ['string', 'null'], 'description': 'Postal or ZIP code reported for the record.'}, 'county': {'type': ['string', 'null'], 'description': 'County reported for the record.'}, 'phone': {'type': ['string', 'null'], 'description': 'Public provider telephone number in CMS display format.'}, 'ownership': {'type': ['string', 'null'], 'description': 'Ownership or profit status as classified by CMS for this directory.'}, 'subtype': {'type': ['string', 'null'], 'description': 'Directory-specific subtype, e.g. hospital type for hospitals or provider type for nursing homes.'}, 'star_rating': {'type': ['number', 'null'], 'description': 'CMS overall one-to-five star rating for the provider, when the directory publishes one.'}, 'certification_date': {'type': ['string', 'null'], 'description': 'Date CMS certified the provider, in YYYY-MM-DD form where available.'}, 'beds': {'type': ['number', 'null'], 'description': 'Number of certified beds. Nursing homes and long-term care hospitals only.'}, 'chain': {'type': ['string', 'null'], 'description': 'Chain or corporate ownership group name, when CMS reports one. Nursing homes and dialysis facilities only.'}, 'emergency_services': {'type': ['string', 'null'], 'description': "Whether the hospital reports emergency services ('Yes'/'No'). Hospitals only."}}, 'required': ['ccn', 'name']}}}, 'required': ['results']}, 'annotations': {'readOnlyHint': True, 'destructiveHint': False, 'idempotentHint': True, 'openWorldHint': True}},
    {'name': 'europe_pmc_paper_search', 'title': 'Europe PMC Research Paper Search', 'description': "Search Europe PMC and PubMed for research papers, preprints and patents by topic, author, journal, publication year and open-access status. Returns flat records with identifiers, abstracts, citation counts, MeSH indexing, funding and full-text links.\n\nBehavioral Transparency:\n- Execution: Network call executed synchronously in the cloud via Apify Actor 'captainhandsome/europe-pmc-paper-search'.\n- Side Effects: Strictly read-only; queries the official Europe PMC REST API, no API key or login required.\n- Authentication: Requires APIFY_TOKEN environment variable.\n- Latency & Limits: Typical run duration is 5-20 seconds for the default 10 results; timeout capped at 120 seconds. Requesting a large max_results or enabling include_entities adds paginated and annotation-batch requests and increases duration.\n\nUsage Guidelines:\n- When to use: Use for biomedical and life-science literature search, systematic-review scoping, citation and impact tracking, funding/grant provenance research, open-access discovery, or mining gene/disease/organism entities from paper text.\n- When NOT to use: Do not use for clinical trial recruitment or study status (use 'clinical_trials_search'), drug/device safety data, approvals, adverse events or recalls (use 'openfda_search'), or general corporate/regulatory lookups.\n- Named alternatives: Use 'clinical_trials_search' for ClinicalTrials.gov study records, or 'openfda_search' for FDA drug and device safety datasets.", 'inputSchema': {'type': 'object', 'properties': {'query': {'type': 'string', 'minLength': 2, 'description': "Keywords, topic, condition, intervention or Europe PMC search expression. Example: 'gut microbiome obesity'."}, 'author': {'type': 'string', 'description': "Filter to papers by this author's name. Example: 'Villapol S'."}, 'journal': {'type': 'string', 'description': "Filter to papers published in this journal. Example: 'Nature Medicine'."}, 'year_from': {'type': 'integer', 'description': 'Return only papers published in this year or later. Example: 2022.'}, 'year_to': {'type': 'integer', 'description': 'Return only papers published in this year or earlier. Example: 2026.'}, 'open_access_only': {'type': 'boolean', 'description': 'Return only records Europe PMC marks as open access. Example: true.'}, 'has_abstract_only': {'type': 'boolean', 'description': 'Return only papers for which Europe PMC provides an abstract. Example: true.'}, 'sort_by': {'type': 'string', 'enum': ['relevance', 'cited', 'date'], 'default': 'relevance', 'description': "Order results by relevance, citation count, or newest publication date. Defaults to 'relevance'. Example: 'cited'."}, 'include_entities': {'type': 'boolean', 'default': False, 'description': 'Add genes, diseases, organisms, chemicals, Gene Ontology terms, experimental methods and accession numbers mined from the full text. Adds roughly one extra request per 8 results. Defaults to false. Example: true.'}, 'max_results': {'type': 'integer', 'minimum': 1, 'maximum': 100, 'default': 10, 'description': 'Maximum number of papers to retrieve. Defaults to 10. Example: 25.'}}, 'required': ['query']}, 'outputSchema': {'type': 'object', 'properties': {'results': {'type': 'array', 'description': 'Collection of Europe PMC records matching the search.', 'items': {'type': 'object', 'properties': {'id': {'type': 'string', 'description': 'Structured id value returned by the official Europe PMC REST API.'}, 'source': {'type': 'string', 'description': "Source database the record came from, e.g. 'MED' for PubMed, 'PPR' for preprint, 'PAT' for patent."}, 'pmid': {'type': 'string', 'description': 'PubMed identifier for the publication.'}, 'pmcid': {'type': 'string', 'description': 'PubMed Central identifier for full-text content.'}, 'doi': {'type': 'string', 'description': 'Digital Object Identifier for the publication.'}, 'title': {'type': 'string', 'description': 'Published title of the paper, study or source record.'}, 'authors': {'type': 'string', 'description': 'Full author byline as one comma-separated string.'}, 'first_author': {'type': 'string', 'description': "First author in abbreviated form, e.g. 'Kara G'."}, 'journal': {'type': 'string', 'description': 'Journal title the paper was published in.'}, 'pub_year': {'type': 'string', 'description': 'Year of publication.'}, 'publication_date': {'type': 'string', 'description': 'First publication date of the record.'}, 'abstract': {'type': 'string', 'description': 'Publication abstract supplied by Europe PMC.'}, 'keywords': {'type': 'string', 'description': 'Author-supplied keywords, comma separated.'}, 'mesh_terms': {'type': 'string', 'description': 'Medical Subject Headings assigned to the paper, comma separated.'}, 'cited_by_count': {'type': 'integer', 'description': 'Number of citing works recorded by Europe PMC.'}, 'is_open_access': {'type': 'boolean', 'description': 'True when Europe PMC marks the record as open access.'}, 'full_text_availability': {'type': 'string', 'description': "Best access available across providers: 'Open access', 'Free', or 'Subscription required'."}, 'pdf_url': {'type': 'string', 'description': 'Direct link to the PDF, preferring an open-access or free copy.'}, 'url': {'type': 'string', 'description': 'Canonical public URL for the source record on europepmc.org.'}, 'funders': {'type': 'string', 'description': 'Agencies that funded the work, comma separated.'}}, 'required': ['id', 'title']}}}, 'required': ['results']}, 'annotations': {'readOnlyHint': True, 'destructiveHint': False, 'idempotentHint': True, 'openWorldHint': True}},
    {'name': 'gleif_lei_search', 'title': 'GLEIF Legal Entity Identifier Search', 'description': "Search the official GLEIF register for Legal Entity Identifiers by company name, exact LEI, or free text, and return normalized records carrying registration status, jurisdiction, legal and headquarters addresses, and the company's own national registration number.\n\nBehavioral Transparency:\n- Execution: Network call executed synchronously in the cloud via Apify Actor 'captainhandsome/gleif-lei-search'.\n- Side Effects: Strictly read-only; queries the free, public GLEIF API, no API key or login required.\n- Authentication: Requires APIFY_TOKEN environment variable.\n- Latency & Limits: Typical run duration is 5-30 seconds for a flat lookup; enabling include_relationships adds up to six extra requests per record and can push a large run past a minute; timeout capped at 120 seconds.\n\nUsage Guidelines:\n- When to use: Use for counterparty due diligence, KYC/AML onboarding checks, entity resolution across jurisdictions, or confirming a company's registration status, legal form, and own national registry number via its Legal Entity Identifier.\n- When NOT to use: Do not use for SEC financial filings (use 'sec_edgar_filings'), for a US state's own corporate registry record (use 'us_business_entity_search'), or for French Sirene registry detail (use 'french_company_search'); GLEIF coverage is limited to entities that hold an LEI.\n- Named alternatives: Use 'sec_edgar_filings' for US public company filings, 'us_business_entity_search' for US state-level business entity lookups, or 'french_company_search' for the French national company registry.", 'inputSchema': {'type': 'object', 'properties': {'query': {'type': 'string', 'minLength': 2, 'description': "Company name, an LEI code, or free text to search for, depending on search_mode. Example: 'Siemens'."}, 'search_mode': {'type': 'string', 'enum': ['name', 'fulltext', 'lei'], 'default': 'name', 'description': "How to interpret query. 'name' matches the registered legal name only, 'fulltext' matches the whole record including addresses and former names, 'lei' is an exact 20-character LEI lookup. Defaults to 'name'."}, 'country': {'type': 'string', 'minLength': 2, 'maxLength': 2, 'description': "Two-letter ISO country code of the entity's legal address to filter on, e.g. 'DE' for Germany. Omit to search every country."}, 'jurisdiction': {'type': 'string', 'minLength': 2, 'maxLength': 2, 'description': "Two-letter code of the registering jurisdiction to filter on, e.g. 'FR'. Can differ from country. Omit to search every jurisdiction."}, 'status': {'type': 'string', 'enum': ['ACTIVE', 'INACTIVE'], 'description': "Limit results to entities with this operating status, e.g. 'ACTIVE'. Omit to return both active and inactive entities."}, 'include_relationships': {'type': 'boolean', 'default': False, 'description': 'Also fetch direct and ultimate parent, subsidiary count and names, and ISINs. Costs up to six extra requests per record and slows the run. Defaults to false.'}, 'max_results': {'type': 'integer', 'minimum': 1, 'maximum': 100, 'default': 10, 'description': 'Maximum number of LEI records to retrieve. Defaults to 10.'}}, 'required': ['query']}, 'outputSchema': {'type': 'object', 'properties': {'results': {'type': 'array', 'description': 'Collection of GLEIF LEI records matching the search.', 'items': {'type': 'object', 'properties': {'lei': {'type': 'string', 'description': 'Twenty-character Legal Entity Identifier, the ISO 17442 global key for this entity.'}, 'legal_name': {'type': 'string', 'description': 'Registered legal name of the entity, in its own script.'}, 'status': {'type': 'string', 'description': 'Whether the entity itself is still operating: ACTIVE or INACTIVE.'}, 'registration_status': {'type': 'string', 'description': 'Lifecycle of the LEI registration itself: ISSUED, LAPSED, RETIRED, ANNULLED and so on.'}, 'jurisdiction': {'type': 'string', 'description': 'Two-letter code of the legal jurisdiction the entity is formed in.'}, 'legal_form_name': {'type': 'string', 'description': "Legal form resolved to words, e.g. 'Private Limited Company'. Null when GLEIF has no free-text label for the code."}, 'registered_as': {'type': 'string', 'description': "The company's number in its own national registry, the join key to Companies House, SIRENE, the Handelsregister and the rest."}, 'registered_at_name': {'type': 'string', 'description': "Name of the national registration authority the entity is filed with, e.g. 'Companies House'."}, 'legal_country': {'type': 'string', 'description': 'ISO 3166-1 alpha-2 country code of the registered legal address.'}, 'legal_city': {'type': 'string', 'description': 'City of the registered legal address.'}, 'corroboration_level': {'type': 'string', 'description': 'How hard the data was verified: FULLY_CORROBORATED, PARTIALLY_CORROBORATED or ENTITY_SUPPLIED_ONLY.'}, 'next_renewal_date': {'type': 'string', 'description': 'When the LEI must next be revalidated, ISO 8601. A date in the past means the record is lapsing.'}, 'gleif_profile_url': {'type': 'string', 'description': 'Public GLEIF record page for this LEI, for verifying a row by hand.'}}, 'required': ['lei', 'legal_name']}}}, 'required': ['results']}, 'annotations': {'readOnlyHint': True, 'destructiveHint': False, 'idempotentHint': True, 'openWorldHint': True}},
    {'name': 'tech_stack_detector', 'title': 'Website Tech Stack & Ecommerce Scanner', 'description': "Scan a batch of public websites and detect the CMS, ecommerce platform, payment gateway, CDN, analytics, hosting, and 15 other technology categories from 75 signatures, alongside the infrastructure headers, page metadata, and contact/social links the same page response already carries.\n\nBehavioral Transparency:\n- Execution: Network call executed synchronously in the cloud via Apify Actor 'captainhandsome/tech-stack-detector'.\n- Side Effects: Strictly read-only; fetches each site's homepage (and, with include_details, its robots.txt and one contact/about page) as a normal browser would, no login or API key required on the target site.\n- Authentication: Requires APIFY_TOKEN environment variable.\n- Latency & Limits: Typical run duration is 5-20 seconds for a small batch; timeout capped at 120 seconds. Detection is signature-based HTML/header matching, not a headless browser, so it is evidence of presence, never proof of absence, and JavaScript-rendered technology is not executed or seen.\n\nUsage Guidelines:\n- When to use: Use for competitive technology research, B2B lead qualification and segmentation, ecommerce/payment-stack prospecting, or pulling the public contact and social links a company's own website exposes.\n- When NOT to use: Do not use for a company's legal registration or corporate-registry status (use 'us_business_entity_search' or 'gleif_lei_search'), hiring signals (use 'linkedin_jobs_search' or 'glassdoor_jobs_search'), app-store sentiment (use 'google_play_reviews_search'), or a business's physical location and reviews (use 'google_maps_search').\n- Named alternatives: Use 'us_business_entity_search' for state corporate registry records, 'gleif_lei_search' for global legal entity identifiers, 'linkedin_jobs_search' or 'glassdoor_jobs_search' for a company's open roles and employee sentiment, or 'google_maps_search' for a business's physical location and reviews.", 'inputSchema': {'type': 'object', 'properties': {'urls': {'type': 'array', 'items': {'type': 'string'}, 'minItems': 1, 'description': 'Domains or URLs to analyze; one record is returned per site. A bare domain is normalized to https automatically. Example: ["ghost.org", "webflow.com"].'}, 'include_details': {'type': 'boolean', 'default': False, 'description': 'Also fetch /robots.txt and a discovered contact or about page per site, adding the sitemap URL, crawl-rule count, and any extra emails/phones the homepage omits. Costs up to two extra requests per site. Defaults to false.'}, 'max_results': {'type': 'integer', 'minimum': 1, 'maximum': 100, 'default': 10, 'description': 'Maximum number of site records to return. Defaults to 10.'}}, 'required': ['urls']}, 'outputSchema': {'type': 'object', 'properties': {'results': {'type': 'array', 'description': 'One record per analyzed website.', 'items': {'type': 'object', 'properties': {'url': {'type': 'string', 'description': 'Requested website URL, as normalized before the request.'}, 'final_url': {'type': 'string', 'description': 'Final URL after HTTP redirects.'}, 'status': {'type': 'integer', 'description': 'HTTP response status code.'}, 'domain': {'type': 'string', 'description': 'Registered host of the final URL with any leading www. removed.'}, 'is_https': {'type': 'boolean', 'description': 'True when the final URL was served over HTTPS.'}, 'technologies': {'type': 'array', 'items': {'type': 'string'}, 'description': 'Detected technology names, e.g. Fastly, Next.js.'}, 'count': {'type': 'integer', 'description': 'Number of detected technologies.'}, 'categories': {'type': 'array', 'items': {'type': 'string'}, 'description': 'Distinct categories of detected technologies, e.g. cdn, framework.'}, 'cms': {'type': 'string', 'description': 'Detected content management systems, comma separated.'}, 'ecommerce_platform': {'type': 'string', 'description': 'Detected ecommerce platforms, comma separated.'}, 'framework': {'type': 'string', 'description': 'Detected web application frameworks, comma separated.'}, 'analytics': {'type': 'string', 'description': 'Detected analytics and tag-management tools, comma separated.'}, 'payments': {'type': 'string', 'description': 'Detected payment providers, comma separated.'}, 'cdn': {'type': 'string', 'description': 'Detected content delivery networks, comma separated.'}, 'hosting': {'type': 'string', 'description': 'Detected hosting and deployment platforms, comma separated.'}, 'security_tech': {'type': 'string', 'description': 'Detected bot-protection and CAPTCHA services, comma separated.'}, 'title': {'type': 'string', 'description': 'Contents of the HTML title tag.'}, 'meta_description': {'type': 'string', 'description': 'Meta description of the page.'}, 'emails': {'type': 'string', 'description': 'Email addresses published on the page (mailto: links plus same-domain plain-text addresses), comma separated.'}, 'phones': {'type': 'string', 'description': 'Phone numbers taken from tel: links, comma separated.'}, 'linkedin_url': {'type': 'string', 'description': 'First LinkedIn company, school, or member URL linked from the page.'}, 'twitter_url': {'type': 'string', 'description': 'First Twitter/X profile URL linked from the page.'}, 'github_url': {'type': 'string', 'description': 'First GitHub organization or repository URL linked from the page.'}, 'contact_page_url': {'type': 'string', 'description': 'Contact or about page found on the same host. Null unless include_details is on.'}, 'robots_txt_found': {'type': 'boolean', 'description': 'True when /robots.txt returned a real robots file. Null unless include_details is on.'}, 'sitemap_url': {'type': 'string', 'description': 'First sitemap URL declared in /robots.txt. Null unless include_details is on.'}, 'error': {'type': 'string', 'description': 'Fetch or processing error for this site, or null on success.'}}, 'required': ['url']}}}, 'required': ['results']}, 'annotations': {'readOnlyHint': True, 'destructiveHint': False, 'idempotentHint': True, 'openWorldHint': True}},
    {'name': 'us_census_geocoder', 'title': 'US Census Address Geocoder', 'description': "Geocode US street addresses into full Census Bureau geography, not just a pin: state and county FIPS, census tract and block GEOIDs, congressional district, incorporated place, school district and metro area (CBSA). Built on the official, public-domain Census Bureau geocoder.\n\nBehavioral Transparency:\n- Execution: Network call executed synchronously in the cloud via Apify Actor 'captainhandsome/us-census-geocoder'.\n- Side Effects: Strictly read-only; queries the public Census Bureau geocoder API, no API key or login required.\n- Authentication: Requires APIFY_TOKEN environment variable.\n- Latency & Limits: Requests run five addresses at a time against the Census Bureau's geocoder with a 60-second timeout each; typical run duration is 10-60 seconds depending on list size, timeout capped at 120 seconds. Returns exactly one row per address, matched or not - output volume is set by the length of 'addresses', not by 'max_results'.\n\nUsage Guidelines:\n- When to use: Use to append census tract, block, county FIPS, congressional district or school district GEOIDs to US street addresses for demographic joins, site selection, fair-lending/CRA reporting, or district-based targeting.\n- When NOT to use: Do not use for interactive place search, driving directions or points of interest; do not use for business entity or contractor license lookups (use 'us_business_entity_search' or 'us_contractor_license_search'). Addresses outside the United States are not supported.\n- Named alternatives: Use 'us_business_entity_search' or 'us_contractor_license_search' for entity and licensing lookups instead of an address. No other tool in this toolset performs US address geocoding.", 'inputSchema': {'type': 'object', 'properties': {'addresses': {'type': 'array', 'items': {'type': 'string'}, 'minItems': 1, 'description': "One or more one-line US addresses to geocode, e.g. ['1600 Amphitheatre Pkwy, Mountain View, CA 94043']. The Census parser is tolerant of punctuation but wants at least a street, a city and a state. Each address returns exactly one result row, matched or not."}, 'benchmark': {'type': 'string', 'enum': ['Public_AR_Current', 'Public_AR_Census2020'], 'default': 'Public_AR_Current', 'description': "Which Census address file to match against. Defaults to 'Public_AR_Current', the live, continuously updated file. Use 'Public_AR_Census2020' to reconcile against the address file as it stood at the 2020 Census."}, 'vintage': {'type': 'string', 'enum': ['Current_Current', 'Census2020_Current'], 'default': 'Current_Current', 'description': "Which geography vintage to report tract, block and district boundaries from. Defaults to 'Current_Current'. Use 'Census2020_Current' when you need boundaries as drawn at the 2020 Census, e.g. before a later congressional redistricting."}, 'max_results': {'type': 'integer', 'minimum': 1, 'maximum': 100, 'default': 10, 'description': "Ceiling on the number of address rows you are willing to pay for. Defaults to 10. This Actor emits exactly one row per address (matched or not) and does not truncate your address list to this number, so keep 'addresses' at or below max_results to control both output volume and cost."}}, 'required': ['addresses']}, 'outputSchema': {'type': 'object', 'properties': {'results': {'type': 'array', 'description': 'One geocoded row per input address, in input order, including addresses that failed to match.', 'items': {'type': 'object', 'properties': {'input_address': {'type': 'string', 'description': 'The address string exactly as supplied, so results can be joined back to the source list.'}, 'matched': {'type': 'boolean', 'description': 'True when the Census geocoder returned at least one candidate for the address. False rows carry every other field as null rather than being dropped.'}, 'match_count': {'type': 'integer', 'description': 'How many candidate addresses Census returned. 1 is a clean hit; more than 1 means the address was ambiguous and the row describes only the first candidate. 0 on unmatched rows.'}, 'matched_address': {'type': 'string', 'description': 'The address as Census standardised it: upper case, standardised street type, and the ZIP it actually resolved to. Null when matched is false.'}, 'latitude': {'type': 'number', 'description': 'Latitude in decimal degrees, interpolated along the matched TIGER street segment (street frontage, not rooftop). Null when matched is false.'}, 'longitude': {'type': 'number', 'description': 'Longitude in decimal degrees, same street-segment interpolation as latitude. Null when matched is false.'}, 'city': {'type': 'string', 'description': 'Postal city of the matched address, upper case. Can differ from place_name, the legally incorporated place. Null when matched is false.'}, 'state': {'type': 'string', 'description': 'Two-letter USPS state or territory code of the matched address. Null when matched is false.'}, 'zip': {'type': 'string', 'description': 'Five-digit ZIP code Census resolved the address to, kept as a string so leading zeros survive export. Null when matched is false.'}, 'state_fips': {'type': 'string', 'description': 'Two-digit state FIPS code, the first component of every Census GEOID. Null when matched is false.'}, 'county_fips': {'type': 'string', 'description': 'Five-digit county GEOID (state FIPS plus county code), the county key used by ACS, BLS and most federal datasets. Null when matched is false.'}, 'county_name': {'type': 'string', 'description': 'County or county-equivalent name (parish, borough, independent city). Null when matched is false.'}, 'place_name': {'type': 'string', 'description': 'Name of the incorporated place (city, town, village) containing the address. Null in unincorporated territory and when matched is false.'}, 'place_geoid': {'type': 'string', 'description': 'Seven-digit place GEOID, the join key to Census place-level tables since place names repeat across states. Null when matched is false.'}, 'tract_geoid': {'type': 'string', 'description': 'Eleven-digit census tract GEOID, the join key for American Community Survey tract tables. Null when matched is false.'}, 'block_group_geoid': {'type': 'string', 'description': 'Twelve-digit block group GEOID, the finest geography the American Community Survey publishes estimates for. Null when matched is false.'}, 'block_geoid': {'type': 'string', 'description': 'Fifteen-digit census block GEOID, the finest geography the Bureau publishes and the join key to decennial block data. Null when matched is false.'}, 'zcta': {'type': 'string', 'description': 'Five-digit ZIP Code Tabulation Area containing the point, the only ZIP-shaped geography the Bureau actually publishes data for. Can differ from zip. Null when matched is false.'}, 'urban_rural': {'type': 'string', 'description': 'Census urban/rural classification of the containing block: U for urban, R for rural. Null when matched is false.'}, 'congressional_district_geoid': {'type': 'string', 'description': 'Four-digit congressional district GEOID (state FIPS plus district), unique nationally and the join key to district-level Census tables. Null when matched is false.'}, 'cbsa_name': {'type': 'string', 'description': 'Combined Statistical Area name, broader than the single metro area inside it (e.g. Washington joined with Baltimore). Null outside any CSA and when matched is false.'}, 'metro_area_name': {'type': 'string', 'description': 'Name of the Core Based Statistical Area (the actual metro or micro area) containing the address. Null outside any CBSA and when matched is false.'}, 'school_district_name': {'type': 'string', 'description': 'Name of the school district containing the address; a unified district where one exists, otherwise the elementary or secondary district per school_district_type. Null when matched is false.'}, 'benchmark_name': {'type': 'string', 'description': 'The Census address benchmark that actually answered, echoed back by the API on every row.'}, 'vintage_name': {'type': 'string', 'description': 'The geography vintage that actually answered, echoed back by the API on every row.'}}, 'required': ['input_address', 'matched', 'match_count']}}}, 'required': ['results']}, 'annotations': {'readOnlyHint': True, 'destructiveHint': False, 'idempotentHint': True, 'openWorldHint': True}},
    {'name': 'grants_gov_opportunity_search', 'title': 'Grants.gov Funding Opportunity Search', 'description': "Search official US federal funding opportunities from Grants.gov by keyword, agency, status, opportunity number or Assistance Listing. Returns deadlines, award ranges, eligibility, contacts and canonical source links.\n\nBehavioral Transparency:\n- Execution: Network call executed synchronously in the cloud via Apify Actor 'captainhandsome/grants-gov-opportunity-search'.\n- Side Effects: Strictly read-only; queries the official Grants.gov API.\n- Authentication: Requires APIFY_TOKEN environment variable.\n- Latency & Limits: Typical run duration is 10-60 seconds; include_details adds one detail request per result.\n\nUsage Guidelines:\n- When to use: Use for grant prospecting, research-funding discovery and federal opportunity monitoring.\n- When NOT to use: Do not use for awarded federal contracts (use 'usaspending_contracts') or European procurement (use 'ted_eu_tender_search').\n- Named alternatives: Use 'usaspending_contracts' for historical US awards or 'ted_eu_tender_search' for European tender notices.", 'inputSchema': {'type': 'object', 'properties': {'keyword': {'type': 'string', 'minLength': 2, 'description': 'Keywords to search in opportunity titles and descriptions.'}, 'opportunity_number': {'type': 'string', 'description': 'Exact or partial funding opportunity number.'}, 'agency_codes': {'type': 'array', 'items': {'type': 'string'}, 'description': 'Federal agency codes such as NSF or HHS.'}, 'statuses': {'type': 'array', 'items': {'type': 'string', 'enum': ['forecasted', 'posted', 'closed', 'archived']}, 'description': 'Opportunity statuses to include.'}, 'assistance_listing': {'type': 'string', 'description': 'Assistance Listing number, formerly CFDA, such as 47.070.'}, 'include_details': {'type': 'boolean', 'default': True, 'description': 'Fetch award, eligibility, synopsis and contact details.'}, 'max_results': {'type': 'integer', 'minimum': 1, 'maximum': 100, 'default': 10, 'description': 'Maximum opportunities to return.'}}}, 'outputSchema': {'type': 'object', 'properties': {'results': {'type': 'array', 'items': {'type': 'object', 'properties': {'opportunity_number': {'type': 'string', 'description': 'Official funding opportunity number.'}, 'title': {'type': 'string', 'description': 'Official opportunity title.'}, 'status': {'type': 'string', 'description': 'Current Grants.gov status.'}, 'agency_name': {'type': 'string', 'description': 'Owning federal agency.'}, 'open_date': {'type': 'string', 'description': 'Opportunity opening date.'}, 'close_date': {'type': 'string', 'description': 'Application deadline.'}, 'estimated_funding': {'type': 'number', 'description': 'Estimated total program funding.'}, 'award_ceiling': {'type': 'number', 'description': 'Maximum award amount.'}, 'award_floor': {'type': 'number', 'description': 'Minimum award amount.'}, 'eligibility': {'type': 'string', 'description': 'Applicant eligibility description.'}, 'contact_email': {'type': 'string', 'description': 'Agency contact email.'}, 'grants_gov_url': {'type': 'string', 'description': 'Canonical Grants.gov opportunity page.'}}}}}, 'required': ['results']}, 'annotations': {'readOnlyHint': True, 'destructiveHint': False, 'idempotentHint': True, 'openWorldHint': True}},
    {'name': 'nhtsa_vehicle_recall_search', 'title': 'NHTSA Vehicle Recall Search', 'description': "Search official US vehicle-safety recalls by year, make and model or by NHTSA campaign number. Returns defect summaries, safety consequences, remedies, affected-unit counts and urgent park warnings.\n\nBehavioral Transparency:\n- Execution: Network call executed synchronously in the cloud via Apify Actor 'captainhandsome/nhtsa-vehicle-recall-search'.\n- Side Effects: Strictly read-only; queries the public NHTSA recalls API.\n- Authentication: Requires APIFY_TOKEN environment variable.\n- Latency & Limits: Typical run duration is 5-20 seconds; output is capped by max_results.\n\nUsage Guidelines:\n- When to use: Use for recall research, vehicle-safety checks, campaign monitoring and fleet-risk analysis.\n- When NOT to use: Do not use for drug, device or food recalls (use 'openfda_search'), or for general company filings.\n- Named alternatives: Use 'openfda_search' for FDA-regulated product recalls or 'sec_edgar_filings' for public-company filings.", 'inputSchema': {'type': 'object', 'properties': {'make': {'type': 'string', 'description': 'Vehicle make, for example Honda. Supply make, model and model_year together unless using campaign_number.'}, 'model': {'type': 'string', 'description': 'Vehicle model, for example Civic.'}, 'model_year': {'type': 'integer', 'minimum': 1949, 'maximum': 2100, 'description': 'Four-digit vehicle model year.'}, 'campaign_number': {'type': 'string', 'description': 'Exact NHTSA campaign number. Overrides vehicle fields when supplied.'}, 'max_results': {'type': 'integer', 'minimum': 1, 'maximum': 100, 'default': 10, 'description': 'Maximum recall rows to return.'}}}, 'outputSchema': {'type': 'object', 'properties': {'results': {'type': 'array', 'items': {'type': 'object', 'properties': {'campaign_number': {'type': 'string', 'description': 'Official NHTSA recall campaign number.'}, 'manufacturer': {'type': 'string', 'description': 'Manufacturer named in the recall.'}, 'make': {'type': 'string', 'description': 'Vehicle make.'}, 'model': {'type': 'string', 'description': 'Vehicle model.'}, 'model_year': {'type': 'integer', 'description': 'Vehicle model year.'}, 'component': {'type': 'string', 'description': 'Affected vehicle system or component.'}, 'summary': {'type': 'string', 'description': 'Official defect summary.'}, 'consequence': {'type': 'string', 'description': 'Official safety consequence.'}, 'remedy': {'type': 'string', 'description': 'Manufacturer remedy and owner instructions.'}, 'potential_units_affected': {'type': 'integer', 'description': 'Potential number of affected units.'}, 'park_it': {'type': 'boolean', 'description': 'Whether NHTSA issues a park-it warning.'}, 'park_outside': {'type': 'boolean', 'description': 'Whether NHTSA issues a park-outside warning.'}}}}}, 'required': ['results']}, 'annotations': {'readOnlyHint': True, 'destructiveHint': False, 'idempotentHint': True, 'openWorldHint': True}},
    {'name': 'ofac_sanctions_search', 'title': 'OFAC Sanctions Search', 'description': "Search official US Treasury OFAC SDN and consolidated non-SDN data by primary name, alias, program, country and entity type. Returns sanctions programs, aliases, addresses and source identifiers.\n\nBehavioral Transparency:\n- Execution: Network call executed synchronously in the cloud via Apify Actor 'captainhandsome/ofac-sanctions-search'.\n- Side Effects: Strictly read-only; downloads and filters official OFAC Sanctions List Service data.\n- Authentication: Requires APIFY_TOKEN environment variable.\n- Latency & Limits: Typical run duration is 10-40 seconds; results are exact source matches, not fuzzy compliance screening scores.\n\nUsage Guidelines:\n- When to use: Use for research, list reconciliation, sanctions-data enrichment and exact/substring name discovery.\n- When NOT to use: Do not treat a name match as a legal compliance determination; do not use for corporate filings (use 'sec_edgar_filings') or entity-registration verification (use 'us_business_entity_search').\n- Named alternatives: Use 'sec_edgar_filings' for US public-company filings, 'gleif_lei_search' for legal-entity identifiers, or 'us_business_entity_search' for state registrations.", 'inputSchema': {'type': 'object', 'properties': {'name': {'type': 'string', 'minLength': 2, 'description': 'Case-insensitive primary name or alias to search.'}, 'match_mode': {'type': 'string', 'enum': ['contains', 'exact'], 'default': 'contains', 'description': 'Substring discovery or exact normalized matching.'}, 'program': {'type': 'string', 'description': 'Optional OFAC sanctions program code.'}, 'country': {'type': 'string', 'description': 'Optional country filter across addresses and vessel flag.'}, 'entity_type': {'type': 'string', 'description': 'Optional party type such as individual, entity, vessel or aircraft.'}, 'list_scope': {'type': 'string', 'enum': ['all', 'sdn', 'non_sdn'], 'default': 'all', 'description': 'Search SDN, consolidated non-SDN, or both.'}, 'include_aliases': {'type': 'boolean', 'default': True, 'description': 'Match the query against alternate names as well as primary names.'}, 'max_results': {'type': 'integer', 'minimum': 1, 'maximum': 100, 'default': 10, 'description': 'Maximum sanctions records to return.'}}, 'required': ['name']}, 'outputSchema': {'type': 'object', 'properties': {'results': {'type': 'array', 'items': {'type': 'object', 'properties': {'list_type': {'type': 'string', 'description': 'Source OFAC list.'}, 'uid': {'type': 'string', 'description': 'OFAC unique record identifier.'}, 'primary_name': {'type': 'string', 'description': 'Primary sanctioned-party name.'}, 'entity_type': {'type': 'string', 'description': 'OFAC party type.'}, 'programs': {'type': 'string', 'description': 'Sanctions program codes.'}, 'aliases': {'type': 'string', 'description': 'Alternate names.'}, 'addresses': {'type': 'string', 'description': 'Street addresses.'}, 'countries': {'type': 'string', 'description': 'Address countries.'}, 'matched_name': {'type': 'string', 'description': 'Primary or alias name that matched.'}, 'match_basis': {'type': 'string', 'description': 'Whether the match was on a primary name or alias.'}, 'source_url': {'type': 'string', 'description': 'Official OFAC source page.'}, 'downloaded_at': {'type': 'string', 'description': 'UTC source retrieval time.'}}}}}, 'required': ['results']}, 'annotations': {'readOnlyHint': True, 'destructiveHint': False, 'idempotentHint': True, 'openWorldHint': True}},
    {'name': 'sec_form_4_insider_transactions', 'title': 'SEC Form 4 Insider Transactions', 'description': "Export structured insider buys, sales, grants, exercises and derivative transactions from official SEC Form 4 and 4/A XML by ticker or CIK. Returns reporting-owner roles, security details, share counts, prices and post-transaction ownership.\n\nBehavioral Transparency:\n- Execution: Network call executed synchronously in the cloud via Apify Actor 'captainhandsome/sec-form-4-insider-transactions'.\n- Side Effects: Strictly read-only; requests public SEC EDGAR submissions and ownership XML under an SEC-compliant contact identity.\n- Authentication: Requires APIFY_TOKEN environment variable; the Actor publisher supplies the SEC contact identity.\n- Latency & Limits: Typical run duration is 10-90 seconds depending on max_filings; output is capped by max_results.\n\nUsage Guidelines:\n- When to use: Use for insider-trading research, ownership-change monitoring and transaction-level Form 4 analysis.\n- When NOT to use: Do not use for 10-K, 10-Q or 8-K filings (use 'sec_edgar_filings') or campaign-finance data (use 'fec_campaign_finance_search').\n- Named alternatives: Use 'sec_edgar_filings' for company filings and exhibits, or 'fec_campaign_finance_search' for US political contributions and committees.", 'inputSchema': {'type': 'object', 'properties': {'company': {'type': 'string', 'minLength': 1, 'description': 'Public-company ticker or 1-10 digit SEC CIK.'}, 'date_from': {'type': 'string', 'pattern': '^\\d{4}-\\d{2}-\\d{2}$', 'description': 'Inclusive filing start date, YYYY-MM-DD.'}, 'date_to': {'type': 'string', 'pattern': '^\\d{4}-\\d{2}-\\d{2}$', 'description': 'Inclusive filing end date, YYYY-MM-DD.'}, 'transaction_codes': {'type': 'array', 'items': {'type': 'string'}, 'description': 'Exact SEC transaction codes such as P, S, A, M or G.'}, 'include_derivative': {'type': 'boolean', 'default': True, 'description': 'Include derivative securities such as options.'}, 'include_amendments': {'type': 'boolean', 'default': True, 'description': 'Include amended Form 4/A filings.'}, 'max_filings': {'type': 'integer', 'minimum': 1, 'maximum': 1000, 'default': 100, 'description': 'Maximum ownership XML filings to inspect.'}, 'max_results': {'type': 'integer', 'minimum': 1, 'maximum': 100, 'default': 10, 'description': 'Maximum transaction rows to return.'}}, 'required': ['company']}, 'outputSchema': {'type': 'object', 'properties': {'results': {'type': 'array', 'items': {'type': 'object', 'properties': {'issuer_name': {'type': 'string', 'description': 'Issuer name.'}, 'ticker': {'type': 'string', 'description': 'Issuer trading symbol.'}, 'reporting_owner_names': {'type': 'string', 'description': 'Reporting-owner names.'}, 'officer_titles': {'type': 'string', 'description': 'Reporting-owner officer titles.'}, 'transaction_id': {'type': 'string', 'description': 'Stable transaction-row identifier.'}, 'transaction_type': {'type': 'string', 'description': 'Non-derivative or derivative table.'}, 'transaction_date': {'type': 'string', 'description': 'Transaction date.'}, 'transaction_code': {'type': 'string', 'description': 'SEC ownership transaction code.'}, 'acquired_disposed_code': {'type': 'string', 'description': 'A for acquired or D for disposed.'}, 'shares': {'type': 'number', 'description': 'Securities acquired or disposed.'}, 'price_per_share': {'type': 'number', 'description': 'Transaction price per share.'}, 'shares_owned_after': {'type': 'number', 'description': 'Securities beneficially owned after the transaction.'}, 'filing_date': {'type': 'string', 'description': 'SEC filing date.'}, 'filing_url': {'type': 'string', 'description': 'Official SEC filing index URL.'}}}}}, 'required': ['results']}, 'annotations': {'readOnlyHint': True, 'destructiveHint': False, 'idempotentHint': True, 'openWorldHint': True}},
    {'name': 'ted_eu_tender_search', 'title': 'TED European Tender Search', 'description': "Search official Tenders Electronic Daily notices by keywords, contracting authority, country, CPV code and publication date. Returns buyers, deadlines, estimated values, classifications and direct TED documents.\n\nBehavioral Transparency:\n- Execution: Network call executed synchronously in the cloud via Apify Actor 'captainhandsome/ted-eu-tender-search'.\n- Side Effects: Strictly read-only; queries the official EU TED Search API.\n- Authentication: Requires APIFY_TOKEN environment variable.\n- Latency & Limits: Typical run duration is 10-45 seconds; output is capped by max_results.\n\nUsage Guidelines:\n- When to use: Use for European public-procurement discovery, bid monitoring, buyer research and CPV market analysis.\n- When NOT to use: Do not use for US grants (use 'grants_gov_opportunity_search') or completed US federal awards (use 'usaspending_contracts').\n- Named alternatives: Use 'grants_gov_opportunity_search' for US funding opportunities or 'usaspending_contracts' for awarded US contracts.", 'inputSchema': {'type': 'object', 'properties': {'keywords': {'type': 'string', 'minLength': 2, 'description': 'Words or phrase to match in TED notice titles.'}, 'buyer_name': {'type': 'string', 'description': 'Text to match in contracting authority names.'}, 'buyer_country': {'type': 'string', 'pattern': '^[A-Za-z]{3}$', 'description': 'ISO alpha-3 buyer country code, for example DEU or FRA.'}, 'cpv_code': {'type': 'string', 'pattern': '^\\d{8}$', 'description': 'Eight-digit Common Procurement Vocabulary code.'}, 'publication_date_from': {'type': 'string', 'pattern': '^\\d{4}-\\d{2}-\\d{2}$', 'description': 'Earliest publication date, YYYY-MM-DD.'}, 'publication_date_to': {'type': 'string', 'pattern': '^\\d{4}-\\d{2}-\\d{2}$', 'description': 'Latest publication date, YYYY-MM-DD.'}, 'language': {'type': 'string', 'default': 'eng', 'minLength': 3, 'maxLength': 3, 'description': 'Three-letter TED language code.'}, 'sort_direction': {'type': 'string', 'enum': ['desc', 'asc'], 'default': 'desc', 'description': 'Newest or oldest publication date first.'}, 'max_results': {'type': 'integer', 'minimum': 1, 'maximum': 100, 'default': 10, 'description': 'Maximum tender notices to return.'}}}, 'outputSchema': {'type': 'object', 'properties': {'results': {'type': 'array', 'items': {'type': 'object', 'properties': {'publication_number': {'type': 'string', 'description': 'Official TED notice publication number.'}, 'title': {'type': 'string', 'description': 'Notice title.'}, 'description': {'type': 'string', 'description': 'Lot descriptions.'}, 'buyer_names': {'type': 'string', 'description': 'Contracting authority names.'}, 'buyer_countries': {'type': 'string', 'description': 'Buyer country codes.'}, 'publication_date': {'type': 'string', 'description': 'TED publication date.'}, 'deadlines': {'type': 'string', 'description': 'Tender receipt deadlines.'}, 'cpv_codes': {'type': 'string', 'description': 'Main CPV codes.'}, 'estimated_value': {'type': 'number', 'description': 'Estimated procedure value.'}, 'currency': {'type': 'string', 'description': 'Estimated-value currency.'}, 'notice_url': {'type': 'string', 'description': 'Canonical TED notice page.'}, 'pdf_url': {'type': 'string', 'description': 'Direct preferred-language PDF.'}}}}}, 'required': ['results']}, 'annotations': {'readOnlyHint': True, 'destructiveHint': False, 'idempotentHint': True, 'openWorldHint': True}},
    {'name': 'google_autocomplete_keywords', 'title': 'Google Autocomplete Keyword Suggestions', 'description': "Generate localized Google Autocomplete keyword suggestions from one or many seed phrases. Supports alphabet and question-prefix expansion and returns ranked, globally deduplicated keyword ideas.\n\nBehavioral Transparency:\n- Execution: Network call executed synchronously in the cloud via Apify Actor 'captainhandsome/google-autocomplete-keyword-suggestions'.\n- Side Effects: Strictly read-only; queries the public Google suggestion endpoint.\n- Authentication: Requires APIFY_TOKEN environment variable.\n- Latency & Limits: Base queries normally finish in 5-20 seconds; expansion modes make additional requests; output is capped by max_results.\n\nUsage Guidelines:\n- When to use: Use for long-tail SEO research, customer-question discovery, content planning, and localized keyword ideation.\n- When NOT to use: Do not treat suggestions as verified search-volume, CPC, or competition data.\n- Named alternatives: Use 'google_search' for live search results or 'google_news_search' for current news coverage.", 'inputSchema': {'type': 'object', 'properties': {'queries': {'type': 'array', 'items': {'type': 'string'}, 'minItems': 1, 'maxItems': 100, 'description': 'Seed phrases to expand.'}, 'language': {'type': 'string', 'default': 'en', 'description': 'Two-letter suggestion language code.'}, 'country': {'type': 'string', 'default': 'US', 'description': 'Two-letter country code used to localize suggestions.'}, 'expansion_mode': {'type': 'string', 'enum': ['none', 'alphabet', 'questions', 'all'], 'default': 'none', 'description': 'Optional query expansion strategy.'}, 'max_results': {'type': 'integer', 'minimum': 1, 'maximum': 100, 'default': 25, 'description': 'Maximum unique suggestions to return.'}}, 'required': ['queries']}, 'outputSchema': {'type': 'object', 'properties': {'results': {'type': 'array', 'items': {'type': 'object', 'properties': {'seed': {'type': 'string', 'description': 'Original seed phrase.'}, 'request_query': {'type': 'string', 'description': 'Exact expanded request phrase.'}, 'suggestion': {'type': 'string', 'description': 'Autocomplete keyword suggestion.'}, 'rank': {'type': 'integer', 'description': 'Position in the source response.'}, 'expansion': {'type': 'string', 'description': 'Expansion prefix, suffix, or base.'}, 'language': {'type': 'string', 'description': 'Language code used.'}, 'country': {'type': 'string', 'description': 'Country code used.'}}}}}, 'required': ['results']}, 'annotations': {'readOnlyHint': True, 'destructiveHint': False, 'idempotentHint': True, 'openWorldHint': True}},
    {'name': 'google_news_search', 'title': 'Google News Search', 'description': "Search Google News for companies, people, products, brands, industries, and topics. Returns current headlines, publishers, timestamps, article links, source sites, and snippets.\n\nBehavioral Transparency:\n- Execution: Network call executed synchronously in the cloud via Apify Actor 'captainhandsome/google-news-search'.\n- Side Effects: Strictly read-only; queries public Google News RSS results.\n- Authentication: Requires APIFY_TOKEN environment variable.\n- Latency & Limits: Typical run duration is 5-20 seconds; output is capped by max_results.\n\nUsage Guidelines:\n- When to use: Use for company-news monitoring, brand mentions, market intelligence, current-event research, and source discovery.\n- When NOT to use: Do not use for full article text, historical news archives, or verified fact checking.\n- Named alternatives: Use 'sec_edgar_filings' for official company filings, 'federal_register_search' for US agency publications, or 'europe_pmc_paper_search' for biomedical literature.", 'inputSchema': {'type': 'object', 'properties': {'query': {'type': 'string', 'description': 'Company, person, product, topic, or quoted phrase to search.'}, 'language': {'type': 'string', 'default': 'en', 'description': 'Two-letter Google News language code.'}, 'country': {'type': 'string', 'default': 'US', 'description': 'Two-letter Google News country edition.'}, 'max_results': {'type': 'integer', 'minimum': 1, 'maximum': 100, 'default': 10, 'description': 'Maximum news records to return.'}}, 'required': ['query']}, 'outputSchema': {'type': 'object', 'properties': {'results': {'type': 'array', 'items': {'type': 'object', 'properties': {'title': {'type': 'string', 'description': 'News headline.'}, 'source_name': {'type': 'string', 'description': 'Publisher name.'}, 'source_url': {'type': 'string', 'description': 'Publisher website.'}, 'published_at': {'type': 'string', 'description': 'Publication timestamp normalized to UTC.'}, 'article_url': {'type': 'string', 'description': 'Google News result link.'}, 'snippet': {'type': 'string', 'description': 'Plain-text result snippet.'}, 'query': {'type': 'string', 'description': 'Search query used.'}}}}}, 'required': ['results']}, 'annotations': {'readOnlyHint': True, 'destructiveHint': False, 'idempotentHint': True, 'openWorldHint': True}},
    {'name': 'cve_vulnerability_intelligence', 'title': 'NVD CVE and CISA KEV Vulnerability Intelligence', 'description': "Search NIST NVD vulnerabilities and enrich every CVE with CISA Known Exploited Vulnerability status, remediation deadlines, ransomware use, CVSS, CWE, affected CPEs, and references.\n\nBehavioral Transparency:\n- Execution: Network call executed synchronously in the cloud via Apify Actor 'captainhandsome/nvd-cisa-vulnerability-intelligence'.\n- Side Effects: Strictly read-only; queries official NIST NVD and CISA KEV data.\n- Authentication: Requires APIFY_TOKEN environment variable; no NVD or CISA credential is required.\n- Latency & Limits: Typical exact and keyword runs take 5-30 seconds; NVD rate limits can slow large filtered jobs; output is capped by max_results.\n\nUsage Guidelines:\n- When to use: Use for CVE research, vulnerability triage, patch prioritization, and identifying active exploitation.\n- When NOT to use: Do not use as a network scanner or as proof that a particular deployed asset is vulnerable.\n- Named alternatives: Use 'tech_stack_detector' to identify public website technologies before researching relevant CVEs.", 'inputSchema': {'type': 'object', 'properties': {'query': {'type': 'string', 'description': 'Keyword, vendor, product, or phrase to search in NVD.'}, 'cve_id': {'type': 'string', 'description': 'Exact CVE ID; overrides query when supplied.'}, 'severity': {'type': 'string', 'enum': ['LOW', 'MEDIUM', 'HIGH', 'CRITICAL'], 'description': 'Optional CVSS v3 severity filter.'}, 'published_start': {'type': 'string', 'description': 'Optional NVD start timestamp; supply with published_end.'}, 'published_end': {'type': 'string', 'description': 'Optional NVD end timestamp; supply with published_start.'}, 'known_exploited_only': {'type': 'boolean', 'default': False, 'description': 'Return only CVEs currently in CISA KEV.'}, 'max_references': {'type': 'integer', 'minimum': 0, 'maximum': 500, 'default': 50, 'description': 'Maximum reference URLs retained per CVE.'}, 'max_cpes': {'type': 'integer', 'minimum': 0, 'maximum': 2000, 'default': 100, 'description': 'Maximum affected CPE criteria retained per CVE.'}, 'max_results': {'type': 'integer', 'minimum': 1, 'maximum': 100, 'default': 10, 'description': 'Maximum vulnerability records to return.'}}}, 'outputSchema': {'type': 'object', 'properties': {'results': {'type': 'array', 'items': {'type': 'object', 'properties': {'cve_id': {'type': 'string', 'description': 'Canonical CVE identifier.'}, 'description': {'type': 'string', 'description': 'English NVD vulnerability description.'}, 'published_at': {'type': 'string', 'description': 'NVD publication timestamp.'}, 'cvss_score': {'type': 'number', 'description': 'Highest available base CVSS score.'}, 'cvss_severity': {'type': 'string', 'description': 'Severity for the selected CVSS metric.'}, 'cwe_ids': {'type': 'array', 'items': {'type': 'string'}, 'description': 'CWE weakness identifiers.'}, 'affected_cpes': {'type': 'array', 'items': {'type': 'string'}, 'description': 'Bounded affected CPE list.'}, 'is_known_exploited': {'type': 'boolean', 'description': 'Whether CISA lists the CVE in KEV.'}, 'kev_required_action': {'type': 'string', 'description': 'CISA remediation action.'}, 'kev_due_date': {'type': 'string', 'description': 'CISA federal remediation due date.'}, 'kev_known_ransomware_campaign_use': {'type': 'string', 'description': 'CISA ransomware-use indicator.'}}}}}, 'required': ['results']}, 'annotations': {'readOnlyHint': True, 'destructiveHint': False, 'idempotentHint': True, 'openWorldHint': True}},
]

def server_version() -> str:
    """Version of the running server: the installed distribution, else the
    manifest next to this file when run from a source checkout."""
    try:
        from importlib.metadata import version
        return version("apify-data-scrapers")
    except Exception:
        try:
            with open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "manifest.json"), encoding="utf-8") as fh:
                return json.load(fh).get("version", "0.0.0")
        except Exception:
            return "0.0.0"


def get_token() -> str:
    token = os.environ.get("APIFY_TOKEN")
    if not token:
        raise ValueError("APIFY_TOKEN is not set. Tool calls run on your own Apify account: create a free token at "
                         "https://console.apify.com/settings/integrations and put it in the server's APIFY_TOKEN "
                         "environment variable (or the 'Apify API token' field of the Smithery/Claude install).")
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
                        "version": server_version()
                    },
                    "instructions": (
                        f"Apify Public Data MCP exposes {len(TOOLS_DEFINITION)} public-data extraction tools: "
                        "business leads (Google Maps, website tech stack), jobs (LinkedIn, Glassdoor), "
                        "corporate and public records (SEC EDGAR, GLEIF, US state business registries, "
                        "contractor licences, French companies), US government data (USAspending, FEC, EPA, "
                        "Census geocoding, CMS providers), research and health (ClinicalTrials.gov, openFDA, "
                        "Europe PMC), and media (Airbnb, YouTube, Twitch, Google Play reviews). Each call runs "
                        "an Apify Actor on the caller's own account and returns JSON records; runs need the "
                        "APIFY_TOKEN environment variable and typically take 5-60 seconds."
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
                elif tool_name == "google_autocomplete_keywords":
                    _queries = tool_args.get("queries")
                    _language = tool_args.get("language", 'en')
                    _country = tool_args.get("country", 'US')
                    _expansion_mode = tool_args.get("expansion_mode", 'none')
                    _max_results = tool_args.get("max_results", 25)
                    _payload = {"queries": [str(x) for x in (_queries if isinstance(_queries, list) else [_queries])], "language": str(_language), "country": str(_country), "expansion_mode": str(_expansion_mode), "max_items": min(int(_max_results or 10), 100)}
                    data = run_actor_sync(ACTORS["google_autocomplete_keywords"], _payload)
                elif tool_name == "google_news_search":
                    _query = tool_args.get("query")
                    _language = tool_args.get("language", 'en')
                    _country = tool_args.get("country", 'US')
                    _max_results = tool_args.get("max_results", 10)
                    _payload = {"query": str(_query), "language": str(_language), "country": str(_country), "max_items": min(int(_max_results or 10), 100)}
                    data = run_actor_sync(ACTORS["google_news"], _payload)
                elif tool_name == "cve_vulnerability_intelligence":
                    _query = tool_args.get("query")
                    _cve_id = tool_args.get("cve_id")
                    _severity = tool_args.get("severity")
                    _published_start = tool_args.get("published_start")
                    _published_end = tool_args.get("published_end")
                    _known_exploited_only = tool_args.get("known_exploited_only", False)
                    _max_references = tool_args.get("max_references", 50)
                    _max_cpes = tool_args.get("max_cpes", 100)
                    _max_results = tool_args.get("max_results", 10)
                    _payload = {"kev_only": _known_exploited_only, "max_references": int(_max_references), "max_cpes": int(_max_cpes), "max_items": min(int(_max_results or 10), 100)}
                    if _query is not None: _payload["query"] = str(_query)
                    if _cve_id is not None: _payload["cve_id"] = str(_cve_id)
                    if _severity is not None: _payload["severity"] = str(_severity)
                    if _published_start is not None: _payload["published_start"] = str(_published_start)
                    if _published_end is not None: _payload["published_end"] = str(_published_end)
                    data = run_actor_sync(ACTORS["cve_vulnerability_intelligence"], _payload)
                elif tool_name == "grants_gov_opportunity_search":
                    _keyword = tool_args.get("keyword")
                    _opportunity_number = tool_args.get("opportunity_number")
                    _agency_codes = tool_args.get("agency_codes")
                    _statuses = tool_args.get("statuses")
                    _assistance_listing = tool_args.get("assistance_listing")
                    _include_details = tool_args.get("include_details", True)
                    _max_results = tool_args.get("max_results", 10)
                    _payload = {"include_details": _include_details, "max_items": min(int(_max_results or 10), 100)}
                    if _keyword is not None: _payload["keyword"] = _keyword
                    if _opportunity_number is not None: _payload["opportunity_number"] = _opportunity_number
                    if _agency_codes is not None: _payload["agency_codes"] = [str(x) for x in (_agency_codes if isinstance(_agency_codes, list) else [_agency_codes])]
                    if _statuses is not None: _payload["statuses"] = [str(x) for x in (_statuses if isinstance(_statuses, list) else [_statuses])]
                    if _assistance_listing is not None: _payload["assistance_listing"] = _assistance_listing
                    data = run_actor_sync(ACTORS["grants_gov_opportunity"], _payload)
                elif tool_name == "nhtsa_vehicle_recall_search":
                    _make = tool_args.get("make")
                    _model = tool_args.get("model")
                    _model_year = tool_args.get("model_year")
                    _campaign_number = tool_args.get("campaign_number")
                    _max_results = tool_args.get("max_results", 10)
                    _payload = {"max_items": min(int(_max_results or 10), 100)}
                    if _make is not None: _payload["make"] = _make
                    if _model is not None: _payload["model"] = _model
                    if _model_year is not None: _payload["model_year"] = int(_model_year)
                    if _campaign_number is not None: _payload["campaign_number"] = _campaign_number
                    data = run_actor_sync(ACTORS["nhtsa_vehicle_recall"], _payload)
                elif tool_name == "ofac_sanctions_search":
                    _name = tool_args.get("name")
                    _match_mode = tool_args.get("match_mode", 'contains')
                    _program = tool_args.get("program")
                    _country = tool_args.get("country")
                    _entity_type = tool_args.get("entity_type")
                    _list_scope = tool_args.get("list_scope", 'all')
                    _include_aliases = tool_args.get("include_aliases", True)
                    _max_results = tool_args.get("max_results", 10)
                    _payload = {"name": _name, "match_mode": _match_mode, "list_scope": _list_scope, "include_aliases": _include_aliases, "max_items": min(int(_max_results or 10), 100)}
                    if _program is not None: _payload["program"] = _program
                    if _country is not None: _payload["country"] = _country
                    if _entity_type is not None: _payload["entity_type"] = _entity_type
                    data = run_actor_sync(ACTORS["ofac_sanctions"], _payload)
                elif tool_name == "sec_form_4_insider_transactions":
                    _company = tool_args.get("company")
                    _date_from = tool_args.get("date_from")
                    _date_to = tool_args.get("date_to")
                    _transaction_codes = tool_args.get("transaction_codes")
                    _include_derivative = tool_args.get("include_derivative", True)
                    _include_amendments = tool_args.get("include_amendments", True)
                    _max_filings = tool_args.get("max_filings", 100)
                    _max_results = tool_args.get("max_results", 10)
                    _payload = {"company": _company, "include_derivative": _include_derivative, "include_amendments": _include_amendments, "max_filings": int(_max_filings), "max_items": min(int(_max_results or 10), 100)}
                    if _date_from is not None: _payload["date_from"] = _date_from
                    if _date_to is not None: _payload["date_to"] = _date_to
                    if _transaction_codes is not None: _payload["transaction_codes"] = [str(x) for x in (_transaction_codes if isinstance(_transaction_codes, list) else [_transaction_codes])]
                    data = run_actor_sync(ACTORS["sec_form_4_insider_transactions"], _payload)
                elif tool_name == "ted_eu_tender_search":
                    _keywords = tool_args.get("keywords")
                    _buyer_name = tool_args.get("buyer_name")
                    _buyer_country = tool_args.get("buyer_country")
                    _cpv_code = tool_args.get("cpv_code")
                    _publication_date_from = tool_args.get("publication_date_from")
                    _publication_date_to = tool_args.get("publication_date_to")
                    _language = tool_args.get("language", 'eng')
                    _sort_direction = tool_args.get("sort_direction", 'desc')
                    _max_results = tool_args.get("max_results", 10)
                    _payload = {"language": _language, "sort_direction": _sort_direction, "max_items": min(int(_max_results or 10), 100)}
                    if _keywords is not None: _payload["keywords"] = _keywords
                    if _buyer_name is not None: _payload["buyer_name"] = _buyer_name
                    if _buyer_country is not None: _payload["buyer_country"] = _buyer_country
                    if _cpv_code is not None: _payload["cpv_code"] = _cpv_code
                    if _publication_date_from is not None: _payload["publication_date_from"] = _publication_date_from
                    if _publication_date_to is not None: _payload["publication_date_to"] = _publication_date_to
                    data = run_actor_sync(ACTORS["ted_eu_tender"], _payload)
                elif tool_name == "cms_healthcare_provider_search":
                    _provider_types = tool_args.get("provider_types")
                    _state = tool_args.get("state")
                    _city = tool_args.get("city")
                    _zip = tool_args.get("zip")
                    _county = tool_args.get("county")
                    _name_contains = tool_args.get("name_contains")
                    _max_results = tool_args.get("max_results", 10)
                    _payload = {"max_items": min(int(_max_results or 10), 100)}
                    if _provider_types is not None: _payload["provider_types"] = _provider_types
                    if _state is not None: _payload["state"] = _state
                    if _city is not None: _payload["city"] = _city
                    if _zip is not None: _payload["zip"] = _zip
                    if _county is not None: _payload["county"] = _county
                    if _name_contains is not None: _payload["name_contains"] = _name_contains
                    data = run_actor_sync(ACTORS["cms_healthcare_provider"], _payload)
                elif tool_name == "europe_pmc_paper_search":
                    _query = tool_args.get("query")
                    _author = tool_args.get("author")
                    _journal = tool_args.get("journal")
                    _year_from = tool_args.get("year_from")
                    _year_to = tool_args.get("year_to")
                    _open_access_only = tool_args.get("open_access_only")
                    _has_abstract_only = tool_args.get("has_abstract_only")
                    _sort_by = tool_args.get("sort_by", 'relevance')
                    _include_entities = tool_args.get("include_entities", False)
                    _max_results = tool_args.get("max_results", 10)
                    _payload = {"query": _query, "sort_by": _sort_by, "include_entities": _include_entities, "max_items": min(int(_max_results or 10), 100)}
                    if _author is not None: _payload["author"] = _author
                    if _journal is not None: _payload["journal"] = _journal
                    if _year_from is not None: _payload["year_from"] = int(_year_from)
                    if _year_to is not None: _payload["year_to"] = int(_year_to)
                    if _open_access_only is not None: _payload["open_access_only"] = _open_access_only
                    if _has_abstract_only is not None: _payload["has_abstract_only"] = _has_abstract_only
                    data = run_actor_sync(ACTORS["europe_pmc_paper"], _payload)
                elif tool_name == "gleif_lei_search":
                    _query = tool_args.get("query")
                    _search_mode = tool_args.get("search_mode", 'name')
                    _country = tool_args.get("country")
                    _jurisdiction = tool_args.get("jurisdiction")
                    _status = tool_args.get("status")
                    _include_relationships = tool_args.get("include_relationships", False)
                    _max_results = tool_args.get("max_results", 10)
                    _payload = {"search_mode": _search_mode, "include_relationships": _include_relationships, "max_items": min(int(_max_results or 10), 100)}
                    if _query is not None: _payload["query"] = _query
                    if _country is not None: _payload["country"] = _country
                    if _jurisdiction is not None: _payload["jurisdiction"] = _jurisdiction
                    if _status is not None: _payload["status"] = _status
                    data = run_actor_sync(ACTORS["gleif_lei"], _payload)
                elif tool_name == "tech_stack_detector":
                    _urls = tool_args.get("urls")
                    _include_details = tool_args.get("include_details", False)
                    _max_results = tool_args.get("max_results", 10)
                    _payload = {"urls": _urls, "include_details": _include_details, "max_items": min(int(_max_results or 10), 100)}
                    data = run_actor_sync(ACTORS["tech_stack_detector"], _payload)
                elif tool_name == "us_census_geocoder":
                    _addresses = tool_args.get("addresses")
                    _benchmark = tool_args.get("benchmark", 'Public_AR_Current')
                    _vintage = tool_args.get("vintage", 'Current_Current')
                    _max_results = tool_args.get("max_results", 10)
                    _payload = {"addresses": _addresses, "benchmark": _benchmark, "vintage": _vintage, "max_items": min(int(_max_results or 10), 100)}
                    data = run_actor_sync(ACTORS["us_census_geocoder"], _payload)
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

        elif method == "resources/templates/list":
            res = {"jsonrpc": "2.0", "id": req_id, "result": {"resourceTemplates": []}}
            sys.stdout.write(json.dumps(res) + "\n")
            sys.stdout.flush()

        elif req_id is not None:
            # A request the server does not implement must still get an answer:
            # JSON-RPC -32601. Silence here made LobeHub's inspector (and any
            # client that probes resources/templates/list) wait until timeout.
            res = {"jsonrpc": "2.0", "id": req_id,
                   "error": {"code": -32601, "message": f"Method not found: {method}"}}
            sys.stdout.write(json.dumps(res) + "\n")
            sys.stdout.flush()
        # notifications without an id are ignored by design

def main():
    serve_stdio()

if __name__ == "__main__":
    main()
