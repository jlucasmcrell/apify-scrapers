---
layout: default
title: "US government data MCP server"
description: "An MCP server for US government data letting an AI agent query USAspending, FEC, EPA, Census, CMS, openFDA, and ClinicalTrials.gov data records."
permalink: /mcp/government-data/
---
# MCP server for US government data: USAspending, FEC, EPA, Census, CMS, openFDA, ClinicalTrials.gov

This is an MCP server for US government data: it exposes tools so an AI agent can query USAspending, FEC, EPA, Census, CMS, openFDA, ClinicalTrials.gov, SEC EDGAR, Grants.gov, and NHTSA records. Every tool runs as an Apify Actor on your own Apify account. This page is one of several use-case pages built on [Apify Public Data MCP](/), which exposes 30 tools total.

## What an agent can ask

- What federal contracts has Lockheed Martin been awarded? -> usaspending_contracts(recipient_name="Lockheed Martin", max_results=10)
- Is there an FEC candidate named Warren running for Senate in Massachusetts? -> fec_campaign_finance_search(data_type="candidates", name="Warren", state="MA", office="S")
- Which facilities in Rhode Island have Clean Air Act violations? -> epa_facility_search(state="RI", program="A")
- What census tract and congressional district is this address in? -> us_census_geocoder(addresses=["1600 Amphitheatre Pkwy, Mountain View, CA 94043"])
- List Medicare-certified hospitals in Houston, Texas -> cms_healthcare_provider_search(provider_types=["hospital"], state="TX", city="Houston")
- Has the FDA approved any drugs with semaglutide? -> openfda_search(dataset="drug_approval", search="semaglutide")
- Are there any recruiting clinical trials for Alzheimer's disease? -> clinical_trials_search(condition="Alzheimer disease", status="RECRUITING")
- Pull Tesla's latest 10-K annual report -> sec_edgar_filings(ticker="Tesla Inc", form_type="10-K", max_results=1)

## Tools

### usaspending_contracts - USAspending Federal Procurement and Defense Awards Search

Searches USAspending for federal contracts and defense awards by recipient name.

|Argument|Required|What it does|
|---|---|---|
|recipient_name|Yes|Contractor or recipient name.|
|max_results|No|Records to retrieve. default: 10|

Returns: award_family, award_id, recipient_name, award_type, amount, total_outlays, subsidy_cost, awarding_agency, awarding_sub_agency, start_date, end_date, pop_state, pop_city, pop_zip, naics_code, naics_description, psc_code, psc_description, cfda_number, description, url, recipient_uei, recipient_profile_url, recipient_address, recipient_city, recipient_state, recipient_country, awarding_agency_code, awarding_sub_agency_code, funding_agency, funding_agency_code, funding_sub_agency, funding_sub_agency_code, pop_country, pop_country_code, issued_date, last_date_to_order, base_obligation_date, last_modified_date, cfda_program_title, assistance_listings, def_codes, covid19_obligations, covid19_outlays, infrastructure_obligations, infrastructure_outlays, award_type_code, date_signed, potential_end_date, base_exercised_options, base_and_all_options, subaward_count, total_subaward_amount, parent_award_id, parent_award_type, parent_recipient_name, parent_recipient_uei, recipient_business_categories, recipient_county, recipient_congressional_district, pop_county, pop_congressional_district, awarding_office, funding_office, naics_sector_code, naics_sector_description, psc_category_code, psc_category_description, set_aside_type, extent_competed, other_than_full_and_open, number_of_offers_received, contract_pricing_type, solicitation_id, solicitation_procedures, executive_compensation, top_executive_name, top_executive_compensation, funding_opportunity_number, non_federal_funding, total_funding

Price: $0.003 per result plus $0.0005 Actor-start per run (free-tier price; 10-30% lower on paid Apify plans)

Store listing: [Store](https://apify.com/captainhandsome/usaspending-federal-awards)

Not for: retail leads, corporate SEC filings, or vacation pricing.

### fec_campaign_finance_search - FEC Campaign Finance Search

Searches FEC candidates, committees/PACs, or contributions; data_type picks one record type per call. Contributor addresses are never returned.

|Argument|Required|What it does|
|---|---|---|
|data_type|No|Register to search. default: candidates|
|name|No|Candidate, committee, or contributor name.|
|state|No|Two-letter state code.|
|party|No|Three-letter party code, candidates only.|
|office|No|Office sought: H, S, or P.|
|max_results|No|Records to retrieve. default: 10|

Returns: record_type, id, name, party, office, state, district, url

Price: $0.003 per result plus $0.0005 Actor-start per run (free-tier price; 10-30% lower on paid Apify plans)

Store listing: [Store](https://apify.com/captainhandsome/fec-campaign-finance-search)

Not for: corporate SEC filings, environmental compliance, clinical trials, or FDA data.

### epa_facility_search - EPA ECHO Facility Compliance Search

Searches EPA ECHO facilities by state, facility name, or NAICS code. Violations-only results by default.

|Argument|Required|What it does|
|---|---|---|
|state|Yes|Two-letter state code.|
|facility_name|No|Substring match on facility name.|
|naics_code|No|Industry NAICS code.|
|program|No|Program: A, W, S, or R.|
|max_results|No|Records to retrieve. default: 10|

Returns: registry_id, name, city, state, naics_codes, compliance_status, total_penalties, url

Price: $0.003 per result plus $0.0005 Actor-start per run (free-tier price; 10-30% lower on paid Apify plans)

Store listing: [Store](https://apify.com/captainhandsome/epa-echo-facility-search)

Not for: corporate registry, campaign finance, clinical trial, or FDA data.

### us_census_geocoder - US Census Address Geocoder

Geocodes US addresses into Census FIPS codes, tract/block GEOIDs, district, place, and metro area.

|Argument|Required|What it does|
|---|---|---|
|addresses|Yes|One or more US addresses.|
|benchmark|No|Address file to match. default: Public_AR_Current|
|vintage|No|Geography vintage. default: Current_Current|
|max_results|No|Address rows to bill for. default: 10|

Returns: input_address, matched, match_count, matched_address, latitude, longitude, city, state, zip, state_fips, county_fips, county_name, place_name, place_geoid, tract_geoid, block_group_geoid, block_geoid, zcta, urban_rural, congressional_district_geoid, cbsa_name, metro_area_name, school_district_name, benchmark_name, vintage_name

Price: $0.01 per result plus $0.0005 Actor-start per run (free-tier price; 10-30% lower on paid Apify plans)

Store listing: [Store](https://apify.com/captainhandsome/us-census-geocoder)

Not for: place search, driving directions, or non-US addresses.

### cms_healthcare_provider_search - CMS Healthcare Provider Search

Searches CMS directories for hospitals, nursing homes, and five other facility types in one row shape.

|Argument|Required|What it does|
|---|---|---|
|provider_types|No|Directory types, e.g. ['hospital'].|
|state|Yes|Two-letter state or territory code.|
|city|No|City name, exact match.|
|zip|No|Five-digit ZIP code.|
|county|No|County name, exact match.|
|name_contains|No|Substring match on provider name.|
|max_results|No|Records to retrieve. default: 10|

Returns: provider_type, ccn, name, address, city, state, zip, county, phone, ownership, subtype, star_rating, certification_date, beds, chain, emergency_services

Price: $0.02 per result plus $0.0005 Actor-start per run (free-tier price; 10-30% lower on paid Apify plans)

Store listing: [Store](https://apify.com/captainhandsome/cms-healthcare-provider-search)

Not for: clinical trial, environmental, campaign finance, or licensing data.

### openfda_search - openFDA Drug and Device Search

Searches openFDA labels, approvals (Drugs@FDA), adverse events (FAERS), or recalls; dataset picks which.

|Argument|Required|What it does|
|---|---|---|
|dataset|No|Dataset to search. default: drug_approval|
|search|Yes|Query term or field filter.|
|include_details|No|Add labeler/DEA schedule via NDC. default: false|
|max_results|No|Records to retrieve. default: 10|

Returns: dataset, id, brand_name, generic_name, manufacturer, substance, route, application_number

Price: $0.002 per result plus $0.0005 Actor-start per run (free-tier price; 10-30% lower on paid Apify plans)

Store listing: [Store](https://apify.com/captainhandsome/openfda-search)

Not for: clinical trial, environmental, campaign finance, or registry data.

### clinical_trials_search - ClinicalTrials.gov Study Search

Searches ClinicalTrials.gov studies by condition, intervention, sponsor, or keyword.

|Argument|Required|What it does|
|---|---|---|
|condition|Yes|Condition, intervention, sponsor, or keyword.|
|status|No|Recruitment status filter.|
|max_results|No|Records to retrieve. default: 10|

Returns: nct_id, title, status, phase, conditions, sponsor, enrollment, url

Price: $0.003 per result plus $0.0005 Actor-start per run (free-tier price; 10-30% lower on paid Apify plans)

Store listing: [Store](https://apify.com/captainhandsome/clinical-trials-search)

Not for: FDA approvals, environmental, campaign finance, or registry data.

### sec_edgar_filings - SEC EDGAR Public Corporate Filings Retrieval

Retrieves SEC EDGAR 10-K, 10-Q, or 8-K filings by ticker or company name.

|Argument|Required|What it does|
|---|---|---|
|ticker|Yes|Stock ticker or company name.|
|form_type|No|Filing type: 10-K, 10-Q, 8-K, or ALL. default: 10-K|
|max_results|No|Records to retrieve. default: 5|

Returns: cik, company_name, tickers, exchanges, sic, sic_description, state_of_incorporation, fiscal_year_end, form, is_amendment, filing_date, report_date, acceptance_datetime, accession_number, act, file_number, film_number, items, size_bytes, is_xbrl, is_inline_xbrl, primary_document, primary_document_description, filing_url, filing_url, company_submissions_url, ticker, exchange, entity_type, filer_category, owner_org, ein, phone, state_of_incorporation_description, business_address, business_address_street1, business_address_street2, business_address_city, business_address_state, business_address_state_description, business_address_zip, business_address_country, business_address_is_foreign, mailing_address, mailing_address_street1, mailing_address_street2, mailing_address_city, mailing_address_state, mailing_address_zip, mailing_address_country, former_names, current_name_since, has_insider_transactions_as_owner, has_insider_transactions_as_issuer, filing_directory_url, filing_txt_url, company_filings_url, document_count, document_types, exhibit_count, item_descriptions, filer_names, filer_ciks, reporting_owner_names, reporting_owner_ciks, issuer_name, issuer_cik, subject_company_name, subject_company_cik, group_members, filing_date_changed

Price: $0.002 per result plus $0.0005 Actor-start per run (free-tier price; 10-30% lower on paid Apify plans)

Store listing: [Store](https://apify.com/captainhandsome/sec-edgar-filings-search)

Not for: private company intelligence, real-time prices, or local leads.

## Pairs well with

- europe_pmc_paper_search - adds peer-reviewed biomedical literature (abstracts, citations, MeSH terms) alongside clinical trial and FDA records - [Store](https://apify.com/captainhandsome/europe-pmc-paper-search)

## Install the MCP server

The server is a Python stdio MCP server published on PyPI as `apify-data-scrapers`. Every tool runs an Apify Actor on **your own** Apify account, so you need a free Apify account and its API token (Apify Console -> Settings -> Integrations).

**Claude Desktop / Claude Code** - add to `claude_desktop_config.json` (or `.mcp.json`):

```json
{
  "mcpServers": {
    "apify-scrapers": {
      "command": "uvx",
      "args": ["apify-data-scrapers"],
      "env": { "APIFY_TOKEN": "YOUR_APIFY_API_TOKEN" }
    }
  }
}
```

**Cursor** - Settings -> MCP -> Add server, same command (`uvx apify-data-scrapers`) and the `APIFY_TOKEN` environment variable.

**Smithery** - one-click install from [smithery.ai/servers/jlucasmcrell/apify-scrapers](https://smithery.ai/servers/jlucasmcrell/apify-scrapers).

**Without an MCP client** - the same Actors are callable from Python (`apify-client`), Node.js, n8n, Make or the Apify Console; see the [project README](/).

## Other use-case pages

- [/mcp/sec-edgar/](/mcp/sec-edgar/)
- [/mcp/google-maps/](/mcp/google-maps/)
- [/mcp/public-records/](/mcp/public-records/)
- [/mcp/job-search/](/mcp/job-search/)
- [/](/)

## FAQ

**Does this need an API key?**
Yes. Every tool here requires the APIFY_TOKEN environment variable and runs as an Apify Actor on your own account, so usage bills you directly.

**How fast is a typical run?**
Most tools run 10-30 seconds; usaspending_contracts and epa_facility_search run 10-35 seconds; us_census_geocoder runs 10-60 seconds, matching five addresses at a time. All cap at 120 seconds.

**What isn't in this data?**
Each tool covers one source: usaspending_contracts skips SEC filings, fec_campaign_finance_search skips environmental and FDA data, and openfda_search and clinical_trials_search don't overlap.

**How are results returned?**
Each call returns flat JSON records with the fields listed under its tool above; usaspending_contracts, for example, returns recipientName, awardingAgency, obligationAmount, awardDescription, awardDate, and contractId.
