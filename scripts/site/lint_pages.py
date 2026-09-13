"""Deterministic lint for the five use-case pages against tools_digest.json.

Checks front matter, tool names, argument names in "-> tool(arg=...)" examples,
prices, Store links, cross-links, the verbatim install section, and banned
phrases. Exit 1 on any problem so it can gate the commit.
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

S = Path(__file__).resolve().parent
PAGES = Path(__file__).resolve().parents[2] / "mcp"
SLUGS = ["sec-edgar", "google-maps", "public-records", "job-search", "government-data"]
digest = {d["tool"]: d for d in json.loads((S / "tools_digest.json").read_text(encoding="utf-8"))}
install = re.sub(r"\s+", " ", (S / "install_snippet.md").read_text(encoding="utf-8")).strip()

problems: list[str] = []


def check(slug: str) -> None:
    p = PAGES / f"{slug}.md"
    if not p.is_file():
        problems.append(f"{slug}: file missing"); return
    text = p.read_text(encoding="utf-8")
    m = re.match(r"---\n(.*?)\n---\n", text, re.S)
    if not m:
        problems.append(f"{slug}: no front matter"); return
    fm = dict(re.findall(r"^(\w+):\s*(.*)$", m.group(1), re.M))
    if fm.get("layout") != "default":
        problems.append(f"{slug}: layout={fm.get('layout')!r}")
    if fm.get("permalink") != f"/mcp/{slug}/":
        problems.append(f"{slug}: permalink={fm.get('permalink')!r}")
    desc = fm.get("description", "").strip().strip('"')
    if not 120 <= len(desc) <= 170:
        problems.append(f"{slug}: description length {len(desc)}")
    body = text[m.end():]
    h1 = re.search(r"^# (.+)$", body, re.M)
    if not h1 or h1.group(1).strip() != fm.get("title", "").strip().strip('"'):
        problems.append(f"{slug}: H1 != title")
    # tool names: every snake_case token that looks like a tool must exist
    for name in set(re.findall(r"\b([a-z]+(?:_[a-z]+){1,4})\b", body)):
        if name.endswith(("_search", "_filings", "_contracts", "_streams", "_detector", "_geocoder")) and name not in digest:
            problems.append(f"{slug}: unknown tool name {name}")
    # examples: -> tool(arg=..., arg=...)
    for tool, args in re.findall(r"->\s*`?(\w+)`?\((.*?)\)", body):
        if tool not in digest:
            problems.append(f"{slug}: example uses unknown tool {tool}"); continue
        for arg in re.findall(r"(\w+)\s*=", args):
            if arg not in digest[tool]["args"]:
                problems.append(f"{slug}: example {tool}({arg}=) - arg not in schema")
    # prices and store links per section
    for tool, section in re.findall(r"^### (\w+)[^\n]*\n(.*?)(?=^### |^## |\Z)", body, re.M | re.S):
        if tool not in digest:
            problems.append(f"{slug}: section for unknown tool {tool}"); continue
        d = digest[tool]
        pr = re.search(r"\$([0-9.]+) per result plus \$([0-9.]+) Actor-start", section)
        if not pr:
            problems.append(f"{slug}: {tool} price line missing")
        elif float(pr.group(1)) != float(d["pricing"]["per_result_usd"]) or float(pr.group(2)) != float(d["pricing"]["per_start_usd"]):
            problems.append(f"{slug}: {tool} price {pr.groups()} != digest ({d['pricing']['per_result_usd']}, {d['pricing']['per_start_usd']})")
        if d["pricing"]["store_url"] not in section:
            problems.append(f"{slug}: {tool} store url missing")
        ret = re.search(r"Returns:\**\s*(.+)", section)
        if ret:
            # output fields are camelCase on the six hand-written tools (jobUrl, accessionNumber)
            for f in re.findall(r"`?([A-Za-z_][A-Za-z0-9_]*)`?", ret.group(1)):
                if f and f not in d["output_fields"] and f not in ("and", "or", "Returns"):
                    problems.append(f"{slug}: {tool} Returns field {f} not in output schema")
    # install section verbatim (whitespace-insensitive)
    if install not in re.sub(r"\s+", " ", body):
        problems.append(f"{slug}: install section not verbatim")
    # cross-links
    for other in SLUGS:
        if other != slug and f"/mcp/{other}/" not in body:
            problems.append(f"{slug}: missing link to /mcp/{other}/")
    for bad in ("30+", " best ", "most powerful", "\u2014"):
        if bad in body:
            problems.append(f"{slug}: banned text {bad!r}")
    words = len(re.sub(r"\s+", " ", body.split("## Install the MCP server")[0]).split())
    print(f"{slug:16} words~{words:4}  sections={len(re.findall(r'^### ', body, re.M))}")


for s in SLUGS:
    check(s)
if problems:
    print("\nPROBLEMS:")
    for x in problems:
        print(" -", x)
    sys.exit(1)
print("\nall pages pass lint")
