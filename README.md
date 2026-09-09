# CodexBlender

**말로 요청 → Blender 작업 창에서 확인 → 수정 → 원본과 이미지 저장**을 위한 로컬 작업 환경입니다. 외부 서버·API 키·pip 설치 없이 Blender와 Python 표준 라이브러리를 사용합니다.

## 이 PC에서 시작

프로젝트의 `Start-Blender.cmd`를 더블클릭하면 연결된 Blender 작업 창이 열립니다. 이미 이 프로젝트의 연결이 있으면 재사용합니다. 기존에 별도로 열어 둔 Blender에는 연결하지 않습니다.

Codex에서 이 폴더를 프로젝트로 열고 다음처럼 요청하세요.

> AGENTS.md를 읽고 현재 블렌더 장면을 확인해줘. 가운데 물체를 둥근 형태로 바꾸고 중간 결과를 보여줘.

기본 원본은 `scenes/current.blend`입니다. 블렌더 창을 옆에 놓고 변화를 확인할 수 있고, 주요 단계는 Codex 대화에도 PNG로 표시합니다. 명령 실행이 끝난 뒤 화면이 갱신됩니다. 렌더 중에는 기다려야 하며, 대화창 자체가 실시간 영상 스트림인 것은 아닙니다.

## 다른 Windows PC에서 Git clone 후

1. Blender를 설치합니다. 현재 검증 버전은 **5.2.1 LTS**이며 재현성을 위해 같은 버전을 권장합니다. Blender 실행 파일 자체는 저장소에 넣지 않습니다.
2. `git clone https://github.com/wooguylee/CodexBlender.git`으로 저장소를 clone하고 Codex에서 해당 폴더를 엽니다.
3. `Start-Blender.cmd`를 더블클릭하거나 Codex에 “AGENTS.md를 읽고 연결해서 현재 작업을 이어줘”라고 요청합니다.
4. 자동 탐색이 실패하면 `blender.local.example.json`을 `blender.local.json`으로 복사하고 그 PC의 `blender_executable` 경로로 수정합니다. 또는 `BLENDER_EXECUTABLE` 환경변수를 지정합니다.

Windows 실행기는 Blender에 포함된 Python을 사용합니다. 별도 Python 설치가 보통 필요 없습니다. Blender가 특수 배포판이라 Python이 없으면 Python 3.11+를 설치해야 합니다.

`blender.local.json`과 `.runtime/`은 Git 제외 대상이며 각 PC에서 새로 생성됩니다. `workflows/`, `scenes/`, `assets/`, `outputs/`, 문서, 도구는 기본적으로 Git에 포함됩니다. 원격 저장소는 [wooguylee/CodexBlender](https://github.com/wooguylee/CodexBlender)이며 커밋/푸시는 사용자의 요청 범위에서 수행합니다. 큰 영상이나 누적 `.blend` 파일은 크기에 따라 Git LFS 또는 별도 보관 정책을 선택하세요. 현재 예제는 일반 Git으로 보관할 수 있는 작은 파일입니다.

## 명령

아래 명령은 저장소 루트의 PowerShell에서 실행합니다. Codex가 대신 실행할 수 있으므로 사용자가 외울 필요는 없습니다.

```powershell
# 설치 정보, 연결, 장면 조회
powershell -NoProfile -ExecutionPolicy Bypass -File scripts/blender.ps1 doctor
powershell -NoProfile -ExecutionPolicy Bypass -File scripts/blender.ps1 start
powershell -NoProfile -ExecutionPolicy Bypass -File scripts/blender.ps1 status
powershell -NoProfile -ExecutionPolicy Bypass -File scripts/blender.ps1 scene

# 시연: 파란 물체 생성 → 주황색으로 변경하고 높이 조정
powershell -NoProfile -ExecutionPolicy Bypass -File scripts/blender.ps1 run --script workflows/demo_scene.py --label "파란 물체 생성"
powershell -NoProfile -ExecutionPolicy Bypass -File scripts/blender.ps1 run --script workflows/demo_adjust.py --label "주황색과 높이 수정"

# 추가 미리보기와 명시적 저장
powershell -NoProfile -ExecutionPolicy Bypass -File scripts/blender.ps1 preview
powershell -NoProfile -ExecutionPolicy Bypass -File scripts/blender.ps1 save --file scenes/my-scene.blend

# 연결 종료: Blender GUI 창은 남아 있습니다.
powershell -NoProfile -ExecutionPolicy Bypass -File scripts/blender.ps1 stop
```

`run`/`preview`의 대기 기본값은 180초입니다. 큰 작업은 `--timeout 600`처럼 늘릴 수 있습니다. 타임아웃 응답에는 작업 ID와 결과 경로가 표시되며 작업이 계속 진행될 수 있으므로 같은 명령을 다시 보내지 마세요. `status`로 상태를 보고 해당 `result.json`을 확인합니다. 렌더 중 `busy`의 갱신 시각이 오래되어도 즉시 연결 장애라고 판단하지 않습니다.

`run --no-preview`는 백업과 저장을 유지하면서 렌더만 생략합니다. `scene`은 조회만 합니다. `save`는 저장만 하며 미리보기를 생성하지 않습니다.

## 폴더

| 경로 | 내용 |
|---|---|
| `AGENTS.md` | 다음 Codex 작업에도 적용할 실행·보호·검증 규칙 |
| `bridge/` | 명령 클라이언트, Blender 내부 worker, 공통 파일 도구 |
| `scripts/blender.ps1`, `Start-Blender.cmd` | Windows 실행 진입점 |
| `workflows/` | 보존·재실행 가능한 제작 코드 |
| `scenes/current.blend` | 현재 작업 원본 |
| `assets/` | 텍스처, 폰트, 모델 등 프로젝트 자산 |
| `outputs/jobs/<id>/` | 요청, 실행 코드 사본, 로그, 결과, 변경 전후 `.blend`, PNG |
| `outputs/latest.json` | 마지막 미리보기 경로와 해당 작업 결과 |
| `outputs/demo/` | 최초 시연의 전후 비교 이미지 |
| `docs/current-state.md` | 현재 작업과 다음 작업을 위한 기록 |
| `outputs/verification/` | 실제 검증 결과 |
| `.runtime/` | PC별 연결/잠금/세션 로그. Git 제외 |

`run`에 전달하는 파일은 저장소 안의 `.py`여야 합니다. 실행 시 `PROJECT_ROOT`(저장소 경로), `OUTPUT_DIR`(해당 결과 폴더), `bpy`가 제공됩니다. 전체 장면을 지우는 대신 대상 컬렉션이나 객체를 제한하세요. 예제 생성기는 `CodexDemo` 컬렉션만 재생성하지만 다른 최상위 컬렉션을 현재 뷰 레이어에서 제외하므로 제작 중 장면에 무조건 실행하지 마세요.

## 저장·복구·자산

기본 `run`은 현재 장면을 `before.blend`로 백업한 후 코드를 실행하고, 성공한 장면을 `scenes/current.blend`와 `after.blend`로 저장하고 미리보기를 만듭니다. 미리보기 실패 시에도 장면 저장은 완료되어 있을 수 있으며 결과 JSON의 `file`/`snapshot`/`error`로 구분합니다. 실패 코드를 자동으로 되돌리거나 재실행하지 않습니다.

복구할 때는 연결을 `stop`하고 `start --file outputs/jobs/<작업ID>/before.blend`로 새 창에 백업을 여세요. 기존 창은 남습니다. 사용자가 직접 편집한 내용은 먼저 저장합니다. `stop`은 저장 명령이 아닙니다.

`save`가 만든 `previous-file.blend`는 기존 디스크 파일의 **그대로 복사한 보관본**입니다. 이 파일의 상대 자산 경로는 원래 저장 위치를 기준으로 합니다. 복구할 때는 해당 작업 `request.json`의 `file` 경로를 확인하고, 그 위치의 현재 파일을 별도 보관한 다음 보관본을 원래 위치로 복사하여 `start --file <원래 경로>`로 여세요. `previous-file.blend`를 결과 폴더에서 직접 열면 상대 텍스처/라이브러리 경로가 달라질 수 있습니다. `run`의 `before.blend`/`after.blend`는 Blender의 경로 재매핑 저장을 사용합니다.

외부 텍스처·폰트 등은 `assets/`에 보관하고 상대 경로로 연결하거나 지원되는 자산을 `.blend`에 pack합니다. 연결 라이브러리·캐시·영상은 별도 파일도 필요할 수 있습니다. 현재 데모에는 외부 자산이 없습니다.

## 연결 방식과 한계

CLI가 `.runtime/sessions/<id>/queue/`에 요청을 기록하고 Blender의 메인 스레드 타이머가 0.25초 간격으로 확인합니다. 인터넷이나 로컬 네트워크 포트를 열지 않습니다. 같은 프로젝트에는 연결 하나만 허용하며, 재시작은 새 세션을 사용합니다. 오래된 큐는 자동 재생하지 않습니다.

이는 Blender 내 Python 실행 도구입니다. **AGENTS.md는 에이전트 작업 지침이며 보안 샌드박스가 아닙니다.** 임의 Python은 사용자 계정 권한을 가지므로 신뢰하는 코드만 실행하세요. 파일 인수의 프로젝트 경계 검사는 임의 스크립트의 모든 OS 접근을 막지는 않습니다. 장시간 또는 무한 루프 스크립트는 Blender 창을 멈출 수 있습니다.

시작 시 공장 초기 설정과 파일 자동 실행 비활성화를 사용하므로 사용자 개인 애드온/환경설정에 의존하지 않습니다. 코드가 연결·저장·렌더를 담당하며 Blender UI 마우스 자동화는 사용하지 않습니다.

## 검증 / 다른 OS

```powershell
python -m unittest discover -s tests -v
$env:BLENDER_E2E = '1'
python -m unittest discover -s tests -v
Remove-Item Env:BLENDER_E2E
```

별도 Python이 없으면 Blender 설치 폴더의 `<버전>/python/bin/python.exe`로 같은 unittest 명령을 실행합니다. 실제 Blender 검증은 `.runtime/` 아래 공백·한글 경로에 도구 사본을 만들고 독립된 백그라운드 프로세스로 실행합니다. 기존 GUI 작업에는 영향을 주지 않습니다.

macOS/Linux에서는 Python 3.11+로 `python3 bridge/client.py doctor`, `python3 bridge/client.py start` 등 동일한 하위 명령을 사용할 수 있게 작성했습니다. 표준 설치 경로/PATH 탐색 또는 `BLENDER_EXECUTABLE` 설정을 지원합니다. **현재 실제 검증은 Windows에서 수행했으며 다른 OS/GPU 결과는 보장하지 않습니다.** 자세한 결과는 `docs/verification.md`를 확인하세요.
