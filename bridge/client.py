"""Portable command-line client for the project-owned Blender process."""
import argparse
from datetime import datetime, timezone
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys
import time
import uuid

from common import FileLock, is_locked, project_path, read_json, write_json

ROOT = Path(__file__).resolve().parents[1]
RUNTIME = ROOT / '.runtime'


def discover_blender():
    configured = os.environ.get('BLENDER_EXECUTABLE')
    local = ROOT / 'blender.local.json'
    if not configured and local.exists():
        configured = read_json(local).get('blender_executable')
    if configured:
        candidate = Path(configured).expanduser()
        if not candidate.is_file():
            raise ValueError(f'Configured Blender executable does not exist: {candidate}')
        return candidate.resolve()
    found = shutil.which('blender')
    if found:
        return Path(found).resolve()
    candidates = []
    if os.name == 'nt':
        for base in (Path(os.environ.get('ProgramFiles', 'C:/Program Files')) / 'Blender Foundation',
                     Path(os.environ.get('LOCALAPPDATA', str(Path.home()))) / 'Programs/Blender Foundation'):
            candidates.extend(base.glob('Blender*/blender.exe'))
    elif sys.platform == 'darwin':
        candidates.extend(Path('/Applications').glob('Blender*.app/Contents/MacOS/Blender'))
    else:
        candidates.extend(Path('/opt').glob('blender*/blender'))
        candidates.extend(Path('/snap/bin').glob('blender'))
    if not candidates:
        raise ValueError('Blender not found. Set BLENDER_EXECUTABLE or blender.local.json; see README.md.')
    return max(candidates, key=lambda p: tuple(int(x) for x in re.findall(r'\d+', str(p))))


def connection():
    if not is_locked(RUNTIME / 'bridge.lock'):
        return None
    try:
        return read_json(RUNTIME / 'connection.json')
    except (OSError, ValueError):
        return None


def start(args):
    with FileLock(RUNTIME / 'start.lock'):
        current = connection()
        if current:
            if args.file:
                raise ValueError('Already connected. Stop the bridge before starting with another file.')
            return {'ok': True, 'already_running': True, **current}
        blender = discover_blender()
        source = project_path(ROOT, args.file or 'scenes/current.blend')
        if args.file and not source.is_file():
            raise ValueError(f'Blend file not found: {source}')
        if source.suffix.lower() != '.blend':
            raise ValueError('Start file must be a .blend file')
        session = uuid.uuid4().hex
        session_dir = RUNTIME / 'sessions' / session
        session_dir.mkdir(parents=True)
        command = [str(blender), '--factory-startup', '--disable-autoexec']
        if args.background:
            command.append('--background')
        if source.is_file():
            command.append(str(source))
        command += ['--python', str(ROOT / 'bridge/worker.py'), '--', '--project', str(ROOT), '--session', session]
        with (session_dir / 'blender.log').open('wb') as log:
            kwargs = {'cwd': str(ROOT), 'stdin': subprocess.DEVNULL, 'stdout': log, 'stderr': subprocess.STDOUT}
            if os.name == 'nt':
                kwargs['creationflags'] = subprocess.CREATE_NEW_PROCESS_GROUP
                startup = subprocess.STARTUPINFO()
                startup.dwFlags |= subprocess.STARTF_USESHOWWINDOW
                startup.wShowWindow = 0 if args.background else 1
                kwargs['startupinfo'] = startup
            else:
                kwargs['start_new_session'] = True
            process = subprocess.Popen(command, **kwargs)
        deadline = time.monotonic() + args.timeout
        while time.monotonic() < deadline:
            current = connection()
            if current and current['session'] == session:
                return {'ok': True, **current}
            if process.poll() is not None:
                raise RuntimeError(f'Blender exited ({process.returncode}). See {session_dir / "blender.log"}')
            time.sleep(.2)
        raise TimeoutError(f'Blender startup timed out; process was not killed. Check status and {session_dir / "blender.log"}')


def send(args):
    current = connection()
    if not current:
        raise RuntimeError('No project Blender connection. Run start first.')
    session_dir = RUNTIME / 'sessions' / current['session']
    # One outstanding client at a time, including rendering. Blender also serializes its queue.
    with FileLock(RUNTIME / 'submit.lock'):
        pending = list((session_dir / 'queue').glob('*.json'))
        active = list((session_dir / 'working').glob('*.json'))
        if pending or active:
            raise RuntimeError('A job is still pending/running. Use status and its result path; do not resubmit.')
        script = None
        if args.command == 'run':
            script = project_path(ROOT, args.script)
            if not script.is_file() or script.suffix.lower() != '.py':
                raise ValueError('run requires an existing project .py file')
        target = None
        if args.command == 'save':
            target = project_path(ROOT, args.file)
            if target.suffix.lower() != '.blend':
                raise ValueError('Save target must end in .blend')
        job_id = datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S') + '-' + uuid.uuid4().hex[:10]
        job_dir = ROOT / 'outputs/jobs' / job_id
        job_dir.mkdir(parents=True)
        request = {'id': job_id, 'session': current['session'], 'action': args.command,
                   'label': getattr(args, 'label', None) or args.command,
                   'created_at': datetime.now(timezone.utc).isoformat(),
                   'preview': not getattr(args, 'no_preview', False)}
        if script:
            shutil.copyfile(script, job_dir / 'script.py')
            request['source'] = script.relative_to(ROOT).as_posix()
        if target:
            request['file'] = target.relative_to(ROOT).as_posix()
        write_json(job_dir / 'request.json', request)
        write_json(session_dir / 'queue' / (job_id + '.json'), request)
        result_file = job_dir / 'result.json'
        deadline = time.monotonic() + args.timeout
        while time.monotonic() < deadline:
            if result_file.exists():
                retired = not (session_dir / 'queue' / (job_id + '.json')).exists() and not (session_dir / 'working' / (job_id + '.json')).exists()
                stopped = args.command != 'stop' or not is_locked(RUNTIME / 'bridge.lock')
                if retired and stopped:
                    return read_json(result_file)
            if not is_locked(RUNTIME / 'bridge.lock'):
                # stop publishes its result before releasing the lock.
                if result_file.exists():
                    return read_json(result_file)
                raise RuntimeError(f'Blender disconnected. Inspect outputs/jobs/{job_id}; do not auto-retry.')
            time.sleep(.2)
        return {'ok': False, 'pending': True, 'id': job_id,
                'error': 'Wait timed out; job may still run. Do not submit it again.',
                'result': result_file.relative_to(ROOT).as_posix()}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest='command', required=True)
    sub.add_parser('doctor')
    sub.add_parser('status')
    p = sub.add_parser('start')
    p.add_argument('--file', help='Existing project .blend; default scenes/current.blend if present')
    p.add_argument('--background', action='store_true', help='Headless verification only')
    p.add_argument('--timeout', type=float, default=60)
    for name in ('scene', 'run', 'preview', 'save', 'stop'):
        p = sub.add_parser(name)
        p.add_argument('--timeout', type=float, default=180)
        if name == 'run':
            p.add_argument('--script', required=True)
            p.add_argument('--label', default='Scene edit')
            p.add_argument('--no-preview', action='store_true')
        if name == 'save':
            p.add_argument('--file', default='scenes/current.blend')
    args = parser.parse_args()
    try:
        if args.command == 'doctor':
            blender = discover_blender()
            version = subprocess.run([str(blender), '--version'], capture_output=True, text=True,
                                     encoding='utf-8', errors='replace', timeout=20, check=True).stdout.splitlines()[0]
            result = {'ok': True, 'root': str(ROOT), 'blender': str(blender), 'version': version,
                      'python': sys.version.split()[0], 'transport': 'project-local files; no network server'}
        elif args.command == 'status':
            current = connection()
            result = {'ok': True, 'connected': bool(current)}
            if current:
                result.update(current)
                status_file = RUNTIME / 'sessions' / current['session'] / 'status.json'
                if status_file.exists():
                    result['worker'] = read_json(status_file)
        elif args.command == 'start':
            result = start(args)
        else:
            result = send(args)
    except Exception as error:
        result = {'ok': False, 'error': str(error)}
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if result.get('ok') else 1


if __name__ == '__main__':
    if hasattr(sys.stdout, 'reconfigure'):
        sys.stdout.reconfigure(encoding='utf-8')
    raise SystemExit(main())
