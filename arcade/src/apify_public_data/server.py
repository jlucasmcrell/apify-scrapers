#!/usr/bin/env python3
"""Arcade MCP server for a focused set of Apify public-data tools."""

import json
import sys
import urllib.error
import urllib.request
from typing import Annotated, Any, Literal

from arcade_mcp_server import Context, MCPApp
from arcade_mcp_server.metadata import (
    Behavior,
    Classification,
    Operation,
    ServiceDomain,
    ToolMetadata,
)

APIFY_API_BASE = "https://api.apify.com/v2"
APIFY_ACTORS = {
    "gleif_lei": "captainhandsome/gleif-lei-search",
    "grants_gov_opportunity": "captainhandsome/grants-gov-opportunity-search",
    "ofac_sanctions": "captainhandsome/ofac-sanctions-search",
    "sec_edgar": "captainhandsome/sec-edgar-filings-search",
    "ted_eu_tender": "captainhandsome/ted-eu-tender-search",
    "usaspending": "captainhandsome/usaspending-federal-awards",
}

app = MCPApp(
    name="apify_public_data",
    version="1.0.0",
    title="Apify Public Data Intelligence",
    description=(
        "Read-only company, sanctions, securities, grant, and public-procurement "
        "research tools backed by the Apify Public Data Fleet."
    ),
    website_url="https://github.com/jlucasmcrell/apify-scrapers",
)


def _metadata(*domains: ServiceDomain) -> ToolMetadata:
    return ToolMetadata(
        classification=Classification(service_domains=list(domains)),
        behavior=Behavior(
            operations=[Operation.READ],
            read_only=True,
            destructive=False,
            idempotent=True,
            open_world=True,
        ),
    )


def _max_items(value: int, maximum: int = 100) -> int:
    value = int(value)
    if value < 1 or value > maximum:
        raise ValueError(f"max_results must be between 1 and {maximum}.")
    return value


def _run_actor(
    context: Context,
    actor_id: str,
    run_input: dict[str, Any],
    timeout_secs: int = 120,
) -> dict[str, Any]:
    token = context.get_secret("APIFY_TOKEN")
    clean_id = actor_id.replace("/", "~")
    url = (
        f"{APIFY_API_BASE}/acts/{clean_id}/run-sync-get-dataset-items"
        f"?timeout={timeout_secs}"
    )
    request = urllib.request.Request(
        url,
        data=json.dumps(run_input).encode("utf-8"),
        headers={
            "Accept": "application/json",
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
        },
        method="POST",
    )

    try:
        with urllib.request.urlopen(request, timeout=timeout_secs + 10) as response:
            results = json.loads(response.read().decode("utf-8"))
    except urllib.error.HTTPError as error:
        detail = error.read().decode("utf-8", errors="ignore")
        raise RuntimeError(f"Apify API error ({error.code}): {detail}") from error
    except Exception as error:
        raise RuntimeError(f"Actor run failed: {error}") from error

    if not isinstance(results, list):
        raise TypeError("The Apify Actor returned an unexpected non-list result.")
    return {"results": results}


@app.tool(
    requires_secrets=["APIFY_TOKEN"],
    metadata=_metadata(ServiceDomain.FINANCIAL_DATA, ServiceDomain.BUSINESS_INTELLIGENCE),
)
def gleif_lei_search(
    context: Context,
    query: Annotated[str, "Company name, exact LEI, or free text to search for."],
    search_mode: Annotated[
        Literal["name", "fulltext", "lei"],
        "Interpret query as a legal name, full-record text, or exact 20-character LEI.",
    ] = "name",
    country: Annotated[
        str | None,
        "Optional two-letter ISO country code for the entity's legal address.",
    ] = None,
    jurisdiction: Annotated[
        str | None,
        "Optional two-letter registering-jurisdiction code.",
    ] = None,
    status: Annotated[
        Literal["ACTIVE", "INACTIVE"] | None,
        "Optional entity operating status.",
    ] = None,
    include_relationships: Annotated[
        bool,
        "Also retrieve parent, subsidiary, and ISIN relationships; this is slower.",
    ] = False,
    max_results: Annotated[int, "Maximum LEI records to return, from 1 to 100."] = 10,
) -> Annotated[dict[str, Any], "Matching official GLEIF legal-entity records"]:
    """Search the official GLEIF register for legal entities and LEI records."""
    payload: dict[str, Any] = {
        "search_mode": search_mode,
        "include_relationships": include_relationships,
        "max_items": _max_items(max_results),
        "query": query,
    }
    if country is not None:
        payload["country"] = country
    if jurisdiction is not None:
        payload["jurisdiction"] = jurisdiction
    if status is not None:
        payload["status"] = status
    return _run_actor(context, APIFY_ACTORS["gleif_lei"], payload)


@app.tool(
    requires_secrets=["APIFY_TOKEN"],
    metadata=_metadata(ServiceDomain.FINANCIAL_DATA, ServiceDomain.BUSINESS_INTELLIGENCE),
)
def ofac_sanctions_search(
    context: Context,
    name: Annotated[str, "Case-insensitive primary or alias name to search."],
    match_mode: Annotated[
        Literal["contains", "exact"],
        "Use substring discovery or exact normalized matching.",
    ] = "contains",
    program: Annotated[str | None, "Optional OFAC sanctions program code."] = None,
    country: Annotated[str | None, "Optional country filter."] = None,
    entity_type: Annotated[
        str | None,
        "Optional party type such as individual, entity, vessel, or aircraft.",
    ] = None,
    list_scope: Annotated[
        Literal["all", "sdn", "non_sdn"],
        "Search SDN, consolidated non-SDN, or both lists.",
    ] = "all",
    include_aliases: Annotated[bool, "Match alternate names as well as primary names."] = True,
    max_results: Annotated[int, "Maximum sanctions records to return, from 1 to 100."] = 10,
) -> Annotated[dict[str, Any], "Matching official OFAC sanctions records"]:
    """Search official US Treasury OFAC sanctions lists.

    Results are research matches, not legal compliance determinations.
    """
    payload: dict[str, Any] = {
        "name": name,
        "match_mode": match_mode,
        "list_scope": list_scope,
        "include_aliases": include_aliases,
        "max_items": _max_items(max_results),
    }
    if program is not None:
        payload["program"] = program
    if country is not None:
        payload["country"] = country
    if entity_type is not None:
        payload["entity_type"] = entity_type
    return _run_actor(context, APIFY_ACTORS["ofac_sanctions"], payload)


@app.tool(
    requires_secrets=["APIFY_TOKEN"],
    metadata=_metadata(ServiceDomain.FINANCIAL_DATA, ServiceDomain.BUSINESS_INTELLIGENCE),
)
def sec_edgar_filings(
    context: Context,
    ticker: Annotated[str, "Public-company ticker symbol or official company name."],
    form_type: Annotated[
        Literal["10-K", "10-Q", "8-K", "ALL"],
        "SEC form type, or ALL for any filing.",
    ] = "10-K",
    max_results: Annotated[int, "Maximum filing records to return, from 1 to 50."] = 5,
) -> Annotated[dict[str, Any], "Matching official SEC EDGAR filing records"]:
    """Retrieve official SEC EDGAR corporate filings by ticker or company."""
    return _run_actor(
        context,
        APIFY_ACTORS["sec_edgar"],
        {
            "company": ticker,
            "forms": [form_type],
            "max_items": _max_items(max_results, 50),
        },
    )


@app.tool(
    requires_secrets=["APIFY_TOKEN"],
    metadata=_metadata(ServiceDomain.SALES_INTELLIGENCE, ServiceDomain.BUSINESS_INTELLIGENCE),
)
def usaspending_contracts(
    context: Context,
    recipient_name: Annotated[
        str,
        "Legal name of the prime contractor, vendor, or recipient institution.",
    ],
    max_results: Annotated[int, "Maximum federal award records to return, from 1 to 100."] = 10,
) -> Annotated[dict[str, Any], "Matching official USAspending contract-award records"]:
    """Search official USAspending federal procurement and defense awards."""
    return _run_actor(
        context,
        APIFY_ACTORS["usaspending"],
        {
            "award_type": "contracts",
            "keywords": recipient_name,
            "max_items": _max_items(max_results),
        },
    )


@app.tool(
    requires_secrets=["APIFY_TOKEN"],
    metadata=_metadata(ServiceDomain.SALES_INTELLIGENCE, ServiceDomain.BUSINESS_INTELLIGENCE),
)
def ted_eu_tender_search(
    context: Context,
    keywords: Annotated[str | None, "Words or phrase to match in tender titles."] = None,
    buyer_name: Annotated[str | None, "Text to match in contracting-authority names."] = None,
    buyer_country: Annotated[
        str | None,
        "Optional ISO alpha-3 buyer country code, such as DEU or FRA.",
    ] = None,
    cpv_code: Annotated[str | None, "Optional eight-digit CPV classification code."] = None,
    publication_date_from: Annotated[
        str | None,
        "Optional earliest publication date in YYYY-MM-DD format.",
    ] = None,
    publication_date_to: Annotated[
        str | None,
        "Optional latest publication date in YYYY-MM-DD format.",
    ] = None,
    language: Annotated[str, "Three-letter TED language code."] = "eng",
    sort_direction: Annotated[
        Literal["desc", "asc"],
        "Sort by newest or oldest publication date first.",
    ] = "desc",
    max_results: Annotated[int, "Maximum tender notices to return, from 1 to 100."] = 10,
) -> Annotated[dict[str, Any], "Matching official TED public-procurement notices"]:
    """Search official EU Tenders Electronic Daily procurement notices."""
    payload: dict[str, Any] = {
        "language": language,
        "sort_direction": sort_direction,
        "max_items": _max_items(max_results),
    }
    optional_values = {
        "keywords": keywords,
        "buyer_name": buyer_name,
        "buyer_country": buyer_country,
        "cpv_code": cpv_code,
        "publication_date_from": publication_date_from,
        "publication_date_to": publication_date_to,
    }
    payload.update({key: value for key, value in optional_values.items() if value is not None})
    return _run_actor(context, APIFY_ACTORS["ted_eu_tender"], payload)


@app.tool(
    requires_secrets=["APIFY_TOKEN"],
    metadata=_metadata(ServiceDomain.BUSINESS_INTELLIGENCE, ServiceDomain.SALES_INTELLIGENCE),
)
def grants_gov_opportunity_search(
    context: Context,
    keyword: Annotated[str | None, "Keywords to search in opportunity titles and descriptions."] = None,
    opportunity_number: Annotated[
        str | None,
        "Exact or partial federal funding opportunity number.",
    ] = None,
    agency_codes: Annotated[
        list[str] | None,
        "One or more federal agency codes, such as NSF or HHS.",
    ] = None,
    statuses: Annotated[
        list[str] | None,
        "One or more statuses: forecasted, posted, closed, or archived.",
    ] = None,
    assistance_listing: Annotated[
        str | None,
        "Optional Assistance Listing number, formerly CFDA, such as 47.070.",
    ] = None,
    include_details: Annotated[
        bool,
        "Retrieve award, eligibility, synopsis, and contact details.",
    ] = True,
    max_results: Annotated[int, "Maximum opportunities to return, from 1 to 100."] = 10,
) -> Annotated[dict[str, Any], "Matching official Grants.gov funding opportunities"]:
    """Search official US federal funding opportunities from Grants.gov."""
    payload: dict[str, Any] = {
        "include_details": include_details,
        "max_items": _max_items(max_results),
    }
    if keyword is not None:
        payload["keyword"] = keyword
    if opportunity_number is not None:
        payload["opportunity_number"] = opportunity_number
    if agency_codes is not None:
        payload["agency_codes"] = [str(item) for item in agency_codes]
    if statuses is not None:
        payload["statuses"] = [str(item) for item in statuses]
    if assistance_listing is not None:
        payload["assistance_listing"] = assistance_listing
    return _run_actor(context, APIFY_ACTORS["grants_gov_opportunity"], payload)


if __name__ == "__main__":
    transport = sys.argv[1] if len(sys.argv) > 1 else "stdio"
    app.run(transport=transport, host="127.0.0.1", port=8000)
