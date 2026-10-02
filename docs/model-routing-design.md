# Model Auto Routing 설계

2026-10-02. 사용자 첨부 요청서의 22개 항목을 구현 기준으로 한다.

## 현재 구조와 삽입 위치

현재 흐름은 Codex → `scripts/blender.ps1` → `bridge/client.py` → 프로젝트 파일 큐
→ `bridge/worker.py` → bpy다. 프로젝트에는 LLM API 호출이나 MCP 서버가 없다.
따라서 기존 worker/CLI/schema를 변경하지 않고 별도 Python 실행 계층을 추가한다.

새 흐름은 `python -m router route|run|chat` → 규칙 기반 router → Responses API
→ 제한된 브리찌 adapter → 기존 CLI다. 모델 API와 도구 실행 인터페이스를 분리해
향후 Codex 또는 실제 MCP client를 교체 연결할 수 있게 한다.
현재 Codex 앱 대화의 모델을 바꾸거나 기존 대화를 가로채는 기능은 아니다.

기존 CLI에 routing을 넣으면 자연어/실행 도구의 책임이 섞인다. Codex CLI를 하위
에이전트로 실행하면 개별 도구 호출의 제한과 미완료 작업 통제가 어려워진다.
독립 Responses 실행 계층을 선택하며 Python 표준 라이브러리만 사용한다.

## 결정 정책

- `route_task(task, context, config)`는 tier, effort, score, reasons를 반환한다.
- 한국어/영어 특징 추출 + 명시적 context. 가중치/문턱/예산/모델 ID는 JSON 설정.
- 명확한 단순 작업만 Luna. 불확실하거나 모델링/노드/Python 작업이면 최소 Sol.
- 기본 점수 0–2 Luna, 3–6 Sol, 7 이상 Astra. 고난도 분석/설계는 별도 후보.
- 단순 작업은 실패 이력이 쌓여도 자동 Astra 금지. 명시적 모델 지정은 우선한다.
- Luna low, Sol medium 또는 high, Astra high 또는 디버깅 xhigh. 지원 effort는 모델
  설정에서 검사하고, 알 수 없는 모델 ID로 바꿀 때 effort capability를 재설정한다.
- scorer 오류는 Sol로 fail-safe. 손상된 실행 예산/설정은 실행 전에 명확히 오류 처리.

## 실행 및 실패 처리

- 요청마다 독립 state와 UUID. 시도/실패/실제 도구 호출/모델 호출/승급/토큰 통계 기록.
- 도구 성공 후에도 동일 시도를 이어가며, 오류 발생 시 원인에 따라 재계획한다.
- 객체 이름/인수/일시적 통신 오류는 같은 모델에서 수정 기회. 반복 Luna 실패는 Sol.
- Sol의 계획/코드/목표 불일치가 2회 누적되면 Astra 후보. 인프라 오류만으로 Astra 금지.
- 강제 모델은 도구 오류로 바꾸지 않는다. 모델 이용 불가인 경우만 설정된 fallback.
- 재시도/승급/모델 호출/도구 호출/동일 오류/동일 도구 반복의 상한을 실행 전에 검사.
- Blender pending/알 수 없는 실행 상태는 즉시 pending 종료. 원본 변경을 재전송하지
  않는다. `inspect-job`으로 result 및 큐 퇴역 여부를 확인한다.
- 변경 실패는 부분 적용 가능성이 있으므로 scene 재조회 전 다음 변경을 허용하지 않는다.
- 성공한 동일 변경을 같은 요청 안에서 다시 실행하지 않는다.
- 모델 변경 시 목표, 실제 도구 결과, 오류와 현재 상태를 전달한다. 전체 요청 재실행 금지.

## 경계 및 검증

실행 시 API 키를 환경변수에서 읽는다. 키/토큰/인증 파일을 기록하지 않는다.
기본 로그는 결정/해시/집계만 보존하고 debug는 요청/도구 상세를 추가한다.
모델 출력은 실행 권한을 확대하지 않는다. adapter는 프로젝트 경로와 도구 schema를
검사하지만 기존 임의 bpy Python은 보안 sandbox가 아니다.

`run`은 현재 브리찌 연결을 사용한다. start/stop/외부 업로드/설치는 모델 도구에 제공하지
않는다. 스크립트는 `workflows/model-routing/<task-id>/`에 보존하고 기본 백업/저장/렌더를
유지한다. PNG가 반환되면 모델에게 이미지로 전달해 결과 확인에 사용한다.

기존 6개 회귀 테스트를 기준으로 scorer 7개 요청 사례, 승급 2개 사례, 실행 한도,
미완료/부분 변경, override/fallback, HTTP payload, 통계, 실제 Blender 독립 사본을 검증한다.
실제 유료 LLM 호출은 이 구현 검증에 포함하지 않는다.

공식 API 확인: [모델 및 effort](https://developers.openai.com/api/docs/guides/latest-model),
[function calling](https://developers.openai.com/api/docs/guides/function-calling),
[reasoning](https://developers.openai.com/api/docs/guides/reasoning).
