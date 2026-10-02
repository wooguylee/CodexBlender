# Model Auto Routing Implementation Plan

> 실행: 이 세션에서 직접 구현. 사용자가 지정한 최소 변경/별도 에이전트 기본 사용 금지/
> 작업 범위를 유지한다. 후속 사용자 지시로 검증 후 커밋·푸시까지 수행한다. 설계: `docs/model-routing-design.md`.

**Goal:** 요청 단위 모델 선택, 제한된 재시도와 승급, 실제 브리찌 실행을 독립 계층으로 제공.
**Architecture:** router → llm/client → adapters/blender → 변경 없는 bridge/client.
**Tech Stack:** Python 3.11+, 표준 라이브러리, JSON, unittest, OpenAI Responses.

## Global Constraints

- 기존 도구 이름/schema/Python 실행 방식/설정 파일 보존. 새 dependency 없음.
- 모든 생성 파일은 프로젝트 내부. 현재 제작 Scene은 회귀 검증으로 변경하지 않는다.
- timeout/pending은 재시도하지 않고 명시적 결과 확인. 설정은 비밀키를 포함하지 않는다.

## Review Focus

- 한국어 단순 명령에 복잡한 조건이 섞였을 때 Luna 오분류.
- 변경 실행 후 응답 유실 시 중복 실행.
- 강제 모델의 도구 실패와 모델 이용 불가의 구분.
- 승급 시 기존 결과/오류 전달 및 전체 예산 유지.
- JSON 오류/알 수 없는 tool/경로 탈출/과다 호출에서 잘못된 완료 보고.

## Task 1: 설정과 순수 routing

- [x] `tests/test_routing.py`: 요청서 1–7, uncertain, context, override, scorer fail-safe,
  설정 변경/effort capability 실패 테스트 작성 → 미구현 실패 확인.
- [x] `router/types.py`, `config.py`, `complexity.py`, `model_router.py`, `config.json` 구현.
  인터페이스: `route_task(str, RoutingContext | None, dict | None) -> RoutingDecision`.
- [x] `python -m unittest discover -s tests -v` → 새/기존 단위 테스트 통과.

## Task 2: 실행 상태와 실패 정책

- [x] `tests/test_execution.py`: Luna 반복→Sol, Sol 논리 오류 2회→Astra, transient 유지,
  override 유지, 모델 fallback, 모든 budget, pending, partial, 통계/상태 테스트 → 실패 확인.
- [x] `router/escalation.py`, `executor.py`, `audit.py` 구현.
  인터페이스: `TaskExecutor(client, tools, config).execute(task, context) -> ExecutionResult`.
  외부 부작용 경계만 fixture로 대체하고 실제 상태 머신을 검증.
- [x] 전체 단위 테스트 통과 확인.

## Task 3: API 및 브리찌 연결과 진입점

- [x] `tests/test_adapters.py`, `test_router_cli.py`, `test_router_live.py`에 payload,
  로컬 스크립트 보존, 실패/timeout, 이미지, CLI, 실제 독립 Blender roundtrip 테스트 작성.
- [x] `llm/client.py`, `adapters/blender.py`, `router/cli.py`, `router/__main__.py` 구현.
  HTTP 자체는 단위 테스트에서 대체, CLI/파일 처리는 실제 실행.
- [x] `BLENDER_E2E=1` 전체 테스트 실행. 실제 PNG 확인 및 기존 파일 변경 여부 확인.
- [x] `docs/model-routing.md`, README, current-state 갱신. 미검증 API 범위와 사용법 보고.

## 검증 기록

- 시작 기준: 기존 테스트 6개, 5개 통과/실제 Blender 1개 opt-in skip.
- `doctor`: Blender 5.2.1 LTS, Python 3.13.13; GUI 연결 시작 후 `scene` 조회 성공.
- 현재 Scene `Rainy_Cafe_v002`, 카메라 `RCE_Camera`. 제작물은 변경하지 않는다.
- 순수 routing 11개 및 실행 상태 17개를 각각 미구현 실패 확인 후 구현했다.
- 실제 Windows 테스트로 짧은/긴 경로 표현 차이와 stdin 한국어 인코딩 문제를 찾아 수정했다.
- 최종 검토로 코드 공백/label 변경 재실행, preview 실패의 예외 누락, 설정 기본 모델 우선순위,
  저장 완료 후 렌더 실패, 부분 적용 재실행, 잘못된 config/API 응답, 기존 호출 예산 누락을
  각각 실패 테스트로 재현하고 수정했다.
- 최종 전체 검증: `BLENDER_E2E=1 python -m unittest discover -s tests -v` → **58/58 통과**, 13.428초.
- 실제 Blender 회귀/새 router 연동은 독립 사본에서 실행했고 PNG를 직접 확인했다.
- 로그: `outputs/verification/model-routing-tests.log`, 기존 회귀 이번 결과:
  `outputs/verification/model-routing-portable-smoke.json`. 이전 portable-smoke 기록은 Git 내용과 Windows 줄바꿈으로 복원했다.
- 작업 시작/종료 실제 Scene JSON 비교: `Rainy_Cafe_v002`, `RCE_Camera`, 1,892개 객체가 완전히 동일.
  기록: `outputs/verification/model-routing-preservation.json`.
- 프로젝트 사용자 지침에 따라 기존 작업 디렉터리에서 직접 구현/검토했다.
  기존 제작물·사용자 변경을 보존하고 별도 에이전트·실제 유료 API 호출은 수행하지 않았다.
- 2026-10-02 후속 사용자 지시: 모든 작업의 마무리는 커밋·푸시. 이번 구현과 해당 상시 규칙을
  함께 반영하며, 프로젝트 지침·메모리를 갱신하고 푸시 후 로컬/원격 해시 일치를 확인한다.
- 커밋 직전 일반 회귀: 58개 실행, 56개 통과/실제 Blender opt-in 2개 skip. 실제 Blender를
  포함한 전체 58개 통과 결과는 위 최초 구현 검증 기록을 유지한다.
