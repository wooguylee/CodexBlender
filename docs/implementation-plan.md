# Blender 제어 구현 계획

승인된 범위는 [design.md](design.md)를 따른다. 현재 비어 있는 프로젝트 폴더에서 직접 구현한다. Git 초기화·커밋·푸시는 사용자가 수행한다.

- [x] 1. 프로젝트 경계, 원자적 JSON 기록, OS 잠금, 세션별 작업 처리의 동작 테스트를 먼저 작성하고 실패 확인.
- [x] 2. `bridge/common.py`에 공통 파일/잠금 도구, `bridge/client.py`에 doctor/start/status/scene/run/preview/save/stop CLI, `bridge/worker.py`에 Blender 타이머와 저장/미리보기 실행 구현.
- [x] 3. `scripts/blender.ps1`과 `Start-Blender.cmd`에 경로 탐색/내장 Python 실행. `workflows/`에 기본 시연 및 수정 코드.
- [x] 4. 실제 GUI에서 상태→시연→수정 검증. 독립된 실제 Blender 백그라운드 프로세스에서 오류→복구→종료/재연결 및 한글/공백 경로 이식 확인.
- [x] 5. 한국어 README, AGENTS.md, Git 제외 정책, 실제 검증 보고서와 결과물 저장. 최종 장면과 미리보기 확인. 코드 검토의 한글 설정/완료 순서 문제는 실패 재현 후 수정하고 6개 테스트 통과.

검증 명령: `python -m unittest discover -s tests -v`, `powershell -NoProfile -ExecutionPolicy Bypass -File scripts/blender.ps1 doctor`, 같은 실행기로 `start`, `scene`, `run --script workflows/demo_scene.py`, `run --script workflows/demo_adjust.py`, `preview`, `stop`.
