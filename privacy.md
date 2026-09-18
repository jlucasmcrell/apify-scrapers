---
layout: default
title: "Privacy policy"
description: "What the Apify Public Data MCP server does and does not collect: no telemetry, no data leaves your machine except the Apify API calls you trigger."
permalink: /privacy/
---

# Privacy policy

*Last updated 18 September 2026. Applies to the `apify-data-scrapers` MCP server, its MCPB desktop extension, and this website.*

## The short version

The MCP server runs on your own machine. It collects nothing, stores nothing, and sends nothing to us. Its only outbound calls are to the Apify API, with your own token, to run the Actor you asked for.

## What the MCP server collects

**Nothing.** There is no telemetry, no analytics, no crash reporting and no phone-home of any kind in the server. We operate no server that your installation contacts, so we never receive your queries, your results, your token or your IP address.

## What the MCP server sends, and where

When a tool is called, the server makes one HTTPS request to `api.apify.com` containing:

- your Apify API token, read from the `APIFY_TOKEN` environment variable, and
- the arguments you (or your AI client) supplied for that tool.

Apify runs the Actor on **your** Apify account and bills it to you. Your use of Apify is governed by [Apify's privacy policy](https://apify.com/privacy-policy) and terms, not by this one. Results are returned to your client and are not retained by the server.

Each Actor in turn fetches from the public source it is named for — Google Maps, SEC EDGAR, USAspending, and so on. Those sources see requests from Apify's infrastructure, not from you directly.

## Credentials

`APIFY_TOKEN` is read from the environment at call time and used only in the `Authorization` header of the request to Apify. It is never logged, never written to disk by the server, and never transmitted anywhere else. If the token is absent, the server returns an error telling you where to create one; it does not fall back to any shared credential.

## Data retention

The server keeps no database, no cache and no log file. Anything retained lives in your own Apify account (run history and datasets, under your control and deletable there) and in your MCP client's conversation history.

## Children

The tools return public business, government and research records. The server is not directed at children and collects no personal data from anyone.

## This website

`apify.revenuesystemslabs.com` is a static site. It uses [GoatCounter](https://www.goatcounter.com/privacy) for page counts: no cookies, no cross-site tracking, no personal data, no consent banner needed. GoatCounter records the page path, referrer, and a coarse browser/country string derived without storing your IP address. Nothing else on the site tracks you.

## Third parties

We sell nothing, share nothing, and have no advertising or data-broker relationships. The only third party involved in normal use is Apify, because that is where your Actor runs, on your own account.

## Changes

Material changes will be published on this page with a new date, and the version that ships in the extension manifest will point here.

## Contact

Open an issue at [github.com/jlucasmcrell/apify-scrapers](https://github.com/jlucasmcrell/apify-scrapers/issues), or email jlucasmcrell@gmail.com.
