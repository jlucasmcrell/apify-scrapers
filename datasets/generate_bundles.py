import os
import json
import csv
import dotenv
import httpx

token = dotenv.dotenv_values(r"G:\apify-fleet\.env")["APIFY_TOKEN"]
headers = {"Authorization": f"Bearer {token}"}

targets = [
    {
        "name": "phoenix_hvac_leads",
        "dataset_id": "c81ia5q15g7epMOvL",
        "dir": r"G:\apify-scrapers\datasets\phoenix_hvac_leads",
        "base": "phoenix_hvac_leads",
        "title": "Phoenix HVAC Contractor & Local Business Leads (2026)",
        "actor": "captainhandsome/google-maps-business-search",
        "task": "captainhandsome/phoenix-hvac-company-leads",
        "desc": "Real verified extract of HVAC repair, installation, and commercial contractor businesses across Phoenix, Arizona including business names, phone numbers, full addresses, ratings, review counts, Google Maps URLs, and website domains. Generated via Apify Actor captainhandsome/google-maps-business-search."
    },
    {
        "name": "austin_software_jobs",
        "dataset_id": "FS30hdcH8ke4TQ30m",
        "dir": r"G:\apify-scrapers\datasets\austin_software_jobs",
        "base": "austin_software_jobs",
        "title": "Austin Software Engineer Job Postings with Normalized Dates",
        "actor": "captainhandsome/glassdoor-jobs-scraper",
        "task": "captainhandsome/austin-software-engineer-jobs",
        "desc": "Clean structured extract of active software engineering, full stack, and AI developer job listings in the Austin, Texas metro area. Includes canonical job URLs, company names, employer ratings, location tags, salary estimates, raw posting age (e.g. 24h, 3d), and normalized estimated posting dates. Generated via Apify Actor captainhandsome/glassdoor-jobs-scraper."
    },
    {
        "name": "california_contractors",
        "dataset_id": "Iq8SfYU8K6lrYbyug",
        "dir": r"G:\apify-scrapers\datasets\california_solar_contractors",
        "base": "california_licensed_contractors",
        "title": "California State Licensed Contractors Sample Registry",
        "actor": "captainhandsome/ca-contractor-license-search",
        "task": "captainhandsome/california-contractor-smith",
        "desc": "Public registry extract of verified California licensed specialty and general building contractors from the California Contractors State License Board (CSLB). Includes business names, license numbers, current license status, issue dates, expiration dates, and classifications. Generated via Apify Actor captainhandsome/ca-contractor-license-search."
    }
]

with httpx.Client(headers=headers, timeout=30) as client:
    for t in targets:
        ds_url = f"https://api.apify.com/v2/datasets/{t['dataset_id']}/items?clean=true"
        r = client.get(ds_url)
        items = r.json()
        print(f"Fetched {len(items)} items for {t['name']}")

        os.makedirs(t["dir"], exist_ok=True)
        
        # Save JSON
        json_path = os.path.join(t["dir"], f"{t['base']}.json")
        with open(json_path, "w", encoding="utf-8") as f:
            json.dump(items, f, indent=2)
            
        # Save CSV
        if items:
            csv_path = os.path.join(t["dir"], f"{t['base']}.csv")
            keys = list(items[0].keys())
            with open(csv_path, "w", newline="", encoding="utf-8") as f:
                writer = csv.DictWriter(f, fieldnames=keys)
                writer.writeheader()
                for row in items:
                    writer.writerow({k: str(row.get(k, "")) for k in keys})
                    
        # Save Dataset Card README.md for Kaggle & Hugging Face
        readme_path = os.path.join(t["dir"], "README.md")
        readme_content = f"""# {t['title']}

## Overview
This dataset contains clean, structured public data exported directly from production runs of Apify actors.
It serves as a benchmark and sample for lead generation, labor market intelligence, and compliance verification.

- **Source Actor:** [{t['actor']}](https://apify.com/{t['actor']})
- **Preconfigured Run Task:** [{t['task']}](https://apify.com/{t['task']})
- **Records in Sample:** {len(items)}
- **Formats Included:** CSV (`{t['base']}.csv`) and JSON (`{t['base']}.json`)

## Description
{t['desc']}

## Fields
"""
        if items:
            for k, v in items[0].items():
                example = str(v)[:60].replace("\n", " ")
                readme_content += f"- `{k}`: (e.g. `{example}`)\n"
                
        readme_content += f"""
## How to Fetch Live or Unlimited Data
To extract thousands of records, schedule recurring daily alerts, or run custom location/industry searches:

1. Visit the production Actor on Apify: **[{t['actor']}](https://apify.com/{t['actor']})**
2. Pass your target query parameters or run the preconfigured task: **[{t['task']}](https://apify.com/{t['task']})**
3. Export results directly into CSV, JSON, Google Sheets, or integrate into your AI workflow via the [apify-scrapers open-source repository](https://github.com/jlucasmcrell/apify-scrapers).

---
*Published by Joseph McRell (@captainhandsome). Open data for research, lead qualification, and software development.*
"""
        with open(readme_path, "w", encoding="utf-8") as f:
            f.write(readme_content)
            
        # Write Kaggle dataset metadata
        meta_path = os.path.join(t["dir"], "dataset-metadata.json")
        slug = t["name"].replace("_", "-")
        meta = {
            "title": t["title"],
            "id": f"jlucasmcrell/{slug}",
            "licenses": [{"name": "CC0-1.0"}],
            "description": t["desc"]
        }
        with open(meta_path, "w", encoding="utf-8") as f:
            json.dump(meta, f, indent=2)
            
        print(f"Generated complete Kaggle/HF bundle in {t['dir']}")
