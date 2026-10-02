"""Exercise the actual state machine with only HTTP/Blender effects substituted."""
import copy
import importlib.util
import json
from pathlib import Path
import tempfile
import unittest

from router.config import load_config
from router.types import RoutingContext


def call(name='scene', arguments=None, call_id='c1'):
    return {'status': 'completed', 'output': [{'type': 'function_call', 'name': name,
            'arguments': json.dumps(arguments or {}), 'call_id': call_id}],
            'usage': {'input_tokens': 10, 'output_tokens': 5,
                      'input_tokens_details': {'cached_tokens': 2},
                      'output_tokens_details': {'reasoning_tokens': 3}}}


def done(message='완료'):
    return {'status': 'completed', 'output': [{'type': 'message', 'role': 'assistant',
            'content': [{'type': 'output_text', 'text': message}]}]}


class ScriptedClient:
    def __init__(self, responses):
        self.responses = iter(responses)
        self.requests = []

    def complete(self, **kwargs):
        self.requests.append(copy.deepcopy(kwargs))
        response = next(self.responses)
        if isinstance(response, Exception):
            raise response
        return response


class ScriptedTools:
    schemas = []
    instructions = 'Test Blender transport.'

    def __init__(self, results):
        self.results = iter(results)
        self.calls = []

    def execute(self, name, arguments, task_id):
        self.calls.append((name, arguments, task_id))
        return next(self.results)

    def image_content(self, result):
        return []


class ExecutionTests(unittest.TestCase):
    def setUp(self):
        self.assertIsNotNone(importlib.util.find_spec('router.executor'), 'executor is not implemented')
        from router.executor import TaskExecutor
        self.Executor = TaskExecutor
        self.config = load_config()

    def execute(self, task, responses, results, context=None):
        self.client = ScriptedClient(responses)
        self.tools = ScriptedTools(results)
        return self.Executor(self.client, self.tools, self.config).execute(task, context)

    def test_luna_repeated_tool_failures_escalate_to_sol(self):
        result = self.execute('Cube 이동', [call(call_id=str(i)) for i in range(3)] + [done()],
                              [{'ok': False, 'error': 'object not found'},
                               {'ok': False, 'error': 'temporary MCP error'}, {'ok': True}])
        self.assertTrue(result.ok)
        self.assertEqual(result.state.failure_count, 2)
        self.assertEqual(result.state.tool_call_count, 3)
        self.assertEqual(result.state.escalation_history[0]['to'], 'sol')
        self.assertEqual(result.state.attempt_count, 3)
        self.assertIn('temporary MCP error', json.dumps(self.client.requests[-1]['history']))

    def test_sol_two_logical_failures_escalate_to_astra(self):
        responses = [call('finish_task', {'success': False, 'message': '잘못된 계획', 'error_kind': 'plan'}, 'p1'),
                     call('finish_task', {'success': False, 'message': '목표 불일치', 'error_kind': 'goal'}, 'p2'),
                     call('scene', call_id='s1'), done()]
        result = self.execute('책상 모델링', responses, [{'ok': True}])
        self.assertTrue(result.ok)
        self.assertEqual(result.state.selected_model, 'astra')
        self.assertEqual(result.decision.reasoning_effort, 'xhigh')

    def test_transient_error_uses_same_model(self):
        result = self.execute('책상 모델링', [call(call_id='1'), call(call_id='2'), done()],
                              [{'ok': False, 'error': 'temporary MCP error'}, {'ok': True}])
        self.assertTrue(result.ok)
        self.assertFalse(result.state.escalated)

    def test_infrastructure_failures_never_trigger_astra(self):
        result = self.execute('책상 모델링', [call(call_id=str(i)) for i in range(5)],
                              [{'ok': False, 'error': 'temporary MCP error'}] * 5)
        self.assertFalse(result.ok)
        self.assertEqual(result.state.selected_model, 'sol')
        self.assertLessEqual(result.state.model_call_count, 4)

    def test_manual_model_is_not_escalated_for_bad_plans(self):
        responses = [call('finish_task', {'success': False, 'message': 'bad plan', 'error_kind': 'plan'}, str(i)) for i in range(4)]
        result = self.execute('/model luna\n책상 모델링', responses, [])
        self.assertFalse(result.ok)
        self.assertFalse(result.state.escalated)
        self.assertEqual(result.state.selected_model, 'luna')
        self.assertEqual(result.state.attempt_count, 3)

    def test_model_unavailable_allows_manual_fallback(self):
        from llm.client import ModelCallError
        result = self.execute('/model luna\nCube 이동',
                              [ModelCallError('unavailable', 'model unavailable'), call(), done()], [{'ok': True}])
        self.assertTrue(result.ok)
        self.assertEqual(result.state.selected_model, 'sol')
        self.assertEqual(result.state.escalation_history[0]['kind'], 'fallback')

    def test_auth_failure_does_not_cycle_models(self):
        from llm.client import ModelCallError
        result = self.execute('Cube 이동', [ModelCallError('fatal', 'HTTP 401')], [])
        self.assertFalse(result.ok)
        self.assertEqual(result.state.model_call_count, 1)

    def test_pending_never_resubmits(self):
        pending = {'ok': False, 'pending': True, 'id': 'job', 'result': 'outputs/jobs/job/result.json'}
        result = self.execute('Cube 이동', [call()], [pending])
        self.assertFalse(result.ok)
        self.assertEqual(result.state.status, 'pending')
        self.assertEqual(result.state.tool_call_count, 1)
        self.assertEqual(result.state.attempt_count, 1)
        self.assertEqual(result.pending_result, pending)

    def test_partial_change_demands_scene_read_before_next_write(self):
        result = self.execute('Cube 이동', [call('scene'), call('run', {'script': 'x'}),
                              call('run', {'script': 'y'}, 'c2'), call('scene', call_id='c3'), done()],
                              [{'ok': True}, {'ok': False, 'error': 'ValueError: wrong state', 'recovery': 'Partial changes may remain'}, {'ok': True}])
        self.assertFalse(result.ok, 'reading a scene alone must not erase the unresolved failed modification')
        self.assertEqual([x[0] for x in self.tools.calls], ['scene', 'run', 'scene'])

    def test_all_global_budgets_apply_before_side_effect(self):
        self.config['limits']['max_tool_calls'] = 1
        result = self.execute('Cube 이동', [call(call_id='1'), call(call_id='2')], [{'ok': True}] * 2)
        self.assertFalse(result.ok)
        self.assertEqual(result.state.tool_call_count, 1)
        self.config['limits']['max_model_calls'] = 1
        result = self.execute('Cube 이동', [call(), done()], [{'ok': True}])
        self.assertFalse(result.ok)
        self.assertEqual(result.state.model_call_count, 1)

    def test_context_tool_usage_counts_against_remaining_budget(self):
        self.config['limits']['max_tool_calls'] = 2
        result = self.execute('Cube 이동', [call()], [], RoutingContext(tool_call_count=2))
        self.assertFalse(result.ok)
        self.assertEqual(len(self.tools.calls), 0)

    def test_escalation_budget_blocks_model_change(self):
        self.config['limits']['max_escalations'] = 0
        result = self.execute('Cube 이동', [call(call_id='1'), call(call_id='2')],
                              [{'ok': False, 'error': 'object not found'}, {'ok': False, 'error': 'wrong object name'}])
        self.assertFalse(result.ok)
        self.assertFalse(result.state.escalated)

    def test_identical_mutation_is_never_applied_twice(self):
        result = self.execute('Cube 이동', [call('scene'), call('run', {'script': 'x'}, 'a'),
                              call('run', {'script': 'x'}, 'b')], [{'ok': True}, {'ok': True}])
        self.assertFalse(result.ok)
        self.assertEqual([x[0] for x in self.tools.calls], ['scene', 'run'])

    def test_identical_tool_call_limit_stops_poll_loop(self):
        result = self.execute('Cube 이동', [call(call_id=str(i)) for i in range(3)], [{'ok': True}] * 3)
        self.assertFalse(result.ok)
        self.assertEqual(result.state.tool_call_count, 2)

    def test_identical_error_limit_survives_model_switch(self):
        self.config['limits']['max_identical_errors'] = 2
        result = self.execute('Cube 이동', [call(call_id='1'), call(call_id='2')],
                              [{'ok': False, 'error': 'same failure'}] * 2)
        self.assertFalse(result.ok)
        self.assertEqual(result.state.failure_count, 2)

    def test_empty_or_incomplete_response_is_not_success(self):
        for response in ({'status': 'incomplete', 'output': []}, {'status': 'completed', 'output': []}, done()):
            self.config['limits']['max_retries_per_model'] = 0
            result = self.execute('Cube 이동', [response], [])
            self.assertFalse(result.ok)

    def test_statistics_attribute_tokens_and_attempts_to_models(self):
        self.config['models']['luna']['pricing_per_million'] = {'input': 2, 'cached_input': 1, 'output': 4}
        result = self.execute('Cube 이동', [call(), done()], [{'ok': True}])
        stats = result.statistics['luna']
        self.assertEqual((stats['calls'], stats['input_tokens'], stats['output_tokens']), (2, 10, 5))
        self.assertEqual(stats['reasoning_tokens'], 3)
        self.assertAlmostEqual(stats['estimated_cost'], .000038)
        self.assertEqual(stats['successful_attempts'], 1)
        self.assertEqual(stats['average_tool_calls'], 1)

    def test_default_log_omits_task_and_tool_body(self):
        from router.audit import AuditLog
        with tempfile.TemporaryDirectory() as folder:
            log = AuditLog(Path(folder), debug=False)
            result = self.Executor(ScriptedClient([call(), done()]), ScriptedTools([{'ok': True}]),
                                   self.config, log=log).execute('Cube SECRET_PRIVATE 이동')
            body = '\n'.join(p.read_text(encoding='utf-8') for p in Path(folder).rglob('*.jsonl'))
            self.assertTrue(result.ok)
            self.assertNotIn('SECRET_PRIVATE', body)
            self.assertIn('routing', body)

    def test_mutation_label_and_whitespace_do_not_bypass_replay_guard(self):
        result = self.execute('Cube 이동', [call('scene'),
                              call('run', {'code': 'obj.location.x += 2', 'label': 'first'}, 'a'),
                              call('run', {'code': 'obj.location.x  +=  2 # again', 'label': 'retry'}, 'b')],
                              [{'ok': True}, {'ok': True}])
        self.assertFalse(result.ok)
        self.assertEqual(result.state.tool_call_count, 2)

    def test_bad_image_returns_failed_state_after_successful_mutation(self):
        tools = ScriptedTools([{'ok': True}, {'ok': True, 'preview': 'bad.png'}])
        def images(result):
            if 'preview' in result:
                raise ValueError('Preview PNG does not exist')
            return []
        tools.image_content = images
        result = self.Executor(ScriptedClient([call('scene'), call('run', {'code': 'pass', 'label': 'x'})]),
                               tools, self.config).execute('Cube 이동')
        self.assertFalse(result.ok)
        self.assertEqual(result.state.status, 'failed')
        self.assertEqual(result.state.tool_call_count, 2)

    def test_validation_failure_before_submission_does_not_require_scene_again(self):
        result = self.execute('Cube 이동', [call('scene'), call('run', {'code': 'bad'}, 'a'),
                              call('run', {'code': 'fixed'}, 'b'), done()],
                              [{'ok': True}, {'ok': False, 'error': 'SyntaxError: invalid code', 'not_submitted': True}, {'ok': True}])
        self.assertTrue(result.ok)
        self.assertEqual([c[0] for c in self.tools.calls], ['scene', 'run', 'run'])

    def test_saved_change_with_render_error_is_not_reapplied(self):
        result = self.execute('Cube 이동', [call('scene'), call('run', {'code': 'x += 1'}, 'a'),
                              call('scene', call_id='b'), call('run', {'code': 'x += 1'}, 'c')],
                              [{'ok': True}, {'ok': False, 'error': 'Render failed',
                               'file': 'scenes/current.blend', 'snapshot': 'outputs/jobs/1/after.blend'}, {'ok': True}])
        self.assertFalse(result.ok)
        self.assertEqual(result.state.tool_call_count, 3)

    def test_saved_change_can_finish_after_scene_and_preview_recovery(self):
        result = self.execute('Cube 이동', [call('scene'), call('run', {'code': 'x += 1'}, 'a'),
                              call('scene', call_id='b'), call('preview', call_id='c'), done()],
                              [{'ok': True}, {'ok': False, 'error': 'Render failed',
                               'file': 'scenes/current.blend', 'snapshot': 'outputs/jobs/1/after.blend'},
                               {'ok': True}, {'ok': True}])
        self.assertTrue(result.ok)
        self.assertEqual(result.state.tool_call_count, 4)

    def test_partial_failure_cannot_repeat_same_code_after_inspection(self):
        result = self.execute('Cube 이동', [call('scene'), call('run', {'code': 'x += 1'}, 'a'),
                              call('scene', call_id='b'), call('run', {'code': 'x += 1'}, 'c')],
                              [{'ok': True}, {'ok': False, 'error': 'Python error after first edit'}, {'ok': True}])
        self.assertFalse(result.ok)
        self.assertEqual(result.state.tool_call_count, 3)


if __name__ == '__main__':
    unittest.main()
