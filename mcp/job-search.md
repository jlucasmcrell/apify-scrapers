---
layout: default
title: "MCP server for job search: LinkedIn and Glassdoor listings"
description: "An MCP server for job search that lets an AI agent fetch LinkedIn and Glassdoor job listings, company names, locations, and salary estimates as JSON."
permalink: /mcp/job-search/
---

# MCP server for job search: LinkedIn and Glassdoor listings

[Apify Public Data MCP](/) is a 25-tool MCP server, and two of those tools make it an MCP server for job search: linkedin_jobs_search and glassdoor_jobs_search. Each one runs as its own Apify Actor on your own Apify account. Together they let an agent pull public job postings, hiring companies, and Glassdoor's estimated salary and rating data without any scraping code of your own.

## What an agent can ask

- Find data engineer openings in Seattle on LinkedIn.
  -> linkedin_jobs_search(search_query="data engineer", location="Seattle, WA")
- What is Glassdoor showing for registered nurse pay in Austin?
  -> glassdoor_jobs_search(job_title="Registered Nurse", location="Austin, TX")
- Pull the full descriptions for the first 20 DevOps Architect roles on LinkedIn nationwide.
  -> linkedin_jobs_search(search_query="DevOps Architect", max_results=20, include_details=true)
- How does Glassdoor rate companies hiring software engineers in New York?
  -> glassdoor_jobs_search(job_title="Software Engineer", location="New York, NY", max_results=25)
- Get remote data analyst listings from Glassdoor.
  -> glassdoor_jobs_search(job_title="Data Analyst", location="Remote")
- Find registered nurse job listings in Dallas, titles and links only.
  -> linkedin_jobs_search(search_query="registered nurse", location="Dallas, TX", include_details=false)
- Look up commercial contacts for HVAC contractors near a hiring market in Phoenix.
  -> google_maps_search(search_query="HVAC contractors in Phoenix, AZ")

## Tools

### linkedin_jobs_search - LinkedIn Public Job Listings Search

Searches public LinkedIn job postings by keyword and location without logging in. It is strictly read-only: it does not log into LinkedIn, apply to jobs, or modify any LinkedIn account, and each call returns the role title, hiring company, location, posting date, and job URL for every match.

| Argument | Required | What it does |
| --- | --- | --- |
| search_query | Yes | Job title, skill, or keyword to search in public LinkedIn job listings (e.g. 'data engineer' or 'registered nurse'). |
| location | No | City, region, or country used to localize results (e.g. 'Seattle, WA'). Defaults to all locations if empty. default: "" |
| max_results | No | Maximum number of job listings to retrieve. default: 10 |
| include_details | No | When true, opens each job posting to add seniority level, employment type, job function, industries, applicant count, and full job description. Costs one extra request per job, so runs take noticeably longer. default: false |

Returns: title, company, location, url, posted_at, posted_at_timestamp, job_id, company_url

Price: $0.001 per result plus $0.001 Actor-start per run (free-tier price; 10-30% lower on paid Apify plans)

Store listing: [LinkedIn Jobs Scraper - Public Job Listings Search API](https://apify.com/captainhandsome/linkedin-public-jobs-search)

Not for: LinkedIn people or profile search, private candidate data, or submitting job applications.

### glassdoor_jobs_search - Glassdoor Active Job Postings and Salary Search

Searches active employment vacancies, hiring employers, estimated compensation bands, and corporate ratings from Glassdoor. It is read-only and never submits an application or touches an account; it just reads what Glassdoor already publishes about the role, the pay estimate, and the employer's rating.

| Argument | Required | What it does |
| --- | --- | --- |
| job_title | Yes | Target job title, professional role, or occupational keyword (e.g. 'Software Engineer', 'Data Analyst', or 'DevOps Architect'). |
| location | No | Geographic municipality, metropolitan area, or 'Remote' filter (e.g. 'Austin, TX' or 'New York, NY'). Defaults to all locations if empty. default: "" |
| max_results | No | Maximum number of active job listings to retrieve. Integer between 1 and 100. default: 10 |

Returns: jobTitle, companyName, location, salaryEstimate, rating, jobUrl

Price: $0.0004 per result plus $0.001 Actor-start per run (free-tier price; 10-30% lower on paid Apify plans)

Store listing: [Glassdoor Job Listings Scraper - Salary & Company Reviews Data](https://apify.com/captainhandsome/glassdoor-jobs-scraper)

Not for: local commercial lead generation, corporate financial filings, or live video streaming.

## Pairs well with

- google_maps_search - adds phone numbers, addresses, and review ratings for a hiring company's physical locations - [Store](https://apify.com/captainhandsome/google-maps-business-search)
- tech_stack_detector - adds the CMS, hosting, analytics, and other technology detected on a hiring company's own website - [Store](https://apify.com/captainhandsome/tech-stack-detector)

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
- [/mcp/government-data/](/mcp/government-data/)
- [/](/)

## FAQ

**Does this need my own Apify account?** Yes. Both tools require the APIFY_TOKEN environment variable, and each run bills your own Apify account rather than a shared one.

**How long does a search take?** linkedin_jobs_search has a typical run duration of 15-40 seconds with a timeout capped at 120 seconds. glassdoor_jobs_search runs in the same 15-40 second range with the same 120-second cap.

**What won't these tools give me?** linkedin_jobs_search is not for LinkedIn people or profile search, private candidate data, or submitting job applications. glassdoor_jobs_search is not for local commercial lead generation, corporate financial filings, or live video streaming.

**How do results come back?** As JSON records, one per listing. linkedin_jobs_search rows carry title, company, location, url, posted_at, posted_at_timestamp, job_id, and company_url. glassdoor_jobs_search rows carry jobTitle, companyName, location, salaryEstimate, rating, and jobUrl.
