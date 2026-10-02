# Model Auto Routing 사용법과 구현 결과

2026-10-02. 기존 브리찌 위에 추가한 독립 모델 선택/실행 계층이다.

## 기존 구조와 새 실행 경로

기존: Codex → `scripts/blender.ps1` → `bridge/client.py` → 파일 큐 → `bridge/worker.py` → bpy.
이 저장소에는 MCP 서버나 자체 LLM 호출 코드가 없었다. 기존 구조/명령/요청 schema는 유지했다.

추가: 자연어 CLI → `router` → `llm/ResponsesClient` → `adapters/BlenderTools` → 기존 CLI.
라우터는 Blender 구현을 모른다. `TaskExecutor`에 다른 model client/tool adapter를 주입할 수 있다.
현재 Codex 앱 대화의 모델을 자동 변경하는 기능은 아니며, 아래 새 진입점으로 실행할 때 적용된다.

## 빠른 사용

저장소 루트에서 Python 3.11+로 실행한다. pip 설치는 필요 없다. 별도 Python이 없으면
Blender 설치 폴더의 `<버전>/python/bin/python.exe`로 `python`을 대체한다.

```powershell
# 모델 판단만 확인: API 키/네트워크/Blender 변경 없음
python -m router route "Cube를 X축으로 2m 이동"
python -m router route "책상 모델을 만들고 Bevel과 Subdivision을 적용해"
python -m router route "현재 Scene 전체 구조를 분석해서 성능이 느린 이유를 찾고 최적화해"

# 명시적 모델 지정과 실행 추정치
python -m router route "Geometry Nodes로 절차적 울타리를 만들어" --model sol
python -m router route "장면 작업" --context '{"step_count":12,"python_generation":true}'
python -m router route "/model astra Cube 이동"
```

실제 실행은 API 키와 연결된 Blender가 필요하다. 이 경로는 OpenAI API를 호출하므로
사용자 요청과 도구 결과/PNG가 해당 API로 전송되고 API 사용량이 발생한다.
Codex 로그인 자격 증명이나 Codex의 현재 모델 설정을 가져오지 않는다.

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File scripts/blender.ps1 start
# OPENAI_API_KEY 환경변수를 자신의 환경에서 설정한 뒤
python -m router run "Cube를 X축으로 2m 이동"
python -m router run "책상 모델을 만들고 Bevel을 적용해" --model sol
```

현재 제작 Scene에는 Cube가 없을 수 있다. `run` 모델은 `scene`을 조회해 실제 이름을
확인해야 하며, 위 Cube 명령은 기본 Cube가 있는 테스트 Scene의 예시다.

```powershell
# 대화형 선택 테스트 또는 실제 실행
python -m router chat --dry-run
python -m router chat
```

대화형 입력에서 `/model luna`, `/model sol`, `/model astra`, `/model auto`를 사용한다.
선택은 해당 프로세스의 이후 요청에 유지된다. `/quit`으로 종료한다. 요청마다 실행 상태와
예산은 새로 만들며 이전 대화 전체를 자동 이월하지 않는다. 강제 지정 우선순위는
요청의 `/model` → `--model` → context `model_mode`/`modelMode` → config `model_mode`다.

## 판단과 reasoning effort

| 조건 | 기본 모델 / effort |
|---|---|
| 명확한 이동·회전·이름·복사·숨김·저장·렌더·동일 반복, 점수 0–2 | Luna / low |
| 일반 모델링·노드·Modifier·애니메이션·불확실한 요청, 일반 점수 3–6 | Sol / medium |
| Geometry Nodes·Rigging·Blender Python 생성 | 최소 Sol / high |
| 점수 7 이상 또는 전체 Scene 설계/분석, 복잡한 노드 문제 분석 | Astra / high |
| 고난도 오류 분석 또는 Sol 논리 오류 누적 | Astra / xhigh |

점수만 낮다고 Luna를 선택하지 않는다. 단순 작업임이 명확하지 않으면 Sol이 기본이다.
반복 개수 자체로 가중하지 않으며, 단순 작업은 실패가 쌓여도 자동 Astra로 보내지 않는다.
사용자가 명시적으로 `/model astra`를 지정한 경우는 사용자 선택을 우선한다.
자연어 추출은 한국어/영어 규칙 기반이며 문맥을 완전히 이해하는 분류기는 아니다.
필요한 경우 `RoutingContext`의 추정치/특징 boolean 또는 강제 모델로 보완한다.
단순 변환을 adapter에서 Python으로 표현하는 것 자체는 복잡한 Python 생성으로 가중하지 않는다.

`route_task(task, context=None, config=None)`와 별칭 `routeTask`는
`RoutingDecision(model, model_id, reasoning_effort, score, reasons, ...)`를 반환한다.
context에는 예상/기존 tool 호출, 단계 수, Python, 노드, 리깅, 애니메이션, Modifier,
장면 분석, 이미지 확인, 수학, 전체 Scene, 실패 횟수, Sol 실패, MCP 오류, 단순 반복,
사용자 모델 선택을 전달할 수 있다. `tool_call_count`는 실행 예산의 이미 사용된 횟수에도 반영한다.

모델 ID와 지원 effort는 [공식 모델 가이드](https://developers.openai.com/api/docs/guides/latest-model)를
확인해 기본 설정에 반영했다. 실제 계정의 모델 접근권은 별개다.
함수 호출은 [Responses API](https://developers.openai.com/api/docs/guides/function-calling)를 사용한다.
동일 모델의 이어지는 요청에는 output/함수 결과/reasoning 항목을 보존한다.
모델 변경 때는 목표와 실제 실행 기록을 인계하고 모델 내부 reasoning은 이월하지 않는다.

## 재시도·승급과 중복 실행 보호

- 객체 이름·인수·일시적 통신 오류: 동일 모델이 원인을 수정해 재시도한다.
- Luna 실패 2회: Sol로 승급. Sol 계획/코드/상태/목표 오류 2회: 복잡한 작업이면 Astra.
- 인프라 오류만 반복된 Sol은 Astra로 승급하지 않고 재시도 한도에서 종료한다.
- 강제 모델은 도구 실패로 바꾸지 않는다. 모델 이용 불가 오류만 설정된 fallback을 허용한다.
  인증·잘못된 API 인수·quota 오류는 명확히 종료한다.
- 기본 최대 재시도는 모델별 2회(최초 포함 3시도), 모델 변경 최대 2회,
  Blender 도구 최대 50회, 모델 API 최대 30회다.
- 동일 오류 최대 4회, 동일 tool+인수는 모델별 최대 2회. 성공하거나 부분 적용될 수 있는
  같은 변경 코드는 같은 요청에서 다시 실행하지 않는다. Python 공백/주석/label 변경으로
  보호를 우회할 수 없도록 AST를 기준으로 비교한다.
- worker timeout, 응답 유실, 진행 여부 불명확은 `pending`으로 종료한다. 자동 재전송하지 않는다.
- 부분 변경 실패 후에는 실제 `scene` 조회가 필요하다. 코드 수정 성공 없이 조회/저장만으로
  미해결 실패를 완료로 처리하지 않는다.
- `.blend`와 snapshot 저장 뒤 preview만 실패하면 이미 실행한 코드를 보호하고,
  `scene` → `preview` 확인으로 복구할 수 있다.
- 실패한 함수/작업의 실제 결과를 모델에 전달한다. 완료에는 성공한 도구 실행 증거가 필요하며,
  빈 응답/중단 응답/미해결 오류를 성공으로 표시하지 않는다.

미완료 작업은 결과의 Blender job ID로 조회한다.

```powershell
python -m router inspect-job 20261002T000000-0123456789
```

`result.json`이 생겼어도 queue/working에서 퇴역할 때까지 pending이다.
ID가 유실된 경우 기존 `status`의 worker job과 `outputs/jobs/`를 먼저 확인한다.
프로세스 재시작 후 자동 재개/재전송은 제공하지 않는다.
CLI 종료 코드는 성공 0, 실패 1, pending 2다. `chat`은 각 입력에 JSON 결과를 출력한다.

## 설정

기본값은 `router/config.json`. 부분 덮어쓰기 JSON을 프로젝트 안에 만들고 `--config`로 지정한다.

```json
{
  "model_mode": "auto",
  "weights": {"geometry_nodes": 3},
  "thresholds": {"sol": 3, "astra": 8},
  "limits": {"max_retries_per_model": 2, "max_escalations": 2, "max_tool_calls": 40},
  "logging": {"debug": false}
}
```

```powershell
python -m router route "Geometry Nodes 울타리" --config router.local.json
```

실제 모델 ID는 `models.luna/sol/astra.id` 또는 `LUNA_MODEL`, `SOL_MODEL`, `ASTRA_MODEL`
환경변수로 설정한다. 기본값은 각각 `gpt-6-luna`, `gpt-6.1-sol`, `gpt-6-astra`.
알 수 없는 ID로 바꾸면 이전 모델의 effort 지원을 추측하지 않고 reasoning 필드를 생략한다.
지원이 확인된 경우 해당 모델의 `supported_efforts`와 `efforts.normal/technical/debugging`를 함께
설정하거나 `LUNA_MODEL_EFFORTS` 등 환경변수에 JSON 배열을 지정한다.
지원 목록 밖의 effort, 잘못된 설정 구조, 음수/무제한 실행 예산은 실행 전에 거부한다.

API 키는 `api.key_env`(기본 `OPENAI_API_KEY`) 환경변수에서만 읽는다.
`api.base_url`, API/브리찌 timeout, 스크립트/이미지 최대 크기도 설정 가능하다.
키를 설정 JSON, Git, 로그에 기록하지 않는다. API 에러 본문은 로그로 내보내지 않는다.
scorer 내부 오류는 Sol로 fail-safe하고 명시적 사용자 모델은 유지한다.
손상된 실행 설정까지 무시해 무제한으로 실행하지는 않는다.

## 파일과 로그

추가 파일:

| 경로 | 역할 |
|---|---|
| `router/types.py` | 요청 특징, routing 결정, 실행 상태/결과 |
| `router/config.json`, `router/config.py` | 기본값, 환경변수, 부분 config 병합/검증 |
| `router/complexity.py`, `router/model_router.py` | 특징/점수와 모델/effort 선택 |
| `router/escalation.py` | 실패 유형과 retry/escalation/fallback 정책 |
| `router/executor.py` | 순차 tool loop, 예산, 중복/미완료/부분 변경 보호 |
| `router/audit.py` | JSONL 로그, 모델별 통계 |
| `router/cli.py`, `router/__main__.py`, `router/__init__.py` | route/run/chat/inspect-job 진입점 |
| `llm/client.py`, `llm/__init__.py` | Responses HTTP/오류/응답 검증 |
| `adapters/blender.py`, `adapters/__init__.py` | 기존 CLI 호출, 워크플로 보존, 이미지 전달 |
| `tests/test_routing.py`, `tests/test_execution.py` | 순수 정책과 실행 상태 테스트 |
| `tests/test_adapters.py`, `tests/test_router_cli.py`, `tests/test_router_live.py` | API/adapter/CLI/실제 Blender 회귀 |
| `docs/model-routing-design.md`, `docs/model-routing-plan.md`, 이 문서 | 설계·계획·사용법/보고 |

기존 파일 수정: README의 진입 안내, `docs/current-state.md`의 최신 상태 추가.
`bridge/`, `scripts/blender.ps1`, 기존 테스트와 설정은 변경하지 않았다.

실행 코드는 `workflows/model-routing/<task-id>/operation-<hash>.py`에 보존한다.
기존 Blender job의 코드 사본/백업/원본/snapshot/미리보기는 기존 위치를 유지한다.
`outputs/router/<task-id>/events.jsonl`에는 결정/근거/승급/호출 해시/Blender job ID와 결과 경로,
`result.json`에는 상태/원인/예산/통계를 기록한다. `--debug`는 요청/도구 인수/결과 상세를 추가한다.

통계는 모델별 호출·시도·성공/실패·tool 평균·승급·입력/캐시/출력/reasoning token을 포함한다.
성공률/실패율은 성공 또는 실패 판정된 시도 기준이며 pending/한도 중단은 성공으로 집계하지 않는다.
예상 비용은 `models.<tier>.pricing_per_million`의 `input`, `cached_input`, `output` 단가를
직접 설정한 경우만 산출한다. 기본값은 `null`이며 가격을 추측하지 않는다.
장문/캐시 쓰기/추가 요금 등 계정별 실제 청구를 대체하는 계산은 아니다.

## 검증과 남은 범위

최종 결과: **58개 테스트 전부 통과, skip 없음**. `BLENDER_E2E=1` 전체 실행은 13.428초.
요청서 1–7의 모델 선택과 8–9의 승급, override/fallback, 예산, 반복, 인코딩,
pending/부분 변경/저장 후 렌더 오류, API payload, 기존 브리찌 실제 회귀를 포함한다.
전체 로그: `outputs/verification/model-routing-tests.log`.
기존 회귀 결과의 이번 실행본: `outputs/verification/model-routing-portable-smoke.json`.
새 adapter 실제 검증: `outputs/verification/router-smoke.json`, `router-preview.png`.

```powershell
python -m unittest discover -s tests -v
$env:BLENDER_E2E = '1'
python -m unittest discover -s tests -v
Remove-Item Env:BLENDER_E2E
```

Windows / Blender 5.2.1 LTS에서 검증했다. E2E는 `.runtime/`의 독립 한글/공백 경로 사본을
사용하므로 현재 `Rainy_Cafe_v002` 제작 장면을 수정하지 않는다.
실제 모델 대신 준비된 함수 호출 응답을 넣고 실제 CLI/파일 큐/bpy/렌더/이미지 전달을 검증한다.
미리보기도 직접 확인했다. 실제 유료 API 호출, 계정별 접근권, 다른 OS/GPU는 검증하지 않았다.

후속 개선: 실제 요청 로그로 한국어/영어 분류 정확도 평가, 작업 단계별 역할 분배,
실제 MCP/Codex model client adapter, 승인된 계정으로 실서비스 모델 통합 평가,
중단 작업의 명시적 재개와 집계 통계 대시보드. 현재 임의 bpy Python은 기존과 같이
사용자 계정 권한으로 실행되며 adapter 경로 검사가 Python 자체의 sandbox는 아니다.
