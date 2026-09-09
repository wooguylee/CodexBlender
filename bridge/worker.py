"""Runs inside Blender. All bpy access happens on Blender's main thread."""
import argparse
import contextlib
from datetime import datetime, timezone
import os
from pathlib import Path
import sys
import time
import traceback

import bpy

sys.path.insert(0, str(Path(__file__).resolve().parent))
from common import FileLock, project_path, read_json, write_json


class Worker:
    def __init__(self, root, session):
        self.root = root.resolve()
        self.session = session
        self.runtime = self.root / '.runtime'
        self.folder = self.runtime / 'sessions' / session
        for name in ('queue', 'working', 'done'):
            (self.folder / name).mkdir(parents=True, exist_ok=True)
        self.lock = FileLock(self.runtime / 'bridge.lock')
        self.lock.__enter__()
        self.running = True
        self.last_heartbeat = 0
        self.active = None
        write_json(self.runtime / 'connection.json', {
            'session': session, 'pid': os.getpid(), 'blender': bpy.app.version_string,
            'background': bpy.app.background, 'root': str(self.root),
            'started_at': datetime.now(timezone.utc).isoformat()})
        self.status('ready')

    def status(self, state, **details):
        write_json(self.folder / 'status.json', {'state': state, 'job': self.active,
                   'updated_at': datetime.now(timezone.utc).isoformat(), **details})
        self.last_heartbeat = time.monotonic()

    def rel(self, path):
        return path.relative_to(self.root).as_posix()

    def save(self, path, copy=False):
        path = project_path(self.root, path)
        path.parent.mkdir(parents=True, exist_ok=True)
        bpy.ops.wm.save_as_mainfile(filepath=str(path), check_existing=False, copy=copy,
                                   relative_remap=True, compress=True)
        return self.rel(path)

    def scene(self):
        scene = bpy.context.scene
        return {'name': scene.name, 'file': bpy.data.filepath,
                'camera': scene.camera.name if scene.camera else None,
                'engine': scene.render.engine,
                'objects': [{'name': o.name, 'type': o.type,
                             'location': list(o.location), 'scale': list(o.scale),
                             'dimensions': list(o.dimensions)} for o in scene.objects]}

    def preview(self, folder):
        scene = bpy.context.scene
        if scene.camera is None:
            raise RuntimeError('No active camera. Add a camera in a workflow and request preview again.')
        render = scene.render
        previous = (render.filepath, render.image_settings.file_format, render.use_file_extension)
        try:
            render.filepath = str(folder / 'preview.png')
            render.image_settings.file_format = 'PNG'
            render.use_file_extension = True
            bpy.ops.render.render(write_still=True)
        finally:
            render.filepath, render.image_settings.file_format, render.use_file_extension = previous
        return self.rel(folder / 'preview.png')

    def execute(self, request):
        if request.get('session') != self.session:
            raise ValueError('Session mismatch; old requests are never executed')
        job_id = request['id']
        if not job_id or any(c not in '0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz-' for c in job_id):
            raise ValueError('Invalid job ID')
        folder = project_path(self.root, 'outputs/jobs/' + job_id)
        folder.mkdir(parents=True, exist_ok=True)
        result = {'ok': False, 'id': job_id, 'action': request['action'], 'label': request['label']}
        started = time.monotonic()
        with (folder / 'execution.log').open('w', encoding='utf-8') as log:
            try:
                with contextlib.redirect_stdout(log), contextlib.redirect_stderr(log):
                    action = request['action']
                    if action == 'run':
                        result['backup'] = self.save(folder / 'before.blend', copy=True)
                        script = folder / 'script.py'
                        namespace = {'__name__': '__main__', '__file__': str(script),
                                     'PROJECT_ROOT': self.root, 'OUTPUT_DIR': folder, 'bpy': bpy}
                        exec(compile(script.read_text(encoding='utf-8-sig'), str(script), 'exec'), namespace)
                        bpy.context.view_layer.update()
                        result['file'] = self.save(self.root / 'scenes/current.blend')
                        result['snapshot'] = self.save(folder / 'after.blend', copy=True)
                        if request.get('preview', True):
                            result['preview'] = self.preview(folder)
                    elif action == 'scene':
                        result['scene'] = self.scene()
                    elif action == 'preview':
                        result['preview'] = self.preview(folder)
                    elif action == 'save':
                        destination = project_path(self.root, request['file'])
                        if destination.suffix.lower() != '.blend':
                            raise ValueError('Save requires .blend extension')
                        if destination.exists():
                            import shutil
                            shutil.copy2(destination, folder / 'previous-file.blend')
                            result['backup'] = self.rel(folder / 'previous-file.blend')
                        result['file'] = self.save(destination)
                    elif action == 'stop':
                        self.running = False
                    else:
                        raise ValueError(f'Unknown action: {action}')
                    for screen in bpy.data.screens:
                        for area in screen.areas:
                            area.tag_redraw()
                    result['ok'] = True
            except BaseException as error:
                result['error'] = f'{type(error).__name__}: {error}'
                result['traceback'] = traceback.format_exc()
                log.write(result['traceback'])
                result['recovery'] = 'Partial changes may remain. Inspect backup; do not automatically retry.'
        result['elapsed_seconds'] = round(time.monotonic() - started, 3)
        result['completed_at'] = datetime.now(timezone.utc).isoformat()
        write_json(folder / 'result.json', result)
        if result.get('preview'):
            write_json(self.root / 'outputs/latest.json', result)
        return result

    def tick(self):
        try:
            jobs = sorted((self.folder / 'queue').glob('*.json'))
            if jobs:
                queued = jobs[0]
                working = self.folder / 'working' / queued.name
                queued.replace(working)
                self.active = queued.stem
                self.status('busy')
                result = self.execute(read_json(working))
                working.replace(self.folder / 'done' / working.name)
                self.active = None
                self.status('ready' if self.running else 'stopped', last_result=result['id'], last_ok=result['ok'])
            elif time.monotonic() - self.last_heartbeat > 2:
                self.status('ready')
        except BaseException:
            # Malformed transport request: preserve the working file for inspection, stop consuming.
            self.status('transport_error', error=traceback.format_exc())
            self.running = False
        if not self.running:
            self.lock.__exit__(None, None, None)
            return None
        return .25


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--project', required=True)
    parser.add_argument('--session', required=True)
    args = parser.parse_args(sys.argv[sys.argv.index('--') + 1:])
    worker = Worker(Path(args.project), args.session)
    # Keep a strong reference and retain timers when loading a .blend from the UI.
    bpy.app.driver_namespace['codex_blender_worker'] = worker
    if bpy.app.background:
        try:
            while worker.running:
                if worker.tick() is None:
                    break
                time.sleep(.25)
        finally:
            worker.lock.__exit__(None, None, None)
    else:
        bpy.app.timers.register(worker.tick, first_interval=.25, persistent=True)


if __name__ == '__main__':
    main()
