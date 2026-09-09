# 검증 기록

검증일: 2026-09-09. 환경: Windows, Blender 5.2.1 LTS, Blender 내장 Python 3.13.13 / 테스트 실행 Python 3.14.

## 자동 검증

`python -m unittest discover -s tests -v`: 파일/잠금/명령 완료 테스트 5개 통과. 실제 Blender 테스트는 `BLENDER_E2E=1`을 지정하여 실행한다.

`$env:BLENDER_E2E='1'; python -m unittest discover -s tests -v`: 6개 테스트 모두 통과.

- 프로젝트 바깥 경로와 심볼릭 링크를 통한 경계 이탈 거부.
- 한글 JSON 원자적 교체와 임시 파일 정리.
- 두 번째 잠금 소유자 거부, 잠금 해제 후 재사용.
- 완료 JSON이 먼저 기록되더라도 실제 작업 파일 정리와 stop 잠금 해제까지 기다리는 회귀 테스트. 수정 전 scene/stop 두 경우의 실패를 재현했다.
- `.runtime/clone space 한글 <임의ID>/`로 도구를 복사한 경로에서 실제 Blender 백그라운드 실행.
- 중복 start 시 같은 연결 반환.
- Windows PowerShell 5.1 실행기와 UTF-8 로컬 설정의 한글 Blender 설치 경로 검증. 실제 설치 폴더를 가리키는 한글 경로 링크로 수정 전 실패를 재현했다.
- 프로젝트 코드 실행, 실행 전 백업, 현재 원본과 미리보기 생성.
- 의도적 Python 오류 기록과 백업 보존, 이후 정상 조회.
- 짧은 대기 제한 후 pending 응답, 실행 중 재전송 거부, 기존 작업의 정상 완료.
- 명시적 save와 덮어쓰기 전 파일 백업.
- stop 후 연결 해제, 새로운 세션으로 재시작 후 저장된 객체 복원.

요약 JSON: `outputs/verification/portable-smoke.json`. 테스트 실행 기록과 실제 작업 데이터는 `.runtime/`의 해당 사본 안에 남으며 Git에는 포함하지 않는다. 복제 테스트는 같은 PC에서 경로를 바꾸어 수행했으며 실제 다른 PC에 Git clone한 검증은 아니다.

## GUI와 실제 이미지

- `scripts/blender.ps1 doctor`: 실제 설치 경로와 5.2.1 LTS 확인.
- `scripts/blender.ps1 start`: GUI 모드(`background: false`) 연결 성공. 기존 실행 중인 Blender 프로세스는 유지하고 별도 프로젝트 창 생성.
- Windows 프로세스의 창 제목에서 `scenes/current.blend` 열린 상태 확인.
- `run --script workflows/demo_scene.py`: 약 16.67초, 파란 물체/받침대/카메라/조명 생성 및 960×720 PNG 확인.
- `run --script workflows/demo_adjust.py`: 약 3.854초, 주황색 변경 및 높이 증가 PNG 확인.
- `scene`: `Demo_Hero`의 Z 크기 약 2.24, `Demo_Camera`, Cycles 장면 확인.
- `Start-Blender.cmd`: 기존 연결 재사용 확인.
- 두 PNG를 이미지 도구로 직접 열어 형상, 색, 카메라 구도, 텍스트를 확인했다.

원본 이미지와 실제 결과 JSON은 `outputs/jobs/`에 보존되어 있다. 비교용 이미지 사본은 `outputs/demo/`에 있다. 시간은 이 PC의 이번 실행 결과이며 다른 PC의 속도 보장이 아니다.

## 검증 범위

별도 코드 검토에서 한글 로컬 설정 인코딩, 완료 통지 순서, 디스크 백업의 상대 자산 경로 문제를 확인했다. 앞의 두 항목은 회귀 테스트 후 수정했으며, 마지막 항목은 바이트 복사 백업을 원래 위치로 복원하는 절차를 README/AGENTS에 명시했다.

Windows에서 로컬 파일 연결과 Cycles CPU 렌더를 검증했다. macOS/Linux 지원 코드, 다른 GPU/드라이버, 다른 Blender 버전, 외부 자산이 포함된 복잡한 장면, 긴 영상 렌더는 실제 검증하지 않았다. 대화창 영상 스트리밍이나 마우스 제어 기능은 구현 범위에 포함되지 않는다. AGENTS.md는 작업 지침이며 임의 Python을 격리하는 보안 장치가 아니다.
