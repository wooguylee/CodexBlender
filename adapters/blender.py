"""Additive adapter over existing CLI commands; never imports bpy or modifies worker code."""
import base64
import hashlib
import json
import os
from pathlib import Path
import re
import subprocess
import sys

from bridge.common import project_path


def _schema(name, description, properties=None):
    properties = properties or {}
    return {'type': 'function', 'name': name, 'description': description, 'strict': True,
            'parameters': {'type': 'object', 'properties': properties,
                           'required': list(properties), 'additionalProperties': False}}


class BlenderTools:
    schemas = [
        _schema('scene', '현재 Scene, 카메라와 실제 객체 이름/변환을 조회한다. 변경 전에 필수.'),
        _schema('status', '현재 브리찌 연결과 진행 중인 작업 상태를 조회한다.'),
        _schema('run', '범위가 제한된 Blender Python을 보존 후 실행한다. 자동 백업/저장/카메라 PNG 포함. 실패 후 상태 재조회 필수.',
                {'code': {'type': 'string'}, 'label': {'type': 'string'}}),
        _schema('preview', '현재 카메라 PNG를 렌더한다. 기존 Scene 렌더 설정을 사용한다.'),
        _schema('save', '프로젝트 내부 .blend 파일에 저장한다. 기존 파일은 백업한다.', {'file': {'type': 'string'}}),
    ]

    def __init__(self, root, config):
        self.root = Path(root).resolve()
        self.config = config
        self.instructions = '''기존 Blender 파일 큐 CLI를 사용한다. run에는 bpy, PROJECT_ROOT, OUTPUT_DIR가 제공된다.
코드에 실행 PC의 절대 경로를 넣지 않는다. 모든 자산/결과를 프로젝트에 보존한다.
기존 객체/Scene 삭제, 파일 덮어쓰기, 외부 자산 도입, 네트워크/설치, Git 작업은 요청 범위에서만 한다.
run은 코드 실행 뒤 기본 원본과 snapshot, preview를 저장한다. 저비용 미리보기를 우선한다.
원본에는 여러 Scene이 있을 수 있다. 실제 조회한 대상만 수정하고 기존 제작물을 보존한다.
'''
        instructions = self.root / 'AGENTS.md'
        if instructions.is_file():
            self.instructions += '\n프로젝트 작업 지침:\n' + instructions.read_text(encoding='utf-8-sig')

    def execute(self, name, arguments, task_id):
        if not re.fullmatch(r'[A-Za-z0-9_-]+', task_id):
            raise ValueError('Invalid task ID')
        try:
            schema = next((tool['parameters'] for tool in self.schemas if tool['name'] == name), None)
            if schema is None:
                raise ValueError(f'Unknown tool: {name}')
            if not isinstance(arguments, dict) or set(arguments) != set(schema['properties']):
                raise ValueError('Unexpected or missing tool arguments')
            if any(not isinstance(value, str) or not value.strip() for value in arguments.values()):
                raise ValueError('Tool arguments must be non-empty strings')
            command = [sys.executable, str(self.root / 'bridge/client.py'), name]
            timeout = self.config['bridge']['timeout_seconds']
            if name != 'status':
                command += ['--timeout', str(timeout)]
            if name == 'run':
                code = arguments['code']
                if len(code.encode('utf-8')) > self.config['bridge']['max_script_bytes']:
                    raise ValueError('Python script exceeds configured byte limit')
                # Compile without execution to catch syntax errors before submitting any Blender changes.
                compile(code, '<Blender workflow>', 'exec')
                folder = project_path(self.root, f'workflows/model-routing/{task_id}')
                folder.mkdir(parents=True, exist_ok=True)
                digest = hashlib.sha256(code.encode('utf-8')).hexdigest()[:16]
                source = folder / f'operation-{digest}.py'
                if not source.exists():
                    header = '# 사용자 요청 작업: ' + arguments['label'].replace('\n', ' ').replace('\r', ' ') + '\n'
                    source.write_text(header + code + '\n', encoding='utf-8')
                command += ['--script', source.relative_to(self.root).as_posix(), '--label', arguments['label']]
            elif name == 'save':
                target = project_path(self.root, arguments['file'])
                if target.suffix.lower() != '.blend':
                    raise ValueError('Save target must end in .blend')
                command += ['--file', target.relative_to(self.root).as_posix()]
        except (ValueError, SyntaxError, OSError) as error:
            return {'ok': False, 'error': f'{type(error).__name__}: {error}', 'not_submitted': True}
        try:
            completed = subprocess.run(command, cwd=self.root, capture_output=True, text=True,
                                       encoding='utf-8', errors='replace', timeout=timeout + 30,
                                       env={**os.environ, 'PYTHONUTF8': '1'})
        except subprocess.TimeoutExpired:
            return {'ok': False, 'pending': True, 'error': 'CLI timeout; inspect status and outputs/jobs before any new mutation', 'tool': name}
        except OSError as error:
            return {'ok': False, 'error': f'CLI launch failed: {type(error).__name__}', 'not_submitted': True}
        try:
            result = json.loads(completed.stdout)
            if not isinstance(result, dict) or type(result.get('ok')) is not bool:
                raise ValueError('Expected ok boolean')
        except ValueError:
            return {'ok': False, 'pending': True, 'error': 'CLI result unavailable; inspect status and outputs/jobs', 'tool': name}
        if completed.returncode and result['ok']:
            return {'ok': False, 'pending': True, 'error': 'CLI exit code and result disagree', 'tool': name}
        if not result['ok'] and name in ('run', 'save', 'preview') and not result.get('id'):
            # A client exception can occur after queue submission. Without an ID we cannot prove otherwise.
            result['pending'] = True
        return result

    def inspect_job(self, job_id):
        if not re.fullmatch(r'[A-Za-z0-9-]+', job_id):
            raise ValueError('Invalid Blender job ID')
        folder = project_path(self.root, f'outputs/jobs/{job_id}')
        request = folder / 'request.json'
        if not request.is_file():
            raise ValueError('Unknown Blender job ID')
        data = json.loads(request.read_text(encoding='utf-8'))
        session = data.get('session', '')
        if not re.fullmatch(r'[A-Za-z0-9_-]+', session):
            raise ValueError('Invalid job session')
        session_dir = project_path(self.root, '.runtime/sessions/' + session)
        result_path = folder / 'result.json'
        if not result_path.exists() or any((session_dir / queue / (job_id + '.json')).exists() for queue in ('queue', 'working')):
            return {'ok': False, 'pending': True, 'id': job_id, 'result': result_path.relative_to(self.root).as_posix()}
        return json.loads(result_path.read_text(encoding='utf-8'))

    def image_content(self, result):
        if not result.get('preview'):
            return []
        path = project_path(self.root, result['preview'])
        if path.suffix.lower() != '.png' or not path.is_file():
            raise ValueError('Preview PNG does not exist')
        if path.stat().st_size > self.config['bridge']['max_image_bytes']:
            raise ValueError('Preview exceeds configured image byte limit')
        data = path.read_bytes()
        if not data.startswith(b'\x89PNG\r\n\x1a\n'):
            raise ValueError('Invalid preview PNG signature')
        return [{'type': 'input_image', 'image_url': 'data:image/png;base64,' + base64.b64encode(data).decode('ascii')}]
