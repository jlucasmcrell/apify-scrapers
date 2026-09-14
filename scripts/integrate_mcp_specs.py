"""Integrate validated tool specs into mcp_server.py, manifest.json and the version files.

Input: one JSON spec per Actor (see the mcp-tool-expansion workflow) in SPEC_DIR:
  { actor, tool{name,title,description,inputSchema,outputSchema,annotations},
    payload_mapping{arg -> {key, transform}}, fixed_payload{key -> const}, example_call, verification }

What it emits, and why in this exact shape:
  - ACTORS entries: "<tool key>": "captainhandsome/<actor>".
  - TOOLS_DEFINITION entries appended verbatim from the spec.
  - Handler branches whose run_actor_sync payload is a LITERAL dict with string
    keys. tests/test_contracts.py::test_mcp_server_sends_only_keys_the_actor_accepts
    parses handler payloads with a regex over that literal form and checks every
    key against the Actor's input_schema.json. A payload built dynamically would
    be invisible to that test - and the whole reason this seam is guarded is
    that five tools once sent keys the Actors reject.
  - manifest.json tools: name + description ONLY (the MCPB validator rejects
    inputSchema there; scripts/build_smithery_bundle.py enriches at pack time).
  - Version bump in setup.py, package.json, server.json (x2), manifest.json.

Idempotent: a spec whose tool name already exists in TOOLS_DEFINITION is skipped.
usage: python scripts/integrate_mcp_specs.py [--spec-dir DIR] [--version 1.0.8] [--dry-run]
"""
from __future__ import annotations

import ast
import json
import re
import sys
from collections import OrderedDict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_SPEC_DIR = ROOT / "specs"

TRANSFORMS = {
    "identity": "{src}",
    "list": "[{src}] if not isinstance({src}, list) else {src}",
    "int": "int({src})",
    "str": "str({src})",
    "strlist": "[str(x) for x in ({src} if isinstance({src}, list) else [{src}])]",
    # google-play `scores`: the Actor's select-editor array wants "1".."5" strings.
    "int_list_to_str_list": "[str(x) for x in ({src} if isinstance({src}, list) else [{src}])]",
    # Sunbiz Actors take start_urls, not a search term: build the result-page URL
    # for the query (URL-encoded) and wrap it in a one-element list. Written here
    # from the spec notes, not copied from agent output.
    "sunbiz_entity_search_url": '["https://search.sunbiz.org/Inquiry/CorporationSearch/SearchResults?inquiryType=EntityName&searchTerm=" + urllib.parse.quote(str({src}))]',
    "sunbiz_officer_search_url": '["https://search.sunbiz.org/Inquiry/CorporationSearch/SearchResults?inquiryType=OfficerRegisteredAgentName&searchTerm=" + urllib.parse.quote(str({src}))]',
}


def transform_expr(name: str, src: str, spec_name: str, arg: str) -> str:
    """Resolve a transform by name, failing with the offending spec/arg named."""
    if name not in TRANSFORMS:
        raise SystemExit(f"{spec_name}.{arg}: unknown transform {name!r}; known: {sorted(TRANSFORMS)}")
    return TRANSFORMS[name].format(src=src)


def py_literal(value) -> str:
    """JSON value -> Python literal source.

    repr() is exact for str/int/float/bool/None/list/dict. The previous
    text-replace of true/false/null over json.dumps output would have rewritten
    every "true" inside a description ("structured" -> "sTrued").
    """
    return repr(value)


def sync_tool_count_claims(count: int) -> None:
    """Keep public metadata in lockstep with the generated MCP manifest."""
    claims = {
        "README.md": [
            (r"(# Apify Public Data MCP: )\d+", rf"\g<1>{count}"),
            (r"(One MCP server gives an AI agent \*\*)\d+", rf"\g<1>{count}"),
        ],
        "_config.yml": [
            (r"(tagline: )\d+", rf"\g<1>{count}"),
            (r"(description: Run )\d+", rf"\g<1>{count}"),
        ],
        "mcp/job-search.md": [
            (r"(is a )\d+(-tool MCP server)", rf"\g<1>{count}\g<2>"),
        ],
        "setup.py": [
            (r"(MCP server exposing )\d+( Apify)", rf"\g<1>{count}\g<2>"),
        ],
        "package.json": [
            (r"(MCP server exposing )\d+( Apify)", rf"\g<1>{count}\g<2>"),
        ],
        "server.json": [
            (r'(\"description\": \"?)\d+( Apify)', rf"\g<1>{count}\g<2>"),
        ],
        "mcp.json": [
            (r'(\"description\": \"?)\d+( Apify)', rf"\g<1>{count}\g<2>"),
            (r"(Apify Public Data MCP exposes )\d+( extraction tools)", rf"\g<1>{count}\g<2>"),
        ],
        "lhm.plugin.json": [
            (r"(MCP server exposing )\d+( Apify)", rf"\g<1>{count}\g<2>"),
        ],
    }
    for rel, replacements in claims.items():
        path = ROOT / rel
        text = path.read_text(encoding="utf-8")
        for pattern, replacement in replacements:
            text = re.sub(pattern, replacement, text, count=1)
        path.write_text(text, encoding="utf-8")


def handler_branch(spec: dict, actor_key: str) -> str:
    """One `elif tool_name == ...:` block with a literal-dict payload."""
    name = spec["tool"]["name"]
    lines = [f'                elif tool_name == "{name}":']
    payload_items = []
    for arg, m in (spec.get("payload_mapping") or {}).items():
        key = m["key"]
        var = f"_{arg}"
        # A default declared on the mapping OR on the tool's inputSchema means the
        # key is sent on every call (us-business-entity-search: omitting `sources`
        # silently narrows the Actor to Alabama only).
        default = m.get("default")
        if default is None:
            default = ((spec["tool"].get("inputSchema") or {}).get("properties") or {}).get(arg, {}).get("default")
        lines.append(f'                    {var} = tool_args.get("{arg}"{", " + py_literal(default) if default is not None else ""})')
        expr = transform_expr(m.get("transform", "identity"), var, name, arg)
        if key == "max_items":
            expr = f"min(int({var} or 10), 100)"
        # Only send optional args the caller actually set - filters must stay inert.
        payload_items.append((key, expr, var, bool(m.get("required", False) or default is not None)))
    fixed = spec.get("fixed_payload") or {}
    lines.append("                    _payload = {" + ", ".join(
        [f'"{k}": {py_literal(v)}' for k, v in fixed.items()]
        + [f'"{k}": {e}' for k, e, v, req in payload_items if req or k == "max_items"]) + "}")
    for k, e, v, req in payload_items:
        if not req and k != "max_items":
            lines.append(f'                    if {v} is not None: _payload["{k}"] = {e}')
    lines.append(f'                    data = run_actor_sync(ACTORS["{actor_key}"], _payload)')
    return "\n".join(lines) + "\n"


def main() -> int:
    args = sys.argv[1:]
    spec_dir = Path(args[args.index("--spec-dir") + 1]) if "--spec-dir" in args else DEFAULT_SPEC_DIR
    version = args[args.index("--version") + 1] if "--version" in args else "1.0.8"
    dry = "--dry-run" in args
    specs = []
    for p in sorted(spec_dir.glob("*.json")):
        try:
            s = json.loads(p.read_text(encoding="utf-8"))
        except Exception as exc:
            print(f"  skip {p.name}: not JSON ({exc})"); continue
        # Agents drop helper files next to their specs; only a real spec has both.
        if not (isinstance(s, dict) and "actor" in s and "tool" in s and "payload_mapping" in s):
            print(f"  skip {p.name}: not a tool spec"); continue
        if not s.get("verification", {}).get("relevant"):
            print(f"  skip {p.name}: NOT live-verified as relevant - refusing to integrate an unproven tool"); continue
        specs.append(s)
    if not specs:
        raise SystemExit(f"no verified specs in {spec_dir}")

    src_path = ROOT / "mcp_server.py"
    src = src_path.read_text(encoding="utf-8")
    # Parse, don't regex: the generated entries are single-quoted repr() dicts,
    # which a "name": "..." pattern misses - the 1.0.10 dry run offered to re-add
    # every one of them.
    existing = {t["name"] for t in ast.literal_eval(src.split("TOOLS_DEFINITION = ", 1)[1].split("\n]\n", 1)[0] + "\n]")}
    added = []
    actors_block, tools_block, handler_block = [], [], []
    for s in specs:
        name = s["tool"]["name"]
        if name in existing:
            print(f"  skip {name} (already defined)"); continue
        key = name.rsplit("_search", 1)[0] if name.endswith("_search") else name
        actors_block.append(f'    "{key}": "captainhandsome/{s["actor"]}",')
        tools_block.append("    " + py_literal(s["tool"]).replace("\n", "\n    ") + ",")
        handler_block.append(handler_branch(s, key))
        added.append(name)
    if not added:
        print("nothing to add"); return 0

    # 1. ACTORS dict: insert before its closing brace
    src = re.sub(r"(ACTORS = \{\n(?:.*\n)*?)(\})", lambda m: m.group(1) + "\n".join(actors_block) + "\n" + m.group(2), src, count=1)
    # 2. TOOLS_DEFINITION: insert before the closing bracket of the list
    head, rest = src.split("TOOLS_DEFINITION = ", 1)
    body, tail = rest.split("\n]\n", 1)
    if not body.rstrip().endswith(","):
        body = body.rstrip() + ","          # last existing entry has no trailing comma
    src = head + "TOOLS_DEFINITION = " + body + "\n" + "\n".join(tools_block) + "\n]\n" + tail
    # 3. handler: insert the new branches after the last existing elif that calls run_actor_sync
    anchor = re.search(r'(                elif tool_name == "airbnb_listings_search":\n(?:.*\n)*?                    data = run_actor_sync\(ACTORS\["airbnb"\][^\n]*\n)', src)
    if not anchor:
        raise SystemExit("could not find the airbnb handler branch to anchor on")
    src = src[:anchor.end()] + "".join(handler_block) + src[anchor.end():]
    ast.parse(src)

    manifest = json.loads((ROOT / "manifest.json").read_text(encoding="utf-8"), object_pairs_hook=OrderedDict)
    have = {t["name"] for t in manifest.get("tools", [])}
    for s in specs:
        if s["tool"]["name"] not in have:
            manifest.setdefault("tools", []).append(OrderedDict([("name", s["tool"]["name"]),
                                                                   ("description", s["tool"]["description"].split("\n")[0][:300])]))
    old_ver = manifest.get("version")
    if dry:
        print(f"DRY RUN: would add {len(added)} tools: {added}; version {old_ver} -> {version}"); return 0

    src_path.write_text(src, encoding="utf-8")
    manifest["version"] = version
    manifest["long_description"] = (
        f"{len(manifest.get('tools', []))} read-only tools over public data sources, each backed by an Apify Actor. "
        "Runs execute on the caller's own Apify account and are billed to it. The server itself is "
        "standard-library Python with no third-party dependencies."
    )
    (ROOT / "manifest.json").write_text(json.dumps(manifest, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    for f, rx in (("setup.py", r'version="' + re.escape(old_ver) + '"'),
                  ("package.json", r'"version": "' + re.escape(old_ver) + '"'),
                  ("server.json", r'"version": "' + re.escape(old_ver) + '"')):
        p = ROOT / f; t = p.read_text(encoding="utf-8")
        p.write_text(re.sub(rx, lambda m: m.group(0).replace(old_ver, version), t), encoding="utf-8")
    sync_tool_count_claims(len(manifest.get("tools", [])))
    ast.parse(src_path.read_text(encoding="utf-8"))
    for f in ("package.json", "server.json", "manifest.json"):
        json.loads((ROOT / f).read_text(encoding="utf-8"))
    print(f"added {len(added)} tools: {added}")
    print(f"version {old_ver} -> {version} in setup.py, package.json, server.json, manifest.json")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
