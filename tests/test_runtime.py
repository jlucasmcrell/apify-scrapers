"""Offline regression checks: no paid runs or real credentials required."""
import io
import json
import os
from pathlib import Path
import queue
import re
import subprocess
import sys
import threading
import unittest
import urllib.error
from unittest.mock import patch

import mcp_server as server

ROOT = Path(__file__).resolve().parents[1]


class RuntimeTests(unittest.TestCase):
    def setUp(self):
        server._context.run = None
        server._context.cancel = threading.Event()

    def call(self, name='google_maps_search', arguments=None):
        return server.handle_request({'jsonrpc': '2.0', 'id': 1, 'method': 'tools/call',
                                      'params': {'name': name, 'arguments': arguments}})['result']

    def test_catalogs_and_specs_match(self):
        catalog = json.loads((ROOT / 'mcp.json').read_text(encoding='utf-8'))
        self.assertEqual(catalog['tools'], server.TOOLS_DEFINITION)
        manifest = json.loads((ROOT / 'manifest.json').read_text(encoding='utf-8'))
        self.assertEqual([t['name'] for t in catalog['tools']], [t['name'] for t in manifest['tools']])
        plugin = json.loads((ROOT / 'lhm.plugin.json').read_text(encoding='utf-8'))
        self.assertEqual(plugin['tools'], catalog['tools'])
        for filename in ['manifest.json', 'lhm.plugin.json', 'package.json', 'server.json']:
            metadata = json.loads((ROOT / filename).read_text(encoding='utf-8'))
            self.assertEqual(metadata['version'], catalog['version'])
        public = {t['name']: t for t in catalog['tools']}
        self.assertEqual(len(public), len(catalog['tools']))
        for path in (ROOT / 'specs').glob('*.json'):
            spec = json.loads(path.read_text(encoding='utf-8-sig'))
            if isinstance(spec, dict) and spec.get('tool', {}).get('name') in public:
                self.assertEqual(spec['tool'], public[spec['tool']['name']], str(path))

    def test_profiles_cover_catalog_once_and_filter_every_surface(self):
        grouped = [name for names in server.TOOL_PROFILES.values() for name in names]
        self.assertEqual(len(grouped), len(set(grouped)))
        self.assertEqual(set(grouped), {t['name'] for t in server.TOOLS_DEFINITION})
        program = '''
import json, mcp_server as s
def request(method, **params):
    return s.handle_request({'id': 1, 'method': method, 'params': params})
def forbidden(*args, **kwargs):
    raise AssertionError('A disabled tool must never reach the Actor runner')
s.run_actor_sync = forbidden
tools = request('tools/list')['result']['tools']
names = {t['name'] for t in tools}
expected = {t['name'] for t in s.TOOLS_DEFINITION} if s.ACTIVE_PROFILE == 'all' else set(s.TOOL_PROFILES[s.ACTIVE_PROFILE])
assert names == expected
catalog = json.loads(request('resources/read', uri='apify://actors/catalog')['result']['contents'][0]['text'])
assert len(catalog['actors']) == len(names)
assert str(len(names)) + ' tools' in request('initialize')['result']['instructions']
for tool in s.TOOLS_DEFINITION:
    if tool['name'] not in names:
        result = request('tools/call', name=tool['name'], arguments={})['result']
        assert result['structuredContent']['error']['code'] == 'UNKNOWN_TOOL'
for prompt in s.PROMPTS_DEFINITION:
    listed = {p['name'] for p in request('prompts/list')['result']['prompts']}
    if prompt['name'] not in listed:
        assert request('prompts/get', name=prompt['name'])['error']['code'] == -32602
if s.ACTIVE_PROFILE != 'all':
    assert all('Named alternatives:' not in t['description'] for t in tools)
print(len(names))
'''
        for profile in ['all', *server.TOOL_PROFILES]:
            with self.subTest(profile=profile):
                result = subprocess.run([sys.executable, '-c', program], cwd=ROOT,
                    env={**os.environ, 'APIFY_TOOL_PROFILE': profile}, capture_output=True, text=True)
                self.assertEqual(result.returncode, 0, result.stderr)
        result = subprocess.run([sys.executable, '-c', 'import mcp_server'], cwd=ROOT,
            env={**os.environ, 'APIFY_TOOL_PROFILE': 'typo'}, capture_output=True, text=True)
        self.assertNotEqual(result.returncode, 0)
        self.assertEqual(result.stdout, '')

    def test_invalid_inputs_never_start_a_run(self):
        cases = [None, [], {}, {'search_query': ''}, {'search_query': 'dentists', 'max_results': -1},
                 {'search_query': 'dentists', 'max_results': True},
                 {'search_query': 'dentists', 'max_results': 101},
                 {'search_query': 'dentists', 'unknown': 'not accepted'}]
        with patch.object(server, 'run_actor_sync') as run:
            for args in cases:
                with self.subTest(args=args):
                    result = self.call(arguments=args)
                    self.assertTrue(result['isError'])
                    self.assertEqual(result['structuredContent']['error']['code'], 'INVALID_INPUT')
            run.assert_not_called()

    def test_named_alternatives_are_public_tools(self):
        public = {tool['name'] for tool in server.TOOLS_DEFINITION}
        for tool in server.TOOLS_DEFINITION:
            alternatives = tool['description'].split('- Named alternatives:')[-1]
            for name in re.findall(r"'([a-z]+(?:_[a-z0-9]+)+)'", alternatives):
                self.assertIn(name, public, (tool['name'], name))

    def test_epa_description_does_not_offer_unavailable_filters(self):
        tool = next(t for t in server.TOOLS_DEFINITION if t['name'] == 'epa_facility_search')
        self.assertNotIn('city', tool['inputSchema']['properties'])
        self.assertNotIn('ZIP', tool['description'].split('.')[0])
        self.assertIn('not this MCP tool', tool['description'])

    def test_empty_results_are_explicitly_unverified(self):
        with patch.object(server, 'run_actor_sync', return_value=[]):
            result = self.call(arguments={'search_query': 'dentists'})
        self.assertFalse(result['isError'])
        self.assertEqual(result['structuredContent'], {'results': [], 'status': 'empty_unverified'})
        self.assertEqual(json.loads(result['content'][0]['text']), result['structuredContent'])

    def test_output_drift_is_a_tool_error(self):
        with patch.object(server, 'run_actor_sync', return_value=[{'name': 123}]):
            result = self.call(arguments={'search_query': 'dentists'})
        self.assertTrue(result['isError'])
        self.assertEqual(result['structuredContent']['error']['code'], 'OUTPUT_SCHEMA_MISMATCH')

    def test_unexpected_exception_is_redacted(self):
        with patch.object(server, 'run_actor_sync', side_effect=RuntimeError('SECRET_VALUE')):
            result = self.call(arguments={'search_query': 'dentists'})
        self.assertNotIn('SECRET_VALUE', json.dumps(result))
        self.assertEqual(result['structuredContent']['error']['code'], 'INTERNAL_ERROR')

    def test_missing_news_query_and_invalid_twitch_slug_rejected(self):
        with patch.object(server, 'run_actor_sync') as run:
            for name, args in [('google_news_search', {}), ('twitch_live_streams', {'game_name': ''})]:
                self.assertTrue(self.call(name, args)['isError'])
            run.assert_not_called()

    def test_twitch_default_is_valid(self):
        with patch.object(server, 'run_actor_sync', return_value=[]) as run:
            self.assertFalse(self.call('twitch_live_streams', {})['isError'])
        self.assertEqual(run.call_args.args[1]['search_query'], 'minecraft')

    def test_api_authorization_never_in_url_and_error_body_redacted(self):
        captured = []
        def fail(request, **kwargs):
            captured.append(request)
            raise urllib.error.HTTPError(request.full_url, 403, 'denied SECRET_VALUE', {}, io.BytesIO(b'SECRET_VALUE'))
        with patch.dict(os.environ, {'APIFY_TOKEN': 'SECRET_VALUE'}), patch.object(server.urllib.request, 'urlopen', side_effect=fail):
            with self.assertRaises(server.ToolFailure) as error:
                server._api('GET', '/actor-runs/test')
        self.assertEqual(error.exception.code, 'ACCESS_DENIED')
        self.assertNotIn('SECRET_VALUE', str(error.exception))
        self.assertNotIn('SECRET_VALUE', captured[0].full_url)
        self.assertEqual(captured[0].get_header('Authorization'), 'Bearer SECRET_VALUE')

    def test_run_started_once_with_cap_and_bounded_dataset(self):
        responses = [{'id': 'run1', 'status': 'SUCCEEDED', 'defaultDatasetId': 'data1'}, [{'name': 'A'}]]
        with patch.object(server, '_api', side_effect=responses) as api, patch.dict(os.environ, {'APIFY_MAX_CHARGE_USD': '0.25'}):
            self.assertEqual(server.run_actor_sync('owner/actor', {'max_items': 3}), [{'name': 'A'}])
        self.assertEqual(api.call_count, 2)
        self.assertIn('maxTotalChargeUsd=0.25', api.call_args_list[0].args[1])
        self.assertIn('limit=3', api.call_args_list[1].args[1])
        self.assertEqual(server._context.run['id'], 'run1')

    def test_ambiguous_start_not_retried(self):
        with patch.object(server, '_api', side_effect=server.ToolFailure('TIMEOUT', 'timeout')) as api:
            with self.assertRaises(server.ToolFailure):
                server.run_actor_sync('owner/actor', {})
        self.assertEqual(api.call_count, 1)

    def test_cancellation_aborts_recorded_run(self):
        def api(method, path, *args, **kwargs):
            if '/abort' in path:
                return {'status': 'ABORTED'}
            server._context.cancel.set()
            return {'id': 'run1', 'status': 'RUNNING'}
        with patch.object(server, '_api', side_effect=api) as mocked:
            with self.assertRaises(server.ToolFailure) as error:
                server.run_actor_sync('owner/actor', {})
        self.assertEqual(error.exception.code, 'CANCELLED')
        self.assertEqual(server._context.run['status'], 'ABORTED')
        self.assertEqual(mocked.call_count, 2)

    def test_terminal_source_block_is_deterministic(self):
        with patch.object(server, '_api', return_value={'id': 'run1', 'status': 'FAILED', 'statusMessage': 'SOURCE_BLOCKED captcha'}):
            with self.assertRaises(server.ToolFailure) as error:
                server.run_actor_sync('owner/actor', {})
        self.assertEqual(error.exception.code, 'SOURCE_BLOCKED')

    def test_protocol_remains_responsive_and_cancels(self):
        # A deliberately blocked local stand-in exercises transport, not an Actor.
        program = ('import mcp_server as s\n'
                   'def blocked(*args, **kwargs):\n'
                   ' s._context.cancel.wait(10)\n'
                   ' raise s.ToolFailure("CANCELLED", "cancelled")\n'
                   's.run_actor_sync=blocked\ns.serve_stdio()\n')
        process = subprocess.Popen([sys.executable, '-u', '-c', program], cwd=ROOT,
                                   stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                                   text=True, encoding='utf-8')
        messages = queue.Queue()
        def read():
            for line in process.stdout:
                messages.put(json.loads(line))
        threading.Thread(target=read, daemon=True).start()
        def send(obj):
            process.stdin.write(json.dumps({'jsonrpc': '2.0', **obj}) + '\n')
            process.stdin.flush()
        try:
            send({'id': 1, 'method': 'tools/call', 'params': {'name': 'google_maps_search', 'arguments': {'search_query': 'dentists'}}})
            send({'id': 2, 'method': 'ping'})
            self.assertEqual(messages.get(timeout=3)['id'], 2)
            send({'method': 'notifications/cancelled', 'params': {'requestId': 1}})
            result = messages.get(timeout=3)
            self.assertEqual(result['id'], 1)
            self.assertEqual(result['result']['structuredContent']['error']['code'], 'CANCELLED')
        finally:
            process.stdin.close()
            try:
                process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                process.kill(); process.wait()
            process.stdout.close(); process.stderr.close()

    def test_windows_transport_accepts_and_returns_utf8(self):
        program = ('import mcp_server as s\n'
                   'def failed(*args, **kwargs):\n'
                   ' raise s.ToolFailure("TEST", "Unicode: \\U0001f9b7 \\u4e2d")\n'
                   's.run_actor_sync=failed\ns.serve_stdio()\n')
        request = {'jsonrpc': '2.0', 'id': 1, 'method': 'tools/call', 'params': {'name': 'google_maps_search', 'arguments': {'search_query': 'Dentistes Montr\u00e9al'}}}
        process = subprocess.run([sys.executable, '-u', '-c', program], cwd=ROOT,
                                 input=(json.dumps(request, ensure_ascii=False) + '\n').encode('utf-8'),
                                 capture_output=True, timeout=10, env={**os.environ, 'PYTHONIOENCODING': 'cp1252'})
        response = json.loads(process.stdout.decode('utf-8'))
        self.assertEqual(response['result']['structuredContent']['error']['message'], 'Unicode: \U0001f9b7 \u4e2d')


if __name__ == '__main__':
    unittest.main()
