import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]


class RouterCliTests(unittest.TestCase):
    def call(self, *args, stdin=None):
        return subprocess.run([sys.executable, '-m', 'router', *args], cwd=ROOT,
                              input=stdin, capture_output=True, text=True, encoding='utf-8', timeout=15)

    def test_dry_routing_without_network_or_scene_changes(self):
        result = self.call('route', 'Cube를 X축으로 2m 이동')
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(json.loads(result.stdout)['decision']['model'], 'luna')

    def test_forced_mode_and_context(self):
        result = self.call('route', '책상 모델링', '--model', 'astra', '--context', '{"expected_tool_calls":12}')
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(json.loads(result.stdout)['decision']['model'], 'astra')
        result = self.call('route', 'Cube 이동', '--context', '{"modelMode":"sol"}')
        self.assertEqual(json.loads(result.stdout)['decision']['model'], 'sol')

    def test_chat_slash_model_persists_until_auto(self):
        result = self.call('chat', '--dry-run', stdin='/model sol\nCube 이동\n/model auto\nCube 이동\n/quit\n')
        self.assertEqual(result.returncode, 0, result.stderr)
        rows = [json.loads(row) for row in result.stdout.splitlines()]
        self.assertEqual([row['decision']['model'] for row in rows if 'decision' in row], ['sol', 'luna'])

    def test_invalid_context_is_a_visible_error(self):
        for context in ('bad-json', '{"expected_tool_calls":-1}', '{"unknown":true}', '{"simple":"false"}'):
            result = self.call('route', 'Cube 이동', '--context', context)
            self.assertNotEqual(result.returncode, 0)
            self.assertFalse(json.loads(result.stdout)['ok'])

    def test_config_model_mode_applies_when_context_has_only_estimates(self):
        path = ROOT / '.runtime/router-test-config.json'
        path.parent.mkdir(exist_ok=True)
        path.write_text('{"model_mode":"astra"}', encoding='utf-8')
        try:
            result = self.call('route', 'Cube 이동', '--config', '.runtime/router-test-config.json',
                               '--context', '{"expected_tool_calls":1}')
            self.assertEqual(json.loads(result.stdout)['decision']['model'], 'astra')
        finally:
            path.unlink()


if __name__ == '__main__':
    unittest.main()
