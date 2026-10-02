"""Explicit natural-language entry point. The existing Blender CLI remains unchanged."""
import argparse
from dataclasses import fields
import json
from pathlib import Path
import sys

from adapters.blender import BlenderTools
from bridge.common import FileLock, project_path, write_json
from llm.client import ModelCallError, ResponsesClient
from .audit import AuditLog
from .config import load_config
from .executor import TaskExecutor
from .model_router import parse_model_command, route_task
from .types import MODEL_TIERS, RoutingContext

ROOT = Path(__file__).resolve().parents[1]


def context_from_json(value, model_mode, default_mode='auto'):
    data = json.loads(value or '{}')
    if not isinstance(data, dict):
        raise ValueError('context must be an object')
    if 'modelMode' in data:
        if 'model_mode' in data:
            raise ValueError('Use modelMode or model_mode, not both')
        data['model_mode'] = data.pop('modelMode')
    allowed = {field.name for field in fields(RoutingContext)}
    if set(data) - allowed:
        raise ValueError('Unknown context fields: ' + ', '.join(sorted(set(data) - allowed)))
    counts = {'expected_tool_calls', 'step_count', 'previous_failures', 'sol_failures', 'tool_call_count'}
    for key, item in data.items():
        if key in counts and (type(item) is not int or item < 0):
            raise ValueError(f'{key} must be a non-negative integer')
        if key not in counts | {'model_mode'} and item is not None and type(item) is not bool:
            raise ValueError(f'{key} must be a boolean')
    if model_mode is not None:
        data['model_mode'] = model_mode
    data.setdefault('model_mode', default_mode)
    return RoutingContext(**data)


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest='command', required=True)
    for name in ('route', 'run', 'chat'):
        command = sub.add_parser(name)
        if name != 'chat':
            command.add_argument('task')
        else:
            command.add_argument('--dry-run', action='store_true')
        command.add_argument('--model', choices=('auto', *MODEL_TIERS))
        command.add_argument('--context', help='JSON feature/estimate overrides')
        command.add_argument('--config', help='Project JSON config override')
        command.add_argument('--debug', action='store_true')
    inspect = sub.add_parser('inspect-job')
    inspect.add_argument('job_id')
    args = parser.parse_args(argv)

    def output(value, compact=False):
        print(json.dumps(value, ensure_ascii=False, indent=None if compact else 2), flush=True)

    try:
        if args.command == 'inspect-job':
            result = BlenderTools(ROOT, load_config()).inspect_job(args.job_id)
            output(result)
            return 0 if result.get('ok') else 2 if result.get('pending') else 1
        config = load_config(project_path(ROOT, args.config) if args.config else None)
        context = context_from_json(args.context, args.model, config['model_mode'])
        if args.debug:
            config['logging']['debug'] = True

        def perform(task, mode_context, dry_run):
            decision = route_task(task, mode_context, config)
            if dry_run:
                return {'ok': True, 'dry_run': True, 'decision': decision.to_dict()}
            # Validate the key before connecting to or querying Blender. No credential files are read.
            client = ResponsesClient(config)
            with FileLock(ROOT / '.runtime/router.lock'):
                tools = BlenderTools(ROOT, config)
                status = tools.execute('status', {}, 'preflight')
                if not status.get('ok') or not status.get('connected'):
                    raise ValueError('No Blender connection. Run scripts/blender.ps1 start first.')
                if status.get('worker', {}).get('state') not in ('ready', None):
                    raise ValueError('Blender is busy or unavailable; inspect status before a new task.')
                result = TaskExecutor(client, tools, config,
                                      AuditLog(ROOT / 'outputs/router', config['logging']['debug'])).execute(task, mode_context)
                path = ROOT / 'outputs/router' / result.state.task_id / 'result.json'
                payload = result.to_dict()
                payload['result_file'] = path.relative_to(ROOT).as_posix()
                write_json(path, payload)
                return payload

        if args.command == 'chat':
            # Each task owns its own limits/state; only the explicit model preference persists.
            for line in sys.stdin:
                line = line.strip()
                if line in ('/quit', '/exit'):
                    break
                if not line:
                    continue
                try:
                    task, mode = parse_model_command(line, context.model_mode)
                    context.model_mode = mode
                    if not task:
                        output({'ok': True, 'model_mode': mode}, compact=True)
                        continue
                    output(perform(task, context, args.dry_run), compact=True)
                except (ValueError, OSError, ModelCallError) as error:
                    output({'ok': False, 'error': str(error)}, compact=True)
            return 0
        result = perform(args.task, context, args.command == 'route')
        output(result)
        return 0 if result['ok'] else 2 if result['state']['status'] == 'pending' else 1
    except (ValueError, OSError, ModelCallError) as error:
        output({'ok': False, 'error': str(error)})
        return 1
