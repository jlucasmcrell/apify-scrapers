"""Build the MCPB bundle Smithery needs for a stdio release - reproducibly.

Why this exists instead of `mcpb pack`:
  Smithery's CLI passes the bundle manifest's `tools` straight into the release's
  serverCard, and the server validates each tool against the MCP Tool schema,
  which REQUIRES `inputSchema`. Publishing with name/description-only tools fails
  ("Invalid input: expected object, received undefined" x6). But the MCPB 0.3
  validator that `mcpb pack` runs REJECTS `inputSchema` on manifest tools
  ("Unrecognized key(s)"), so it refuses to pack an enriched manifest. And
  omitting `tools` publishes fine but leaves the listing with ZERO tools -
  Smithery does not introspect a stdio bundle (it cannot run a Python server
  that needs the caller's Apify token). Measured 2026-09-13.

So: keep the committed manifest.json MCPB-valid (name/description tools), and at
build time enrich a COPY with each tool's inputSchema/annotations lifted from
TOOLS_DEFINITION in mcp_server.py, then zip it with manifest.json at the archive
root (the only structural requirement Smithery's CLI checks).

usage:  python scripts/build_smithery_bundle.py [out.mcpb]
then:   npx -y @smithery/cli mcp publish out.mcpb -n jlucasmcrell/apify-scrapers
        (SMITHERY_API_KEY in env; no --config-schema for bundles - the schema
        comes from manifest.json user_config)
"""
from __future__ import annotations

import ast
import json
import re
import sys
import zipfile
from collections import OrderedDict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
FILES = ("mcp_server.py", "requirements.txt", "LICENSE", "README.md")


def tools_from_server() -> dict[str, dict]:
    src = (ROOT / "mcp_server.py").read_text(encoding="utf-8")
    block = re.search(r"TOOLS_DEFINITION = (\[.*?\n\])\n", src, re.S).group(1)
    return {t["name"]: t for t in ast.literal_eval(block)}


def main() -> int:
    out = Path(sys.argv[1]) if len(sys.argv) > 1 else ROOT / "dist" / "apify-scrapers.mcpb"
    out.parent.mkdir(parents=True, exist_ok=True)
    manifest = json.loads((ROOT / "manifest.json").read_text(encoding="utf-8"), object_pairs_hook=OrderedDict)
    defs = tools_from_server()
    missing = [t["name"] for t in manifest.get("tools", []) if t["name"] not in defs]
    if missing:
        raise SystemExit(f"manifest tools not defined in mcp_server.py TOOLS_DEFINITION: {missing}")
    for t in manifest.get("tools", []):
        d = defs[t["name"]]
        t["inputSchema"] = d["inputSchema"]
        if d.get("annotations"):
            t["annotations"] = d["annotations"]
    if out.exists():
        out.unlink()
    with zipfile.ZipFile(out, "w", zipfile.ZIP_DEFLATED) as z:
        z.writestr("manifest.json", json.dumps(manifest, indent=2, ensure_ascii=False) + "\n")
        for f in FILES:
            z.write(ROOT / f, f)
    with zipfile.ZipFile(out) as z:
        m = json.loads(z.read("manifest.json"))
        n = sum("inputSchema" in t for t in m.get("tools", []))
        print(f"{out}  files={len(z.namelist())}  tools with inputSchema={n}/{len(m.get('tools', []))}  version={m.get('version')}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
