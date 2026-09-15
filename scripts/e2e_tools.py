"""End-to-end test of every MCP tool through the server's real stdio JSON-RPC path.

Spawns `python mcp_server.py`, sends initialize + tools/list, then tools/call for
each tool with a known-good example input, and checks three things a unit test
cannot: the server answers over its actual transport, the Actor run succeeds
and returns rows, and a token from the input appears in the output - i.e. the
tool ran on the input it was given, not on defaults. The five broken tools of
2026-09-13 would have failed the first check with an HTTP 400 in the error.

Framing: one JSON object per line on stdin/stdout (see serve_stdio()).
Requires APIFY_TOKEN in the environment (runs bill the caller's account).
usage: python scripts/e2e_tools.py [tool_name ...]   (default: all tools)
"""
from __future__ import annotations

import json
import os
import subprocess
import sys
import time
import queue
import threading
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from mcp_server import validate_value

# tool -> (arguments, lowercase token expected somewhere in the result JSON)
CASES: dict[str, tuple[dict, str]] = {
    "google_maps_search": ({"search_query": "dentists", "location": "Miami, FL", "max_results": 3}, "miami"),
    "glassdoor_jobs_search": ({"job_title": "nurse", "location": "Denver, CO", "max_results": 3}, "denver"),
    "sec_edgar_filings": ({"ticker": "MSFT", "form_type": "10-K", "max_results": 3}, "microsoft"),
    "usaspending_contracts": ({"recipient_name": "shipbuilding", "max_results": 3}, "ship"),
    "twitch_live_streams": ({"game_name": "minecraft", "max_results": 3}, "minecraft"),
    "airbnb_listings_search": ({"location": "Denver, Colorado", "max_results": 3}, "denver"),
    "alabama_business_search": ({"search_query": "SMITH", "max_results": 3}, "smith"),
    "california_contractor_license_search": ({"search_query": "SMITH", "max_results": 3}, "smith"),
    "florida_new_filings_search": ({"search_query": "SMITH", "max_results": 3}, "smith"),
    "florida_officer_search": ({"search_query": "SMITH", "max_results": 3}, "smith"),
    "us_business_entity_search": ({"search_query": "SMITH", "states": ["alabama"], "max_results": 3}, "smith"),
    "us_contractor_license_search": ({"search_query": "SMITH", "states": ["california"], "max_results": 3}, "smith"),
    "clinical_trials_search": ({"condition": "Alzheimer", "max_results": 3}, "alzheimer"),
    "epa_facility_search": ({"state": "RI", "max_results": 3}, "ri"),
    "fec_campaign_finance_search": ({"state": "CA", "party": "DEM", "office": "House", "max_results": 3}, "ca"),
    "french_company_search": ({"search_query": "BOULANGERIE", "max_results": 3}, "boulangerie"),
    "openfda_search": ({"search_query": "SEMAGLUTIDE", "max_results": 3}, "semaglutide"),
    "google_play_reviews_search": ({"app_ids": ["com.spotify.music"], "max_results": 3}, "spotify"),
    "linkedin_jobs_search": ({"search_query": "paralegal", "location": "Seattle, Washington", "max_results": 3}, "seattle"),
    "youtube_video_search": ({"search_query": "sourdough starter", "max_results": 3}, "sourdough"),
}


def _load_spec_cases() -> None:
    """Prefer each generated tool's live-verified example_call + token from its spec.

    The specs (scratchpad/mcp_specs/*.json) were produced by agents that ran
    every example against the Actor and recorded the token found in the output.
    Hand-typed argument names for those tools are a second source of truth and
    were wrong at least once; the spec is the one that was actually exercised.
    """
    spec_dir = ROOT / "specs"
    if not spec_dir.is_dir():
        return
    for p in spec_dir.glob("*.json"):
        try:
            s = json.loads(p.read_text(encoding="utf-8"))
        except Exception:
            continue
        if not ("tool" in s and "example_call" in s):
            continue
        tok = (s.get("verification") or {}).get("token") or ""
        tok = tok.split("/")[0].split(" ")[0].lower()   # "CA/DEM/House" -> "ca"
        if tok:
            CASES[s["tool"]["name"]] = (s["example_call"], tok)


_load_spec_cases()


class Server:
    def __init__(self):
        if not os.environ.get("APIFY_TOKEN"):
            raise SystemExit("APIFY_TOKEN not set")
        self.p = subprocess.Popen([sys.executable, str(ROOT / "mcp_server.py")], cwd=str(ROOT),
                                  stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL,
                                  text=True, encoding="utf-8", bufsize=1)
        self.n = 0
        self.responses = queue.Queue()
        def read():
            try:
                for line in self.p.stdout:
                    self.responses.put(line)
            finally:
                self.responses.put(None)
        threading.Thread(target=read, daemon=True).start()

    def call(self, method: str, params: dict | None = None, timeout: int = 200) -> dict:
        self.n += 1
        req = {"jsonrpc": "2.0", "id": self.n, "method": method, "params": params or {}}
        self.p.stdin.write(json.dumps(req) + "\n"); self.p.stdin.flush()
        deadline = time.monotonic() + timeout
        while time.monotonic() < deadline:
            try:
                line = self.responses.get(timeout=max(.01, deadline - time.monotonic()))
            except queue.Empty:
                break
            if not line:
                raise RuntimeError("server closed stdout")
            try:
                msg = json.loads(line)
            except json.JSONDecodeError:
                continue
            if msg.get("id") == self.n:
                return msg
        self.p.stdin.write(json.dumps({'jsonrpc': '2.0', 'method': 'notifications/cancelled', 'params': {'requestId': self.n}}) + '\n')
        self.p.stdin.flush()
        raise TimeoutError(f"{method} timed out after {timeout}s; cancellation requested")

    def close(self):
        try:
            self.p.stdin.close()
            self.p.wait(timeout=35)
        except subprocess.TimeoutExpired:
            self.p.kill(); self.p.wait()
        except Exception:
            pass
        finally:
            self.p.stdout.close()


def main() -> int:
    only = sys.argv[1:]
    srv = Server()
    try:
        init = srv.call("initialize", {"protocolVersion": "2024-11-05", "capabilities": {}, "clientInfo": {"name": "e2e", "version": "1"}})
        assert "result" in init, f"initialize failed: {init}"
        listed = srv.call("tools/list")
        names = [t["name"] for t in listed["result"]["tools"]]
        print(f"tools/list -> {len(names)} tools")
        definitions = {t['name']: t for t in listed['result']['tools']}
        missing = [n for n in names if n not in CASES] + [n for n in only if n not in names]
        if missing:
            print("Missing test case or unavailable requested tool:", missing)
        results = []
        for name, (args, token) in CASES.items():
            if name not in names:
                continue
            if only and name not in only:
                continue
            t0 = time.time()
            try:
                resp = srv.call("tools/call", {"name": name, "arguments": args}, timeout=240)
            except Exception as exc:
                results.append((name, "ERROR", f"{type(exc).__name__}: {str(exc)[:120]}")); print(f"ERR  {name}: {exc}"); continue
            secs = round(time.time() - t0, 1)
            if "error" in resp:
                results.append((name, "FAIL", f"rpc error: {json.dumps(resp['error'])[:160]}")); print(f"FAIL {name} ({secs}s): {json.dumps(resp['error'])[:160]}"); continue
            res = resp.get("result") or {}
            structured = res.get('structuredContent')
            schema_error = None
            try:
                validate_value(structured, definitions[name]['outputSchema'], code='OUTPUT_SCHEMA_MISMATCH')
                assert json.loads(res['content'][0]['text']) == structured
            except Exception as exc:
                schema_error = type(exc).__name__
            blob = json.dumps((structured or {}).get('results', [])).lower()
            # A two-letter token ("ri", "ca") is a substring of almost any JSON;
            # require a whole-word match for short tokens so the relevance check
            # cannot pass on noise.
            import re as _re
            token_ok = (_re.search(r"\b" + _re.escape(token) + r"\b", blob) is not None) if len(token) < 4 else (token in blob)
            is_err = bool(res.get("isError"))
            content = res.get("content") or []
            rows = None
            for c in content:
                if c.get("type") == "text":
                    try:
                        parsed = json.loads(c["text"]); rows = parsed.get("results") if isinstance(parsed, dict) else parsed
                    except Exception:
                        pass
            n = len(rows) if isinstance(rows, list) else None
            ok = not schema_error and (not is_err) and (n or 0) > 0 and token_ok
            why = "" if ok else ("schema/structured-content mismatch" if schema_error else "isError" if is_err else "no rows" if not n else f"token {token!r} absent")
            results.append((name, "OK" if ok else "FAIL", f"{n} rows {secs}s {why}"))
            print(f"{'OK  ' if ok else 'FAIL'} {name:38} rows={n} {secs}s {why}")
        good = sum(1 for r in results if r[1] == "OK")
        print(f"\n{good}/{len(results)} tools passed end-to-end")
        return 0 if good == len(results) and not missing else 1
    finally:
        srv.close()


if __name__ == "__main__":
    raise SystemExit(main())
