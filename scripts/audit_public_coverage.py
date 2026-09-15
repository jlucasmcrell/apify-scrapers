#!/usr/bin/env python3
"""Audit MCP tools against the live public Apify Store inventory.

The MCP package is a public product, so every advertised tool must target a
public Actor. Verified specs must also be integrated before a release. The
release script runs this audit in strict mode to prevent tool-count drift and
private Actor tools from reaching users again.
"""
from __future__ import annotations

import argparse
import ast
import json
import urllib.parse
import urllib.request
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
STORE_URL = "https://api.apify.com/v2/store"


def actor_map() -> dict[str, str]:
    tree = ast.parse((ROOT / "mcp_server.py").read_text(encoding="utf-8"))
    for node in tree.body:
        if isinstance(node, ast.Assign) and any(
            isinstance(target, ast.Name) and target.id == "ACTORS"
            for target in node.targets
        ):
            values = ast.literal_eval(node.value)
            return {
                key: value.rsplit("/", 1)[-1]
                for key, value in values.items()
            }
    raise RuntimeError("ACTORS mapping not found in mcp_server.py")


def verified_spec_actors() -> set[str]:
    actors: set[str] = set()
    for path in sorted((ROOT / "specs").glob("*.json")):
        try:
            spec = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            continue
        if (
            isinstance(spec, dict)
            and spec.get("actor")
            and spec.get("tool")
            and spec.get("payload_mapping") is not None
            and spec.get("verification", {}).get("relevant") is True
        ):
            actors.add(spec["actor"])
    return actors


def store_items(username: str, *, agentic_only: bool = False) -> list[dict]:
    params: dict[str, object] = {"username": username, "limit": 100}
    if agentic_only:
        params["allowsAgenticUsers"] = "true"
    url = f"{STORE_URL}?{urllib.parse.urlencode(params)}"
    request = urllib.request.Request(url, headers={"User-Agent": "apify-mcp-release-audit/1.0"})
    with urllib.request.urlopen(request, timeout=30) as response:
        payload = json.load(response)
    data = payload.get("data") or {}
    if int(data.get("total") or 0) > int(data.get("limit") or 100):
        raise RuntimeError("Store inventory exceeds the audit's one-page limit")
    return data.get("items") or []


def audit(username: str) -> dict:
    actors = actor_map()
    defined = set(actors.values())
    specs = verified_spec_actors()
    public_items = store_items(username)
    public = {item["name"] for item in public_items}
    agentic = {
        item["name"] for item in store_items(username, agentic_only=True)
    }
    public_tools = defined & public
    return {
        "username": username,
        "mcp_tool_count": len(actors),
        "public_actor_count": len(public),
        "public_mcp_tool_count": len(public_tools),
        "agentic_public_mcp_tool_count": len(public_tools & agentic),
        "mcp_tools_with_private_actors": sorted(defined - public),
        "public_actors_without_mcp_tools": sorted(public - defined),
        "verified_specs_without_mcp_tools": sorted(specs - defined),
        "public_mcp_tools_not_agentic": sorted(public_tools - agentic),
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--username", default="captainhandsome")
    parser.add_argument("--json", action="store_true")
    parser.add_argument("--require-release-ready", action="store_true")
    args = parser.parse_args()

    report = audit(args.username)
    blockers = (
        report["mcp_tools_with_private_actors"]
        + report["public_actors_without_mcp_tools"]
        + sorted(set(report["verified_specs_without_mcp_tools"]) & set(report["public_actors_without_mcp_tools"]))
        + report["public_mcp_tools_not_agentic"]
    )
    report["release_ready"] = not blockers

    if args.json:
        print(json.dumps(report, indent=2))
    else:
        print(
            "MCP tools: {mcp_tool_count}; public Actors: {public_actor_count}; "
            "public tools: {public_mcp_tool_count}; agentic public tools: "
            "{agentic_public_mcp_tool_count}".format(**report)
        )
        for key in (
            "mcp_tools_with_private_actors",
            "public_actors_without_mcp_tools",
            "verified_specs_without_mcp_tools",
            "public_mcp_tools_not_agentic",
        ):
            if report[key]:
                print(f"{key}: {', '.join(report[key])}")
        print(f"release_ready: {report['release_ready']}")

    return 1 if args.require_release_ready and not report["release_ready"] else 0


if __name__ == "__main__":
    raise SystemExit(main())
