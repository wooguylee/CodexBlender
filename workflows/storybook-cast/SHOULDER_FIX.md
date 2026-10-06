# v002 어깨 연결 보완

사용자 요청: 팔이 몸에 붙어 있지 않은 캐릭터가 많으므로 보완한다.

승인된 보완 범위에서 바로 제작한다. 이전 v001 배포 파일은 보존하고 `exports/storybook-cast/v002/`와 `outputs/storybook-cast/v002/`에 새 결과를 저장한다. GUI에는 별도 v002 Scene을 만들며 기존 Scene을 삭제하지 않는다.

1. 실제 체형의 몸통 표면과 팔 시작 단면 간 signed distance를 측정해 현재 문제를 재현한다.
2. 각 체형의 몸통 안에 어깨 피벗과 팔 시작 단면을 배치한다. 새 팔은 몸통에서 손까지 연속된 tube로 만들고 안쪽은 해당 몸통 뼈에 고정, 바깥쪽은 상완/전완으로 점진 배분한다. 문어·해마·소라게·부엉이의 특수 팔도 검사한다.
3. 모든 20종/양쪽 어깨/368개 베이크 프레임에서 팔의 시작 단면이 몸통 내부에 머무는지 검사한다. 기존 표정·가중치·루프·접지·착석 검증도 유지한다. 중립/걷기/달리기/앉기/인사/기쁨의 정면·사선·측면 이미지를 직접 검사한다.
4. native20/FBX20, 기존 Unity GUID를 유지한 Prefab·클립160, 시연 Scene/영상/전체·주제 패키지를 갱신한다. 이전 전달 파일과 기존 Unity 비관련 Scene은 보존한다.
5. 결과 기록, ZIP/패키지/해시 검증, 이번 변경만 Git 커밋·푸시하고 원격 해시를 확인한다.

연결 보장은 단순히 뼈가 존재하거나 전체 메시가 하나라는 검사가 아니라, 실제 변형된 팔 시작 단면의 몸통 내부 포함과 눈으로 본 접합부를 기준으로 한다.

## 완료된 수정

- 공통 어깨 좌표가 좁은 체형 바깥에 놓였고, 기존 팔 시작 단면도 몸통과 떨어져 있었다. 몸통의 실제 표면을 측정해 어깨를 안쪽에 배치하고 몸통부터 손까지 연속된 팔을 재생성했다. 안쪽 17개 정점은 실제 몸통 뼈(DEF_Body 또는 DEF_Head)에 고정하고 상완·전완으로 점진적으로 가중치를 배분했다. 몸통과 팔은 서로 겹치는 닫힌 표면 구조이며, 용접된 단일 매니폴드 토폴로지를 뜻하지 않는다.
- tube 옆면의 뒤집힌 winding도 바로잡아 옆면과 양 끝 단면의 바깥 방향을 일치시켰다. 부엉이는 기존 날개를 유지하면서 연결 팔을 추가했고 소라게는 상완·전완을 연속 팔로 대체했다.
- 전 프레임 검사에서 복어의 낮은 지느러미가 앉을 때 바닥 보정으로 몸통을 밀어 올리는 문제를 발견했다. 착석 지느러미 목표 높이를 -0.29에서 -0.10으로 수정하고 복어의 원본·FBX·동작을 다시 저장했다. 단독 재내보내기 후에도 카탈로그와 영상 이름 순서가 유지되도록 표준 순서 정렬을 추가했다.
- 기존 Unity 자산 GUID를 유지하고 새 FBX의 클립을 기존 Animator 상태에 다시 연결했다. 개별 .blend 20개, FBX/Prefab/Animator 각 20개, 160개 클립, Showcase 4개, Unity 패키지 5개와 주제 ZIP 4개를 v002에 저장했다.

## 실제 검증 결과

- `shoulders-before.json`은 수정 전 형상을 재현한 실패 증거, `shoulders-fit.json`은 수정된 40개 어깨 단면의 성공 증거다. 초기 진단의 root_caps라는 이름에는 부엉이 타원형 날개의 일반 표면 표본 2개가 포함되어 있었다. 재현 스크립트는 이를 tube_root_ring 38개와 wing_surface 2개로 구분하도록 수정했다. 초기 집계 전체를 40개의 동일한 튜브 단면으로 해석하지 않는다.
- `native-verification.json`: 20개 파일을 독립 Blender에서 재개방했다. 각 캐릭터의 AllMotions 368프레임 × 양쪽 어깨 × 단면 정점 17개가 모두 몸통 안에 유지된다. 최소 포함 깊이 0.0409989, 몸통 좌표 기준 최대 이동 오차 3.05e-7. 가중치·driver·9 Action·루프·표정·바닥·착석 검사도 20/20 통과했다.
- `unity-shoulders/*.json`: 실제 반입된 20개 Prefab의 8개 클립/368프레임을 BakeMesh로 검사했다. 가져온 단면 좌표 대응 최대 오차 6.06e-7, 몸통 기준 단면 이동 최대 오차 6.04e-7. Native 검사의 몸통 내부 포함 결과와 함께 Unity 베이크에서도 접합부가 유지됨을 확인했다.
- `*-unity-verification.json`, `unity-runtime-verification.json`: Generic Avatar·재질·160개 클립·3개 표정/캐릭터 및 실제 Play의 160개 상태, 스키닝 이동, SitDown→SitIdle 전환, 수동 표정 제어 통과. 기존 RainbowIsland Scene 복귀, dirty=false, Play 종료.
- 4주제의 기본/걷기/달리기/앉은 대기/인사/기쁨 자세를 정면·45도·90도로 직접 시각 검사했다. 부엉이 날개와 우주복 어깨 장식을 추가 검토했다. 읽기 전용 독립 리뷰에서도 보이는 팔·몸통과 손목의 분리 틈 없음, 남은 Critical/Important/Minor 항목 없음. 정지 이미지에서 가려진 반대편 표면은 시각 판단 범위 밖이며 전체 프레임의 수치 검사로 보완했다.
- `movie-verification.json`: Unity 실제 렌더 MP4 4개, 각 368프레임/24fps/15.333초, 전체 디코딩 성공, 원본 PNG 고정 배경 국소 ROI의 모든 프레임 변화 0.
- `unitypackage-verification.json`, `zip-verification.json`: Unity 전체 패키지 실제 자산 294개 및 4개 주제 패키지의 자산·meta 바이트 대조 성공. 주제별 ZIP CRC/내부 파일 바이트 대조 성공. 카탈로그 변경 후 최초 export에서 발생한 SourceAssetDB 시간 불일치 경고는 카탈로그 동기 ImportAsset 후 5개 패키지를 재생성하여 해소했다. 추가 경고 없음, 컴파일 오류 없음.
- `delivery-verification.json`: 전달 파일 677개와 SHA256SUMS.json. 기존 v001 675개 + 날씨 원본 19개 = 694개 파일의 SHA-256 동일. 가장 큰 파일 14.7 MB 미만. 영상 원시 프레임·중간 Blender 백업은 outputs 아래에 남기고 Git에는 최종 전달본과 선택한 검증 증거를 반영한다.

## 실행과 현재 상태

브리찌 작업: `20261006T094716-f7e2feddcd`(모델), `20261006T095132-1ce1ec3913`(20개 내보내기), `20261006T095901-7ef457920d`(복어 착석), `20261006T100134-31cf64d922`(카탈로그). 모두 ok=true. GUI는 SC_Sea_v002 기본 자세이며 원본은 개별 배포 .blend로도 저장되어 있다.

새 버전 제작 흐름은 05c → 05d → `03_verify_native.py -- --version v002`이다. 05f는 이번 복어의 실패 산출물을 보존하고 재내보낸 일회성 복구이며 재실행하지 않는다. Unity에서 BuildTheme·VerifyTheme·StorybookShoulderReview.VerifyCharacter를 실행하고 전용 Showcase Play 검사 후 RenderFrames를 호출했다. `04_package.py --unity-project <프로젝트> --version v002 --prepare`, Editor API의 ExportTheme/ExportAll, `04_package.py --unity-project <프로젝트> --version v002` 순서로 포장한다. 05h는 실제 렌더의 전후 비교·각도 검토 이미지를 배치한다.

확인 환경은 Windows / Blender 5.2.1 LTS / RTX3090 / Unity 6000.3.25f1 / URP 17.3.0. 동작은 Generic 제자리 베이크이며 Unity 실시간 IK, Humanoid 리타기팅, 다른 렌더 파이프라인 및 기기 빌드는 이번 범위에 포함하지 않았다. 커밋·푸시 후 원격 해시 확인 결과는 최종 응답으로 보고한다.
