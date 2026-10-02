"""Tier selection must reflect work complexity, not merely object count."""
import importlib.util
import os
from pathlib import Path
import unittest
from unittest.mock import patch


class RoutingTests(unittest.TestCase):
    def setUp(self):
        self.assertIsNotNone(importlib.util.find_spec('router'), 'routing package is not implemented')
        from router.config import load_config
        from router.model_router import route_task
        from router.types import RoutingContext
        self.config = load_config()
        self.route = route_task
        self.context = RoutingContext

    def test_requested_examples(self):
        cases = [
            ('Cube를 X축으로 2m 이동', 'luna'),
            ('선택된 100개 오브젝트 이름 앞에 chair_를 붙여', 'luna'),
            ('책상 모델을 만들고 Bevel과 Subdivision을 적용해', 'sol'),
            ('Principled BSDF와 Noise Texture를 이용해서 낡은 나무 재질을 만들어', 'sol'),
            ('Geometry Nodes로 절차적 울타리를 만들어', 'sol'),
            ('현재 Geometry Nodes에서 오브젝트 수를 늘리면 일부가 사라진다. 원인을 분석해서 수정해', 'astra'),
            ('현재 Scene 전체 구조를 분석해서 성능이 느린 이유를 찾고 최적화해', 'astra'),
        ]
        for task, expected in cases:
            with self.subTest(task=task):
                self.assertEqual(self.route(task).model, expected)

    def test_uncertain_and_mixed_tasks_do_not_use_luna(self):
        for task in ('멋지게 해줘', 'Make this beautiful', 'Cube를 이동하고 복잡한 rigging도 설계해',
                     'Cube를 이동하고 전체 도시를 멋지게 만들어'):
            self.assertNotEqual(self.route(task).model, 'luna')

    def test_simple_batch_and_material_property(self):
        for task in ('Duplicate Cube 100 times', 'Cube roughness를 0.5로 변경',
                     '현재 장면 저장', '렌더 실행', 'Cube를 숨겨', 'Cube 20개를 생성해서 원형으로 배치해'):
            self.assertEqual(self.route(task).model, 'luna', task)

    def test_features_set_minimum_sol_and_effort(self):
        for feature in ('geometry_nodes', 'rigging', 'python_generation'):
            result = self.route('작업', self.context(**{feature: True}))
            self.assertEqual((result.model, result.reasoning_effort), ('sol', 'high'))

    def test_context_scores_tool_calls_and_steps(self):
        result = self.route('작업', self.context(expected_tool_calls=5, step_count=10,
                                             scene_analysis=True, visual_review=True))
        self.assertEqual(result.score, 5)
        self.assertEqual(result.model, 'sol')
        self.assertEqual(self.route('작업', self.context(tool_call_count=15)).model, 'sol')

    def test_simple_never_auto_astra_even_with_failures(self):
        result = self.route('Cube를 X축으로 2m 이동', self.context(previous_failures=8,
                            sol_failures=3, mcp_error=True, tool_call_count=40))
        self.assertNotEqual(result.model, 'astra')

    def test_override_and_slash_command(self):
        self.assertEqual(self.route('/model astra\nCube 이동').model, 'astra')
        self.assertEqual(self.route('/model luna\n복잡한 rigging 설계').model, 'luna')
        self.assertEqual(self.route('Cube 이동', self.context(model_mode='sol')).model, 'sol')
        self.assertEqual(self.route('/model auto\nCube 이동', self.context(model_mode='astra')).model, 'luna')

    def test_bad_scorer_uses_sol_but_preserves_user_override(self):
        with patch('router.model_router.score_task', side_effect=RuntimeError('scorer bug')):
            self.assertEqual(self.route('Cube 이동').model, 'sol')
            self.assertEqual(self.route('/model luna\n작업').model, 'luna')

    def test_weights_and_thresholds_are_configurable(self):
        self.config['weights']['geometry_nodes'] = 8
        self.assertEqual(self.route('Geometry Nodes 울타리', config=self.config).model, 'astra')

    def test_custom_model_does_not_inherit_unverified_efforts(self):
        from router.config import load_config
        with patch.dict(os.environ, {'LUNA_MODEL': 'custom-model'}):
            custom = load_config()
        self.assertEqual(self.route('Cube 이동', config=custom).model_id, 'custom-model')
        self.assertIsNone(self.route('Cube 이동', config=custom).reasoning_effort)

    def test_config_rejects_unbounded_limits_and_invalid_effort(self):
        from router.config import validate_config
        for value in (0, -1, True, '2'):
            with self.subTest(value=value):
                config = {**self.config, 'limits': {**self.config['limits'], 'max_tool_calls': value}}
                with self.assertRaises(ValueError):
                    validate_config(config)
        self.config['models']['sol']['efforts']['normal'] = 'unsupported'
        with self.assertRaises(ValueError):
            validate_config(self.config)

    def test_malformed_config_sections_are_reported_as_validation_errors(self):
        import json
        import tempfile
        from router.config import load_config
        runtime = Path(__file__).resolve().parents[1] / '.runtime'
        runtime.mkdir(exist_ok=True)
        for changes in ([], {'models': []}, {'limits': None}, {'api': {'key_env': []}}):
            with self.subTest(changes=changes), tempfile.TemporaryDirectory(dir=runtime) as folder:
                path = Path(folder) / 'config.json'
                path.write_text(json.dumps(changes))
                with self.assertRaises(ValueError):
                    load_config(path)


if __name__ == '__main__':
    unittest.main()
