"""Failure classification and bounded model changes, separate from execution."""
from dataclasses import dataclass
import re


SUBSTANTIVE = {'plan', 'tool_selection', 'python', 'state', 'geometry', 'goal', 'unknown'}


def classify_error(message):
    text = message.lower()
    patterns = (
        ('object', r'object.*not found|wrong object name|객체.*없|keyerror.*bpy'),
        ('parameter', r'parameter|argument|json|인수|매개변수'),
        ('transient', r'temporary|temporarily|timeout|timed out|일시|connection|http 429|http 5'),
        ('python', r'python|syntaxerror|nameerror|typeerror|attributeerror|indentationerror'),
        ('geometry', r'geometry|지오메트리'),
        ('state', r'state|상태'),
        ('plan', r'plan|계획'),
        ('goal', r'goal|목표'),
    )
    return next((kind for kind, pattern in patterns if re.search(pattern, text)), 'unknown')


@dataclass
class Recovery:
    action: str
    model: str | None
    reason: str
    kind: str = 'escalation'


def recovery_for(state, decision, error_kind, config, unavailable_models):
    tier = state.selected_model
    limits, policy = config['limits'], config['escalation']
    if error_kind == 'fatal':
        return Recovery('stop', None, '모델 인증/설정 오류')
    if error_kind == 'unavailable':
        if policy['allow_model_fallback']:
            for candidate in policy['fallback_order']:
                if candidate != tier and candidate not in unavailable_models and not (decision.simple and candidate == 'astra'):
                    if len(state.escalation_history) >= limits['max_escalations']:
                        break
                    return Recovery('switch', candidate, '모델 호출 이용 불가', 'fallback')
        return Recovery('stop', None, '사용 가능한 모델 fallback 없음')
    target = None
    if not decision.manual:
        if tier == 'luna' and state.failures_by_model[tier] >= policy['luna_failures']:
            target = 'sol'
        elif (tier == 'sol' and not decision.simple and error_kind in SUBSTANTIVE and
              state.substantive_failures[tier] >= policy['sol_substantive_failures']):
            target = 'astra'
    if target:
        if target in unavailable_models or len(state.escalation_history) >= limits['max_escalations']:
            return Recovery('stop', None, '승급 한도 또는 모델 이용 불가')
        return Recovery('switch', target, f'{tier} 반복 실패; 원인={error_kind}')
    if state.failures_by_model[tier] > limits['max_retries_per_model']:
        return Recovery('stop', None, '모델별 재시도 한도')
    return Recovery('retry', tier, f'동일 모델에서 원인 수정: {error_kind}')
