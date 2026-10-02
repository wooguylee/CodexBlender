"""Pure routing decisions; no Blender or network dependency."""
import re

from .complexity import score_task, TECHNICAL
from .config import load_config
from .types import MODEL_TIERS, RoutingContext, RoutingDecision


def parse_model_command(task, mode='auto'):
    match = re.match(r'^\s*/model\s+(\S+)(?:\s+|$)', task, re.I)
    if match:
        mode = match[1].lower()
        task = task[match.end():].strip()
    if mode not in ('auto', *MODEL_TIERS):
        raise ValueError('Model mode must be auto, luna, sol or astra')
    return task, mode


def decision_for(tier, score, reasons, config, *, simple=False, eligible=False,
                 manual=False, technical=False, debugging=False):
    model = config['models'][tier]
    profile = 'debugging' if debugging else 'technical' if technical else 'normal'
    effort = model['efforts'][profile]
    if effort not in model['supported_efforts']:
        effort = None
    return RoutingDecision(tier, model['id'], effort, score, reasons, simple, eligible, manual)


def route_task(task, context=None, config=None):
    config = config if config is not None else load_config()
    context = context if context is not None else RoutingContext(model_mode=config['model_mode'])
    task, mode = parse_model_command(task, context.model_mode)
    if not isinstance(task, str) or not task.strip():
        raise ValueError('A non-empty Blender task is required')
    manual = mode != 'auto'
    try:
        complexity = score_task(task, context, config)
        score, reasons = complexity.score, list(complexity.reasons)
        simple = complexity.simple
        eligible = not simple and (score >= config['thresholds']['astra'] or
                                   complexity.high_difficulty or context.sol_failures >= 2)
        if manual:
            tier = mode
            reasons.append('사용자 모델 지정 우선')
        elif eligible:
            tier = 'astra'
            reasons.append('높은 복잡도/고난도 분석 또는 Sol 실패 누적')
        elif simple and score < config['thresholds']['sol']:
            tier = 'luna'
            reasons.append('명확한 단순 작업')
        else:
            tier = 'sol'
            reasons.append('일반/불확실/다단계 작업의 기본 모델')
        return decision_for(tier, score, reasons, config, simple=simple, eligible=eligible, manual=manual,
                            technical=any(complexity.features[k] for k in ('geometry_nodes', 'rigging', 'python_generation')),
                            debugging=complexity.features['debugging'])
    except Exception as error:
        return decision_for(mode if manual else 'sol', 0,
                            [f'Router fail-safe: {type(error).__name__}', '사용자 지정 유지' if manual else '기본 Sol 사용'],
                            config, manual=manual)


# Public alias for hosts following the request's language-neutral interface.
routeTask = route_task
