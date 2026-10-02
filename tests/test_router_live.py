"""Opt-in router -> actual CLI/queue/bpy test, without paid model calls."""
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import time
import unittest
import uuid

from adapters.blender import BlenderTools
from router.config import load_config
from router.executor import TaskExecutor
from test_execution import ScriptedClient, call, done

ROOT = Path(__file__).resolve().parents[1]


@unittest.skipUnless(os.environ.get('BLENDER_E2E') == '1', 'set BLENDER_E2E=1 for real Blender')
class RouterLiveTests(unittest.TestCase):
    def test_router_edits_isolated_blender_preserving_backup_and_preview(self):
        clone = ROOT / '.runtime' / ('router 검증 ' + uuid.uuid4().hex[:8])
        shutil.copytree(ROOT / 'bridge', clone / 'bridge', ignore=shutil.ignore_patterns('__pycache__'))
        def cli(*args):
            process = subprocess.run([sys.executable, str(clone / 'bridge/client.py'), *args],
                                     capture_output=True, text=True, encoding='utf-8', timeout=90)
            self.assertEqual(process.returncode, 0, process.stdout + process.stderr)
            return json.loads(process.stdout)
        config = load_config()
        tools = BlenderTools(clone, config)
        try:
            cli('start', '--background')
            code = """# User test: move only the default cube in an isolated test scene.
bpy.data.objects['Cube'].location.x = 2
bpy.context.scene.render.engine = 'CYCLES'
bpy.context.scene.cycles.device = 'CPU'
bpy.context.scene.cycles.samples = 1
bpy.context.scene.render.resolution_x = 160
bpy.context.scene.render.resolution_y = 120
"""
            model = ScriptedClient([call('scene'), call('run', {'code': code, 'label': '독립 테스트 Cube 이동'}, 'run1'),
                                    call('scene', call_id='scene2'), done()])
            result = TaskExecutor(model, tools, config).execute('Cube를 X축으로 2m 이동')
            self.assertTrue(result.ok, result.error)
            self.assertEqual(result.state.original_model, 'luna')
            self.assertEqual(result.state.tool_call_count, 3)
            scene = cli('scene')['scene']
            self.assertEqual(next(o for o in scene['objects'] if o['name'] == 'Cube')['location'][0], 2)
            latest = json.loads((clone / 'outputs/latest.json').read_text(encoding='utf-8'))
            for key in ('backup', 'file', 'snapshot', 'preview'):
                self.assertTrue((clone / latest[key]).is_file(), key)
            self.assertTrue(any(part.get('type') == 'input_image' for request in model.requests
                                for item in request['history'] if isinstance(item.get('content'), list)
                                for part in item['content']))
            report = ROOT / 'outputs/verification/router-smoke.json'
            report.parent.mkdir(parents=True, exist_ok=True)
            report.write_text(json.dumps({'ok': True, 'clone': clone.relative_to(ROOT).as_posix(),
                                          'preview': (clone / latest['preview']).relative_to(ROOT).as_posix(),
                                          'checks': ['router state', 'actual CLI', 'actual scene edit', 'backup',
                                                     'saved blend', 'snapshot', 'PNG forwarded to model', 'scene verification'],
                                          'result': result.to_dict()}, ensure_ascii=False, indent=2), encoding='utf-8')
        finally:
            cli('stop')


if __name__ == '__main__':
    unittest.main()
