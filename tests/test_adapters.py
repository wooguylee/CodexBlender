import base64
import importlib.util
import io
import json
from pathlib import Path
import subprocess
import tempfile
import unittest
from unittest.mock import patch
from urllib.error import HTTPError, URLError

from router.config import load_config


class AdapterTests(unittest.TestCase):
    def setUp(self):
        from llm import client
        self.assertTrue(hasattr(client, 'ResponsesClient'), 'Responses client is not implemented')
        self.assertIsNotNone(importlib.util.find_spec('adapters'), 'Blender adapter is not implemented')
        from adapters.blender import BlenderTools
        self.Client, self.Error, self.Tools = client.ResponsesClient, client.ModelCallError, BlenderTools
        self.config = load_config()

    def client(self):
        return self.Client(self.config, api_key='test-secret-key')

    def request(self, client):
        return client.complete(model='configured-id', effort='high', history=[{'role': 'user', 'content': '작업'}],
                               tools=[], instructions='scoped task')

    def test_responses_payload_and_usage(self):
        seen = []
        def receive(request, timeout):
            seen.append((request, timeout))
            return io.BytesIO(json.dumps({'status': 'completed', 'output': [], 'usage': {'input_tokens': 3}}).encode())
        with patch('llm.client.urlopen', side_effect=receive):
            result = self.request(self.client())
        body = json.loads(seen[0][0].data)
        self.assertEqual(seen[0][0].full_url, 'https://api.openai.com/v1/responses')
        self.assertEqual(body['model'], 'configured-id')
        self.assertEqual(body['reasoning'], {'effort': 'high'})
        self.assertEqual(body['input'][0]['content'], '작업')
        self.assertFalse(body['parallel_tool_calls'])
        self.assertFalse(body['store'])
        self.assertNotIn('temperature', body)
        self.assertEqual(result['usage']['input_tokens'], 3)

    def test_unsupported_effort_is_omitted(self):
        seen = []
        def receive(request, timeout):
            seen.append(json.loads(request.data))
            return io.BytesIO(b'{"status":"completed","output":[]}')
        with patch('llm.client.urlopen', side_effect=receive):
            self.client().complete(model='custom', effort=None, history=[], tools=[], instructions='')
        self.assertNotIn('reasoning', seen[0])

    def test_http_failures_classified_without_leaking_response_body(self):
        for status, code, expected in [(401, 'invalid_api_key', 'fatal'), (404, 'model_not_found', 'unavailable'),
                                       (400, 'model_not_found', 'unavailable'), (429, 'rate_limit_exceeded', 'transient'),
                                       (429, 'insufficient_quota', 'fatal'), (503, 'server_error', 'transient'),
                                       (400, 'invalid_request_error', 'fatal')]:
            body = json.dumps({'error': {'code': code, 'message': 'test-secret-key'}}).encode()
            error = HTTPError('https://api.openai.com', status, 'error', {}, io.BytesIO(body))
            with self.subTest(status=status, code=code), patch('llm.client.urlopen', side_effect=error):
                with self.assertRaises(self.Error) as caught:
                    self.request(self.client())
                self.assertEqual(caught.exception.kind, expected)
                self.assertNotIn('test-secret-key', str(caught.exception))

    def test_missing_key_invalid_endpoint_and_malformed_response(self):
        with patch.dict('os.environ', {}, clear=True), self.assertRaises(self.Error):
            self.Client(self.config)
        for endpoint in ('http://example.com/v1', 'https://user:password@example.com/v1'):
            self.config['api']['base_url'] = endpoint
            with self.assertRaises(ValueError):
                self.client()
        self.config = load_config()
        with patch('llm.client.urlopen', return_value=io.BytesIO(b'not JSON')):
            with self.assertRaises(self.Error):
                self.request(self.client())

    def test_tool_script_saved_then_existing_cli_called(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            tools = self.Tools(root, self.config)
            captured = []
            def run(command, **kwargs):
                captured.append(command)
                return subprocess.CompletedProcess(command, 0, '{"ok":true}', '')
            with patch('adapters.blender.subprocess.run', side_effect=run):
                result = tools.execute('run', {'code': "bpy.data.objects['Cube'].location.x = 2", 'label': '이동'}, 'task1')
            self.assertTrue(result['ok'])
            source = list((root / 'workflows/model-routing/task1').glob('*.py'))
            self.assertEqual(len(source), 1)
            self.assertIn('location.x = 2', source[0].read_text(encoding='utf-8'))
            self.assertIn(str(root.resolve() / 'bridge/client.py'), captured[0])
            self.assertIn('--script', captured[0])
            self.assertNotIn('--no-preview', captured[0])

    def test_unknown_tool_bad_args_and_path_escape_rejected(self):
        with tempfile.TemporaryDirectory() as folder:
            tools = self.Tools(Path(folder), self.config)
            for name, arguments in [('delete_all', {}), ('scene', {'extra': 1}),
                                     ('run', {'code': 4, 'label': 'bad'}), ('run', {'code': 'x'}),
                                     ('save', {'file': '../outside.blend'}), ('save', {'file': 'bad.txt'})]:
                with self.subTest(name=name, arguments=arguments):
                    self.assertFalse(tools.execute(name, arguments, 'task1')['ok'])
            with self.assertRaises(ValueError):
                tools.execute('scene', {}, '../escape')

    def test_subprocess_timeout_is_pending(self):
        with tempfile.TemporaryDirectory() as folder:
            tools = self.Tools(Path(folder), self.config)
            with patch('adapters.blender.subprocess.run', side_effect=subprocess.TimeoutExpired(['cli'], 1)):
                result = tools.execute('run', {'code': 'pass', 'label': 'test'}, 'task1')
            self.assertTrue(result['pending'])

    def test_job_inspection_waits_for_retirement(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            tools = self.Tools(root, self.config)
            job = root / 'outputs/jobs/abc'
            queue = root / '.runtime/sessions/session1/working'
            job.mkdir(parents=True)
            queue.mkdir(parents=True)
            (job / 'result.json').write_text('{"ok":true,"id":"abc"}')
            (job / 'request.json').write_text('{"session":"session1"}')
            (queue / 'abc.json').write_text('{}')
            self.assertTrue(tools.inspect_job('abc')['pending'])
            (queue / 'abc.json').unlink()
            self.assertTrue(tools.inspect_job('abc')['ok'])
            with self.assertRaises(ValueError):
                tools.inspect_job('../outside')

    def test_preview_is_forwarded_as_image_only_inside_project(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            tools = self.Tools(root, self.config)
            image = root / 'outputs/p.png'
            image.parent.mkdir()
            image.write_bytes(b'\x89PNG\r\n\x1a\nexample')
            content = tools.image_content({'preview': 'outputs/p.png'})
            self.assertTrue(content[0]['image_url'].startswith('data:image/png;base64,'))
            with self.assertRaises(ValueError):
                tools.image_content({'preview': '../outside.png'})

    def test_malformed_tool_call_is_rejected_at_api_boundary(self):
        for item in (None, {'type': 'function_call', 'name': 'run', 'arguments': '{}'},
                     {'type': 'message', 'content': 'bad'}):
            response = json.dumps({'status': 'completed', 'output': [item]}).encode()
            with self.subTest(item=item), patch('llm.client.urlopen', return_value=io.BytesIO(response)):
                with self.assertRaises(self.Error):
                    self.request(self.client())


if __name__ == '__main__':
    unittest.main()
