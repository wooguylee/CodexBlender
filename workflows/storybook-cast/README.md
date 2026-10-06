# 네 가지 이야기 친구들 — 제작·검증 기록

## 현재 전달본 v002: 팔·몸통 연결 보완

2026-10-06 후속 요청에 따라 20종의 어깨 피벗·팔 메시·스킨 가중치를 보완했다. 최신 모델과 패키지는 `exports/storybook-cast/v002/`이며 기존 v001은 보존했다. 자세한 원인, 구현, 368프레임 접합부 검사, 재현 명령은 [SHOULDER_FIX.md](SHOULDER_FIX.md)에 기록한다. 아래 v001 기록은 제작 당시 검증 범위이며, 당시에는 팔 시작 단면의 몸통 내부 포함 검사가 없었다.

## v001 최초 제작 기록

사용자 요청(2026-10-06): 숲속 우체국·한입 디저트 마을·꼬마 우주 정비소·바닷속 작은 구조대 각각 5종, 총 20종 캐릭터를 만들고 리깅한다. 각자 독립 모델로 저장하고 Unity에서 활용하도록 걷기/달리기/앉기를 포함한다.

기존 weather-rigs / weather-unity 흐름을 확장한다. 디자인은 기존 날씨 요정과 어울리는 둥근 실루엣·파스텔·짧은 팔다리다. 각 캐릭터는 개별 `.blend`, FBX, URP Prefab과 Animator를 제공하며 Generic 리그를 사용한다. 물고기/해마의 Walk/Run 슬롯은 느린/빠른 헤엄이다. Blender에는 손발 IK와 얼굴 driver, Unity에는 평가된 뼈/표정 애니메이션과 얼굴 컴포넌트를 제공한다.

## 제작 순서

- [x] 1. 공통 메시/재질/스킨/손발 IK/얼굴 생성기와 20종 디자인 정의. 4개 전용 Scene 생성과 주제별 미리보기 검사.
- [x] 2. Idle, Walk, Run, SitDown, SitIdle, StandUp, Wave, Celebrate 동작 및 순환/착지/앉은 높이/스키닝 검증.
- [x] 3. 개별 Blender 20개 독립 재개방과 FBX 20개 저장. shape driver 동결과 n-gon 경고 회피.
- [x] 4. Unity 새 `Assets/StorybookCast`, `Assets/Scripts/StorybookCast`에 반입. 20개 Prefab/Animator, 4개 시연 Scene, 160개 클립과 Play 모드 검증.
- [x] 5. 주제별 이미지·동작 영상·패키지/ZIP·한국어 사용법 저장과 무결성 검증.
- [x] 6. 기존 날씨 원본과 배포 자산 19개의 SHA-256 동일 확인. 이번 전용 경로와 상태 추가분만 커밋/푸시 대상으로 분리. 실제 원격 반영 결과는 최종 응답에 기록한다.

## 파일과 검증 책임

`BUILDER_API.md`는 독립 주제 모델 코드의 계약이다. geometry/rig/animation/export/Unity 준비를 분리하고 실시간 Blender/Unity 조작은 root만 한다. 주제별 모델 소스는 독립 파일로 병렬 작성할 수 있다. 공통 제어 연결/기존 장면/저장소 작업은 공유하지 않는다.

최종 경로는 `exports/storybook-cast/v001/`, 작업 증거는 `outputs/storybook-cast/v001/`, Unity 기록은 WorkUnity의 `doc/verification/storybook-cast-v001/`. 메모리를 새로 쓰거나 무관한 기존 파일을 수정하지 않는다.

검증은 실제 산출물 기준: 20개 독립 모델, 스킨 가중치 정규화와 누락 없음, 모든 IK/driver 유효, 8개 클립/캐릭터, 순환 동작 연결, 변형 시 유한 좌표와 착지, Unity 컴파일/재생/재질과 표정 확인, 직접 미리보기 검사, 압축 CRC 및 패키지 내부 바이트 비교. 개별 모델/패키지는 GitHub의 파일 크기 제한 안으로 유지한다. 모바일 LOD/다른 파이프라인·기기 빌드/Unity 실시간 IK는 별도 범위다.

## 진행 기록

- 기존 지침/현재 상태와 실제 브리찌 연결 확인. `Weather_Rigs_v001` / `WR1_Camera`를 확인하고 기존 연결이 없어 current.blend로 새 브리찌 세션을 시작했다. 사용자 승인 범위의 제작을 반복 승인 없이 진행한다.

## 실제 산출물

- `exports/storybook-cast/v001/`: 4주제 ×5종, 독립 `.blend` 20개, FBX 20개, Prefab/Animator 20개씩, 4개 Showcase Scene. 3개 얼굴 ShapeKey와 손발 2관절 IK, 귀/꼬리/촉수 등 추가 뼈.
- `StorybookCast-Unity6-URP-v001.unitypackage`(약 11.7 MB): 전체 20종. 주제별 Unity 패키지 4개(1.9~3.6 MB), 주제별 `*-Models-v001.zip` 4개(8.2~14.6 MB).
- `previews/all-20-characters.png`, 개별 PNG 20개, Unity 기본 자세 4장, 동작 비교표, MP4 4개. 영상마다 1280×720 / 24fps / 368프레임 / 15.333초 / 무음.
- 사용법은 전달 폴더 `README.md`. Native IK/driver는 Blender에서 편집하고 Unity는 뼈/표정이 베이크된 Generic 리그를 재생한다. 복어·해마의 Walk/Run은 느린/빠른 헤엄이며, 모든 이동은 제자리 동작이다.

## 검증 증거

`outputs/storybook-cast/v001/` 아래:

- `export-manifest.json`: 모델 구성, 애니메이션 범위, 경로·SHA-256, 기존 원본 19개 보존 기준.
- `native-verification.json`: 20/20 독립 재개방 통과. 각 파일 하나의 Scene/Armature/스킨 메시, 가중치/driver/9 Action 검사. 반복 끝점 최대 좌표 차이 1.2e-16 미만, 측정한 최대 바닥 관통 8.6e-8 미만. 실제 얼굴 정점 변화와 앉은 높이 감소 확인. 외부 자산 없음. Idle 1프레임, Pose Mode CTRL_Body 선택 상태로 저장 후에만 임시 렌더 조명을 추가했다.
- `Forest/Dessert/Space/Sea-unity-verification.json`: Unity 6000.3.25f1 / URP 17.3.0에서 20개 유효 Generic Avatar, 160개 클립, 모든 URP 재질, 60 BlendShape와 실제 스킨 정점 변화, 반복/바닥/착석 높이 확인.
- `unity-runtime-verification.json`: 실제 Play Mode에서 20개 Actor ×8개 상태 호출, SkinnedMesh BakeMesh 변화, SitDown→SitIdle, 수동 얼굴 40/45/25 결과 확인. 기존 RainbowIsland Scene으로 복귀하고 dirty=false / Play 종료 / 열린 Scene 1개를 확인했다.
- `movie-verification.json`: MP4 4개 전체 디코딩, 프레임수/포맷 확인. 원본 PNG 전체 프레임의 고정 배경 ROI 변화 0. native 20종과 Unity Idle/Walk/Run/SitIdle, 완성 영상 추출 프레임을 직접 시각 검사했다.
- `unitypackage-verification.json`: 전체 패키지 실제 자산 293개와 주제별 72/77/82/77개의 파일 및 `.meta` 바이트가 전달 자산과 동일. 각 패키지 FBX 개수 20 또는 5개 확인. 포함 경로를 전용 폴더로 제한했다.
- `zip-verification.json`, `delivery-verification.json`: ZIP 4개의 CRC와 모든 내부 바이트 일치. 전달 파일 674개 해시 목록 `SHA256SUMS.json`, 가장 큰 파일 14,573,045 bytes.

전달 폴더는 `.gitattributes`의 `exports/storybook-cast/** -text`로 줄바꿈 자동 변환을 막아 패키지·원본 파일 해시를 다른 체크아웃에서도 보존한다. Unity가 생성한 `.meta`/`.mat`/`.prefab`/`.controller`/`.unity`의 빈 값 뒤 공백은 원본 바이트대로 보존하고, 작성한 코드/문서의 공백 오류는 별도 검사한다.

Bridge 최종 작업 `20261006T091131-edbf060846`, `ok=true`, 미리보기 직접 검사. 현재 GUI Blender는 `SC_Dessert_v001`의 기본 자세이며, 개별 배포 원본에는 다른 캐릭터나 스튜디오가 들어 있지 않다. 엔진 제어는 root만 수행했다. 독립 에이전트는 세 주제 모델 소스/런타임 코드/검증 스크립트 및 읽기 전용 리뷰를 맡았다.

## 발견·수정한 문제

1. BMesh bevel의 기본 profile=0으로 빵/로봇/가방 모서리가 계단처럼 보였다. `profile=.5`를 명시하고 별 앞뒤 winding과 링/tube 면 방향을 정리했다.
2. tube 단면마다 독립 `to_track_quat`를 쓰면 수직 접선에서 180° 뒤집혀 무릎에 틈이 생겼다. parallel transport 프레임으로 교체했다. neutral rig 평가 vs 원본 정점 차이는 약 1.3e-6이므로 IK 원인이 아님을 먼저 확인했다.
3. 해마는 꼬리 접지가 몸 하강을 상쇄해 휴식 높이 감소가 .046에 그쳤다. 긴 몸통을 휴식 시 16% 낮추고 해마 하나만 다시 베이크·검증했다.
4. 독립 리뷰에서 마카롱·슈크림의 몸통과 허벅지 상단 빈틈을 확인했다. 두 캐릭터만 hip Z=.98로 연장해 몸통 안으로 연결했다. native/Unity/Play 검사와 수정된 Idle·Walk·Run·SitIdle 이미지 재검토 통과. 남은 Critical/Important 리뷰 항목 없음.
5. Unity에서 92프레임 렌더 호출은 한 번 응답 연결이 끊겼지만 파일 184개가 정상 완료되어 있었다. 같은 구간을 재실행하지 않고 실제 파일 개수를 확인한 뒤 46프레임 단위로 이어서 완료했다.
6. Play 검사 준비의 일회성 C# 도구 호출에 namespace 오타가 있었으며 즉시 중단·수정했다. 해당 오류는 저장된 소스 컴파일 문제가 아니고, 기존 Scene에 변경을 저장하지 않았다. 최종 실제 소스 컴파일 오류 0. 콘솔의 `Deleting invalid font reference` 경고 1건은 기록하되 이 팩의 자산 오류로 단정하지 않는다.

## 재현 범위와 명령

이 workflow는 처음부터 새로 생성하는 제작 절차다. `01_build_models.py`부터 실행하며, 동일한 v001 산출물에 재실행하면 보존 검사로 중단한다. 후속 제작은 경로/Scene 이름을 새 버전으로 바꾸고 진행한다. `01d` / `02b` / `02c`는 당시 draft를 보존한 일회성 보완 스크립트로 일반 재생성에 반복 실행하지 않는다.

1. 브리찌 `run --script workflows/storybook-cast/01_build_models.py`.
2. `02_export_forest.py`, `02_export_dessert.py`, `02_export_space.py`, `02_export_sea.py`를 각각 브리찌로 실행.
3. 별도 Blender `--background --factory-startup --python workflows/storybook-cast/03_verify_native.py`. 이미 검증된 다른 파일의 해시가 같을 때만 `-- --only Key1,Key2`로 수정 대상만 재검증 가능.
4. Unity 코드/FBX/catalog를 전용 Assets 폴더에 복사하고 MCP `refresh_unity`로 컴파일. 공식 Editor API `StorybookAssets.BuildTheme`, `StorybookReview.VerifyTheme/CreateShowcase`, Play Mode `VerifyPlaying`.
5. `RenderFrames(theme, "Timeline", directory, first, 46)`로 0~367을 분할 출력. `04_package.py --unity-project <프로젝트> --prepare`로 이미지/영상을 생성. Unity API `ExportTheme/ExportAll` 후 `04_package.py --unity-project <프로젝트>`로 무결성 검사와 ZIP 작성.

공통 브리지 코드 수정이 없으므로 브리지 unittest/E2E 재실행은 범위 밖이다. Python 구문 검사, 실제 Blender·Unity·출력 파일 검증을 수행했다. Windows/RTX3090 외 장비, 다른 Unity 버전·파이프라인, 모바일 빌드/LOD/Humanoid/실시간 Unity IK는 검증 범위 밖이다.

주제 ZIP을 단독으로 풀었을 때도 사용법의 전체 목록 이미지가 표시되도록 `previews/all-20-characters.png`를 각 ZIP에 포함했다. 네 ZIP 모두 내부 20개 파일 CRC/바이트 검사를 다시 통과했다.
