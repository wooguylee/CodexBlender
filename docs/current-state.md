# 현재 작업 상태

기록일: 2026-09-10 (한국 시간). 실제 연결 여부는 매번 `status`로 확인한다.

## 사용자 목표

Blender를 잘 모르는 사용자가 Codex에게 말로 지시하여 결과물을 만들고, 옆의 Blender 창과 대화의 미리보기로 중간 결과를 확인한다. 도구·제작 코드·원본·작업 기록을 이 프로젝트에 저장하고 Git clone으로 다른 PC에서도 이어간다.

## 구현된 환경

로컬 파일 큐를 사용하는 Blender 연결, Windows 자동 탐색 실행기, 상태/장면/수정/저장/미리보기/연결 종료 CLI를 구성했다. 의존성은 Blender와 Python 표준 라이브러리다. 최초 설치 PC는 Blender 5.2.1 LTS, Windows에서 검증했다.

`AGENTS.md`에 후속 에이전트의 실행·백업·범위 보호·결과 확인 규칙이 있다. 새 세션에서는 이 파일의 상태를 사실로 단정하지 말고 CLI로 확인한다.

사용자 지정 이름은 **브리찌**다. 사용자의 메모리 요청은 Codex 메모리와 프로젝트 메모리에 함께 기록한다. `docs/memory/MEMORY.md`에 명칭과 기록 규칙을 저장했으며 `AGENTS.md`의 세션 시작 절차에서 필수로 읽도록 연결했다.

## 현재 장면

- 원본: `scenes/current.blend`
- 제작용 컬렉션: `CodexDemo`
- 중심 객체: `Demo_Hero` (모서리가 둥근 주황색 직육면체)
- 카메라: `Demo_Camera`
- 렌더: Cycles CPU, 16 samples, 960×720 PNG
- 기본 Cube/Camera/Light 컬렉션은 삭제하지 않았으며 데모 뷰 레이어에서 제외했다.
- 외부 자산/유료 자산/다운로드 없음.

## 최초 시연

1. `workflows/demo_scene.py`: 파란 물체 + 받침대 + 조명 + 카메라.
   - 작업: `outputs/jobs/20260909T143917-5960d9a704/`
   - 미리보기: `outputs/demo/01-blue.png`
2. `workflows/demo_adjust.py`: 주황색과 높이 변경.
   - 작업: `outputs/jobs/20260909T143952-0cf115ac7f/`
   - 미리보기: `outputs/demo/02-orange.png`

각 작업에 실행 코드 사본, 요청/결과 JSON, 로그, 변경 전후 `.blend`, PNG를 저장했다. `outputs/latest.json`이 최신 미리보기를 가리킨다. 이후 제작은 사용자 요구에 맞춰 새 `workflows/<작업명>/` 코드를 추가한다. 현재 예제는 제어 시연이며 사용자의 최종 제작 주제는 아직 정해지지 않았다.

## 다음 PC / 다음 대화

Blender 설치 → 저장소 clone → `Start-Blender.cmd` → `status`와 `scene` 확인 → 사용자 요청의 제작 진행. 이미 저장된 작업을 보려면 예제를 다시 만들지 말고 `start`로 현재 원본을 연다.

원격 저장소: `https://github.com/wooguylee/CodexBlender.git`, 기본 브랜치: `main`. 사용자의 추가 요청에 따라 초기 코드·문서·원본·미리보기를 Git으로 관리한다. `.runtime/`, PC별 경로 설정, 캐시는 제외한다. 동기화 상태는 `git status`와 원격 refs로 확인한다.

검증 상세는 `verification.md`, 설계는 `design.md`, 조작법은 루트 `README.md`를 참고한다.
