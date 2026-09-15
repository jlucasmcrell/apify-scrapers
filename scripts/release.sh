#!/usr/bin/env bash
# Release apify-data-scrapers to every venue, with a read-back after each step.
#
#   0. verify every MCP tool targets a public, agentic-eligible Actor
#   1. build sdist + wheel                    (python -m build)
#   2. PyPI upload + JSON-API verify          (twine; PYPI_TOKEN from G:/apify-fleet/.env)
#   3. official MCP registry publish + verify (mcp-publisher; gh token, non-interactive)
#   4. Smithery bundle build + publish + verify (scripts/build_smithery_bundle.py; SMITHERY_API_KEY)
#   5. GitHub release + artifact checksum verification
#
# Preconditions: version already bumped in setup.py/package.json/server.json/manifest.json
# (scripts/integrate_mcp_specs.py does this), tests green, changes committed.
# Order matters: the registry validates that the PyPI package/version exists (step 2 before 3).
# Requires release-only dependencies: build, twine, httpx, jsonschema.
# usage: bash scripts/release.sh <version>
set -euo pipefail
V="${1:?version required, e.g. 1.0.8}"
REPO="G:/apify-scrapers"; ENV="G:/apify-fleet/.env"
MP="$REPO/bin/mcp-publisher.exe"   # from github.com/modelcontextprotocol/registry releases; bin/ is gitignored
PYPI="$(grep -oE '^PYPI_TOKEN=.*' "$ENV" | cut -d= -f2-)"; SM="$(grep -oE '^SMITHERY_API_KEY=.*' "$ENV" | cut -d= -f2-)"
mask() { sed -E "s/${PYPI}/<pypi>/g; s/${SM}/<smithery>/g; s/(gho_|ghp_|github_pat_)[A-Za-z0-9_]+/<gh>/g; s/[A-Za-z0-9_-]{40,}/<redacted>/g"; }
cd "$REPO" || exit 1
grep -q "version=\"$V\"" setup.py || { echo "ABORT: setup.py is not at $V"; exit 2; }

echo "=== 0. public availability gate ==="
python scripts/audit_public_coverage.py --require-release-ready || exit 2

python -m unittest discover -s tests -q
python scripts/site/lint_pages.py
python scripts/audit_live_contracts.py --env-file "$ENV"

echo "=== 1. build $V ==="
python -m build --sdist --wheel -q --outdir "dist/$V"
ls dist/ | sed 's/^/   /'

echo; echo "=== 2. PyPI upload + verify ==="
TWINE_USERNAME=__token__ TWINE_PASSWORD="$PYPI" python -m twine upload --non-interactive "dist/$V/"* 2>&1 | mask | cat
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
r=httpx.get("https://registry.modelcontextprotocol.io/v0.1/servers/io.github.jlucasmcrell%2Fapify-scrapers/versions/latest",timeout=60)
r.raise_for_status()
j=r.json(); ok=j.get("server",{}).get("version")==v
print("   registry latest is", v, ":", ok); sys.exit(0 if ok else 4)
PY
[ $? -eq 0 ] || exit 4

echo; echo "=== 4. Smithery bundle + publish + verify ==="
python scripts/build_smithery_bundle.py dist/apify-scrapers.mcpb | sed 's/^/   /'
SMITHERY_API_KEY="$SM" npx -y @smithery/cli mcp publish dist/apify-scrapers.mcpb -n jlucasmcrell/apify-scrapers --json 2>&1 | mask | tail -2
TOOL_COUNT="$(python -c 'import json; print(len(json.load(open("manifest.json", encoding="utf-8"))["tools"]))')"
SMITHERY_API_KEY="$SM" python - "$TOOL_COUNT" <<'PY'
import os, sys, httpx
count = int(sys.argv[1])
description = (f"MCP server exposing {count} read-only Apify public-data tools: leads, news, SEO, "
               "jobs, SEC filings, procurement, health, registries, and more.")
r = httpx.patch(
    "https://api.smithery.ai/servers/jlucasmcrell%2Fapify-scrapers",
    headers={"Authorization": f"Bearer {os.environ['SMITHERY_API_KEY']}"},
    json={"description": description}, timeout=30)
r.raise_for_status()
print(f"   Smithery description: {count} tools")
PY
curl --fail --silent --show-error "https://api.smithery.ai/servers/jlucasmcrell%2Fapify-scrapers" -H "Authorization: Bearer $SM" | mask | python -c "import sys,json
j=json.loads(sys.stdin.read()); t=j.get('tools') or []; c=(j.get('connections') or [{}])[0]
print('   Smithery tools:',len(t),'| connection:',c.get('type'),c.get('runtime'))
sys.exit(0 if len(t)==int(sys.argv[1]) else 5)" "$TOOL_COUNT"
echo; echo "=== 5. GitHub release + verify ==="
GH_REPO="jlucasmcrell/apify-scrapers"
if ! gh release view "v$V" --repo "$GH_REPO" >/dev/null 2>&1; then
    gh release create "v$V" "dist/$V/"* dist/apify-scrapers.mcpb \
        --repo "$GH_REPO" --target "$(git rev-parse HEAD)" --latest \
        --title "v$V" --generate-notes
fi
python - "$V" "$GH_REPO" <<'PY'
import hashlib, json, subprocess, sys
from pathlib import Path
version, repo = sys.argv[1:]
release = json.loads(subprocess.check_output(
    ["gh", "api", f"repos/{repo}/releases/latest"], text=True))
if release["tag_name"] != f"v{version}":
    raise SystemExit("GitHub latest release does not match the package version")
assets = {a["name"]: a for a in release["assets"]}
paths = list(Path(f"dist/{version}").glob("*")) + [Path("dist/apify-scrapers.mcpb")]
for path in paths:
    expected = "sha256:" + hashlib.sha256(path.read_bytes()).hexdigest()
    if assets.get(path.name, {}).get("digest") != expected:
        raise SystemExit(f"GitHub artifact missing or checksum mismatch: {path.name}")
print(f"GitHub: v{version} latest; {len(paths)} artifact checksums verified")
PY

echo; echo "=== done: $V on PyPI, MCP registry, Smithery, GitHub ==="
