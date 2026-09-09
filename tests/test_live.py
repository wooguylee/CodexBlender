"""Opt-in real Blender integration: BLENDER_E2E=1 python -m unittest discover -s tests -v."""
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import time
import unittest
import uuid

ROOT = Path(__file__).resolve().parents[1]


@unittest.skipUnless(os.environ.get('BLENDER_E2E') == '1', 'set BLENDER_E2E=1 for real Blender')
class LiveTests(unittest.TestCase):
    def test_portable_session_save_preview_failure_and_restart(self):
        self.assertTrue((ROOT / 'bridge/client.py').is_file(), 'CLI is not implemented')
        clone = ROOT / '.runtime' / ('clone space 한글 ' + uuid.uuid4().hex[:8])
        for folder in ('bridge', 'scripts', 'workflows'):
            shutil.copytree(ROOT / folder, clone / folder, ignore=shutil.ignore_patterns('__pycache__'))

        def call(*args, expected=0):
            completed = subprocess.run([sys.executable, str(clone / 'bridge/client.py'), *args],
                                       capture_output=True, text=True, encoding='utf-8', timeout=180)
            self.assertEqual(completed.returncode, expected, completed.stdout + completed.stderr)
            return json.loads(completed.stdout)

        try:
            started = call('start', '--background')
            self.assertTrue(started['ok'])
            if os.name == 'nt':
                # Exercise Windows PowerShell 5.1 with a UTF-8 local config and Unicode install path.
                blender = Path(call('doctor')['blender'])
                install_link = clone / '블렌더 설치'
                try:
                    install_link.symlink_to(blender.parent, target_is_directory=True)
                except OSError:
                    install_link = None  # This privilege is not granted on every Windows PC.
                if install_link:
                    (clone / 'blender.local.json').write_text(json.dumps({
                        'blender_executable': str(install_link / blender.name)}, ensure_ascii=False), encoding='utf-8')
                    environment = os.environ.copy()
                    environment.pop('BLENDER_EXECUTABLE', None)
                    launcher = subprocess.run(['powershell.exe', '-NoProfile', '-ExecutionPolicy', 'Bypass',
                                              '-File', str(clone / 'scripts/blender.ps1'), 'doctor'],
                                             capture_output=True, env=environment, timeout=30)
                    self.assertEqual(launcher.returncode, 0, launcher.stderr.decode(errors='replace'))
                    self.assertTrue(json.loads(launcher.stdout.decode('utf-8-sig'))['ok'])
            again = call('start', '--background')
            self.assertEqual(again['session'], started['session'])
            # Removing session isolation or save/backup would break the assertions below.
            script = clone / 'workflows/test_scene.py'
            script.write_text("""import bpy
bpy.ops.mesh.primitive_cube_add()
obj = bpy.context.object
obj.name = 'PortableProbe'
obj.location.x = 2.5
bpy.context.scene.render.engine = 'CYCLES'
bpy.context.scene.cycles.device = 'CPU'
bpy.context.scene.cycles.samples = 1
bpy.context.scene.render.resolution_x = 160
bpy.context.scene.render.resolution_y = 120
""", encoding='utf-8')
            result = call('run', '--script', 'workflows/test_scene.py', '--label', 'portable smoke')
            self.assertTrue(result['ok'])
            self.assertTrue((clone / result['preview']).is_file())
            self.assertTrue((clone / result['backup']).is_file())
            self.assertTrue((clone / 'scenes/current.blend').is_file())
            script.write_text("raise RuntimeError('expected integration failure')\n", encoding='utf-8')
            failure = call('run', '--script', 'workflows/test_scene.py', expected=1)
            self.assertIn('expected integration failure', failure['error'])
            self.assertTrue((clone / failure['backup']).is_file())
            scene = call('scene')
            probe = next(o for o in scene['scene']['objects'] if o['name'] == 'PortableProbe')
            self.assertEqual(probe['location'][0], 2.5)
            script.write_text("import time\ntime.sleep(1.5)\nbpy.data.objects['PortableProbe'].location.y = 7\n", encoding='utf-8')
            pending = call('run', '--script', 'workflows/test_scene.py', '--no-preview', '--timeout', '0.02', expected=1)
            self.assertTrue(pending['pending'])
            rejected = call('run', '--script', 'workflows/test_scene.py', expected=1)
            self.assertIn('pending/running', rejected['error'])
            result_path = clone / pending['result']
            deadline = time.monotonic() + 20
            while not result_path.exists() and time.monotonic() < deadline:
                time.sleep(.1)
            self.assertTrue(json.loads(result_path.read_text(encoding='utf-8'))['ok'])
            call('save', '--file', 'scenes/checkpoint.blend')
            saved = call('save', '--file', 'scenes/checkpoint.blend')
            self.assertTrue((clone / saved['backup']).is_file())
            call('run', '--script', '../outside.py', expected=1)
            call('stop')
            self.assertFalse(call('status')['connected'])
            restarted = call('start', '--background')
            self.assertNotEqual(restarted['session'], started['session'])
            scene = call('scene')
            self.assertIn('PortableProbe', [o['name'] for o in scene['scene']['objects']])
            report = ROOT / 'outputs/verification/portable-smoke.json'
            report.parent.mkdir(parents=True, exist_ok=True)
            report.write_text(json.dumps({'ok': True, 'clone': str(clone.relative_to(ROOT)),
                                         'blender': restarted.get('blender'),
                                         'checks': ['start', 'duplicate start', 'unicode relocated path',
                                                    'run', 'backup', 'preview', 'error recovery',
                                                    'timeout without replay', 'busy rejection', 'save backup',
                                                    'path rejection', 'restart saved scene']}, indent=2), encoding='utf-8')
        finally:
            call('stop')


if __name__ == '__main__':
    unittest.main()
