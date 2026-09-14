#!/usr/bin/env bash
# Release apify-data-scrapers to every venue, with a read-back after each step.
#
#   1. build sdist + wheel                    (python -m build)
#   2. PyPI upload + JSON-API verify          (twine; PYPI_TOKEN from G:/apify-fleet/.env)
#   3. official MCP registry publish + verify (mcp-publisher; gh token, non-interactive)
#   4. Smithery bundle build + publish + verify (scripts/build_smithery_bundle.py; SMITHERY_API_KEY)
#
# Preconditions: version already bumped in setup.py/package.json/server.json/manifest.json
# (scripts/integrate_mcp_specs.py does this), tests green, changes committed.
# Order matters: the registry validates that the PyPI package/version exists (step 2 before 3).
# usage: bash scripts/release.sh <version>
set -u
V="${1:?version required, e.g. 1.0.8}"
REPO="G:/apify-scrapers"; ENV="G:/apify-fleet/.env"
MP="$REPO/bin/mcp-publisher.exe"   # from github.com/modelcontextprotocol/registry releases; bin/ is gitignored
PYPI="$(grep -oE '^PYPI_TOKEN=.*' "$ENV" | cut -d= -f2-)"; SM="$(grep -oE '^SMITHERY_API_KEY=.*' "$ENV" | cut -d= -f2-)"
mask() { sed -E "s/${PYPI}/<pypi>/g; s/${SM}/<smithery>/g; s/(gho_|ghp_|github_pat_)[A-Za-z0-9_]+/<gh>/g; s/[A-Za-z0-9_-]{40,}/<redacted>/g"; }
cd "$REPO" || exit 1
grep -q "version=\"$V\"" setup.py || { echo "ABORT: setup.py is not at $V"; exit 2; }

echo "=== 1. build $V ==="
rm -rf dist && python -m build --sdist --wheel -q 2>&1 | tail -1
ls dist/ | sed 's/^/   /'

echo; echo "=== 2. PyPI upload + verify ==="
TWINE_USERNAME=__token__ TWINE_PASSWORD="$PYPI" python -m twine upload --non-interactive dist/*"$V"* 2>&1 | mask | grep -E "View at|error|Error"
python - "$V" <<'PY'
import sys, time, httpx
v=sys.argv[1]
for _ in range(8):
    j=httpx.get("https://pypi.org/pypi/apify-data-scrapers/json",timeout=30).json()
    if v in j["releases"]: print(f"   PyPI: {v} live, latest={j['info']['version']}, files={[f['filename'] for f in j['releases'][v]]}"); break
    time.sleep(5)
else: print("   PyPI: NOT visible yet"); sys.exit(3)
PY
[ $? -eq 0 ] || exit 3

echo; echo "=== 3. MCP registry publish + verify ==="
"$MP" login github --token "$(gh auth token)" 2>&1 | mask | tail -1
"$MP" publish 2>&1 | mask | tail -2
python - "$V" <<'PY'
import sys, httpx
v=sys.argv[1]
j=httpx.get("https://registry.modelcontextprotocol.io/v0/servers",params={"search":"io.github.jlucasmcrell/apify-scrapers"},timeout=30).json()
rows=[(s.get("server",s).get("version"), (s.get("_meta") or {}).get("io.modelcontextprotocol.registry/official",{}).get("isLatest")) for s in j.get("servers",[])]
print("   registry versions:", rows); ok=any(r[0]==v and r[1] for r in rows); print("   latest is", v, ":", ok); sys.exit(0 if ok else 4)
PY
[ $? -eq 0 ] || exit 4

echo; echo "=== 4. Smithery bundle + publish + verify ==="
python scripts/build_smithery_bundle.py dist/apify-scrapers.mcpb | sed 's/^/   /'
SMITHERY_API_KEY="$SM" npx -y @smithery/cli mcp publish dist/apify-scrapers.mcpb -n jlucasmcrell/apify-scrapers --json 2>&1 | grep -vE '^npm (warn|notice)|Assertion failed' | mask | tail -2
TOOL_COUNT="$(python -c 'import json; print(len(json.load(open("manifest.json", encoding="utf-8"))["tools"]))')"
SMITHERY_API_KEY="$SM" python - "$TOOL_COUNT" <<'PY'
import os, sys, httpx
count = int(sys.argv[1])
description = (f"MCP server exposing {count} read-only Apify public-data tools: leads, news, SEO, "
               "CVEs, jobs, SEC filings, procurement, health, registries, and more.")
r = httpx.patch(
    "https://api.smithery.ai/servers/jlucasmcrell%2Fapify-scrapers",
    headers={"Authorization": f"Bearer {os.environ['SMITHERY_API_KEY']}"},
    json={"description": description}, timeout=30)
r.raise_for_status()
print(f"   Smithery description: {count} tools")
PY
curl -s "https://api.smithery.ai/servers/jlucasmcrell%2Fapify-scrapers" -H "Authorization: Bearer $SM" | mask | python -c "import sys,json
j=json.loads(sys.stdin.read()); t=j.get('tools') or []; c=(j.get('connections') or [{}])[0]
print('   Smithery tools:',len(t),'| connection:',c.get('type'),c.get('runtime'))"
echo; echo "=== done: $V on PyPI, MCP registry, Smithery ==="
