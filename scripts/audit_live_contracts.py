"""Read-only schema and saved-output audit. This never starts an Actor run."""
import argparse
import json
import os
from pathlib import Path
import sys
from unittest.mock import patch
import urllib.request

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
import mcp_server as server
from e2e_tools import CASES
from jsonschema import Draft7Validator


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--env-file', type=Path)
    args = parser.parse_args()
    if args.env_file:
        for line in args.env_file.read_text(encoding='utf-8-sig').splitlines():
            if line.startswith('APIFY_TOKEN='):
                os.environ.setdefault('APIFY_TOKEN', line.split('=', 1)[1].strip().strip('\"\''))
    token = os.environ.get('APIFY_TOKEN')
    if not token:
        parser.error('APIFY_TOKEN is required')
    def get(path):
        request = urllib.request.Request('https://api.apify.com/v2' + path,
                                         headers={'Authorization': 'Bearer ' + token})
        with urllib.request.urlopen(request, timeout=30) as response:
            value = json.load(response)
        return value.get('data', value) if isinstance(value, dict) else value
    failures = []
    for tool in server.TOOLS_DEFINITION:
        name = tool['name']
        try:
            example = CASES[name][0]
            server._context.run = None
            with patch.object(server, 'run_actor_sync', return_value=[]) as run:
                response = server.handle_request({'id': 1, 'method': 'tools/call', 'params': {'name': name, 'arguments': example}})
            if response['result']['isError'] or not run.called:
                raise ValueError('example rejected by MCP validation')
            actor, payload = run.call_args.args
            detail = get('/acts/' + actor.replace('/', '~'))
            if not detail.get('isPublic'):
                raise ValueError('advertised Actor is private')
            build = get('/actor-builds/' + detail['taggedBuilds']['latest']['buildId'])
            schema = build.get('inputSchema') or build['actorDefinition']['input']
            if isinstance(schema, str): schema = json.loads(schema)
            errors = list(Draft7Validator(schema).iter_errors(payload))
            if errors:
                raise ValueError('Actor input mismatch at ' + str(list(errors[0].absolute_path)))
            runs = get('/acts/' + actor.replace('/', '~') + '/runs?status=SUCCEEDED&desc=1&limit=5')['items']
            checked = 0
            for previous in runs:
                if not previous.get('defaultDatasetId'): continue
                rows = get('/datasets/' + previous['defaultDatasetId'] + '/items?limit=3')
                if not rows: continue
                value = {'results': rows, 'status': 'success'}
                errors = list(Draft7Validator(tool['outputSchema']).iter_errors(value))
                if errors:
                    error = errors[0]
                    raise ValueError('saved output mismatch at ' + str(list(error.absolute_path)) + ' validator=' + error.validator)
                server.validate_value(value, tool['outputSchema'])
                checked += len(rows)
                break
            if not checked:
                raise ValueError('no saved nonempty output available for verification')
            print('PASS', name, 'input +', checked, 'saved rows', flush=True)
        except Exception as error:
            # Do not echo bodies or validation values (datasets can hold personal data).
            reason = str(error) if isinstance(error, ValueError) else type(error).__name__
            print('FAIL', name, reason, flush=True)
            failures.append(name)
    print(f'{len(server.TOOLS_DEFINITION)-len(failures)}/{len(server.TOOLS_DEFINITION)} contracts verified; no new runs started')
    return 1 if failures else 0


if __name__ == '__main__':
    raise SystemExit(main())
