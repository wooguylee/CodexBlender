"""Conservative bilingual feature extraction; context can supply planner estimates."""
import re
from dataclasses import dataclass

from .types import RoutingContext

PATTERNS = {
    'geometry_nodes': r'geometry\s*nodes?|지오메트리\s*노드',
    'shader_nodes': r'shader|bsdf|noise\s*texture|셰이더|쉐이더|재질.*만들|material.*creat',
    'rigging': r'rigging|\brig\b|리깅|리그|뼈대',
    'animation': r'animation|keyframe|애니메이션|키프레임',
    'modifiers': r'modifier|bevel|subdivision|모디파이어|베벨|서브디비',
    'python_generation': r'python|파이썬|스크립트.*작성|코드.*작성',
    'scene_analysis': r'분석|원인|진단|analy[sz]|diagnos|inspect.*scene',
    'visual_review': r'보고.*판단|결과.*확인|이미지.*확인|viewport.*review|visual.*review',
    'complex_math': r'수학|행렬|좌표.*계산|trigonometry|matrix|coordinate.*calcul',
    'whole_scene': r'(scene|장면).*전체.*(구조|설계|분석)|전체.*(scene|장면).*(설계|분석)|whole\s+scene.*(design|analy)|entire\s+scene',
    'debugging': r'오류|실패|버그|원인|사라진|느린.*이유|debug|bug|fail|disappear|wrong|slow',
    'material_property': r'roughness|metallic|거칠기|금속성|색상|색깔|색을|base.?color',
    'simple_repeat': r'반복|모두|선택된\s*\d+|\d+\s*개|\d+\s+times|batch|all\s+objects',
}
SIMPLE = r'이동|회전|크기|스케일|이름|삭제|복사|숨겨|숨기|보이게|저장|내보내|렌더.*실행|원형.*배치|\b(move|rotate|scale|rename|delete|duplicate|visibility|hide|save|export|render)\b'
CREATIVE = r'만들|설계|모델링|구성|최적화|도시|추상|복잡|멋지|아름|\b(modeling|create|design|build|complex|beautiful|optimi[sz]e)\b'
TECHNICAL = ('geometry_nodes', 'shader_nodes', 'rigging', 'animation', 'modifiers', 'python_generation')


@dataclass
class Complexity:
    score: int
    reasons: list[str]
    features: dict
    simple: bool
    high_difficulty: bool


def score_task(task, context: RoutingContext, config):
    text = task.lower()
    features = {key: bool(re.search(pattern, text, re.I)) for key, pattern in PATTERNS.items()}
    for key in features:
        explicit = getattr(context, key, None)
        if explicit is not None:
            features[key] = bool(explicit)
    features['many_tools'] = max(context.expected_tool_calls, context.tool_call_count) >= config['thresholds']['many_tools']
    features['long_task'] = context.step_count >= config['thresholds']['long_task']
    features['one_failure'] = context.previous_failures == 1
    features['repeated_failures'] = context.previous_failures >= 2
    features['mcp_error'] = context.mcp_error
    creative = bool(re.search(CREATIVE, text, re.I))
    # A specified circular batch is a known operation rather than arbitrary modeling.
    circular_batch = bool(re.search(r'\d+\s*개.*원형.*배치', text))
    simple = bool(re.search(SIMPLE, text, re.I) or features['material_property'] or circular_batch)
    simple = simple and (not creative or circular_batch) and not any(features[k] for k in TECHNICAL)
    simple = simple and not (features['whole_scene'] or features['scene_analysis'] or features['visual_review'])
    if context.simple is not None:
        simple = context.simple and not any(features[k] for k in TECHNICAL)
    high = features['whole_scene'] or (features['debugging'] and features['scene_analysis'] and any(features[k] for k in TECHNICAL))
    if context.high_difficulty is not None:
        high = context.high_difficulty
    reasons = []
    score = 0
    for feature, weight in config['weights'].items():
        if features.get(feature):
            score += weight
            reasons.append(f'{feature}: +{weight}')
    if features['simple_repeat']:
        reasons.append('단순 반복은 오브젝트 개수만으로 가중하지 않음')
    return Complexity(score, reasons, features, simple, high)
