# 날씨 요정 개별 모델과 Unity 변환 v001

사용자 요청: 리깅된 다섯 캐릭터를 개별 모델 파일로 저장하고 Unity에서 활용할 수 있게 한다.

기존 날씨 요정 제작 흐름의 분리/내보내기 작업이다. 중립 리깅 원본과 시연 원본을 독립 복제하여 기존 모델과 영상을 보존한다. 각 캐릭터의 편집용 Blender 파일, Unity용 FBX, URP 재질과 Prefab/Animator, 표정 조절 컴포넌트, 가져오기 패키지를 만든다. 실제 Unity 6.3 LTS 테스트 프로젝트에서 가져오기/스키닝/표정/애니메이션과 렌더를 검사한다.

Blender의 IK 제약/driver 자체는 Unity에서 실행되지 않는다. 편집용 `.blend`에는 원래 조절 기능을 유지하고, FBX에는 평가된 뼈 변환과 표정 가중치를 프레임별로 베이크한다. Unity에서는 Generic Animator, SkinnedMeshRenderer, BlendShape로 재생/조절한다. Humanoid 자동 리타게팅 대상이 아니다.

자산은 `exports/weather-fairies/v001/`, 검사 중간 파일은 `outputs/weather-unity/v001/`에 저장한다. Unity 검증 기록은 WorkUnity의 `doc/verification/weather-fairies-v001/`에도 보관한다.

검증 기준: 개별 파일마다 캐릭터 하나/Armature 하나, 외부 링크 없음; FBX의 스킨과 표정/클립 유효; Unity 컴파일 오류 없음; 재질/얼굴/애니메이션 렌더 직접 확인; 원본 SHA-256 유지; 관련 변경만 커밋/푸시.

## 완료 결과 — 2026-10-06

- 각 캐릭터 `.blend` 5개 / FBX 5개 / Unity Prefab 5개 / Animator Controller 5개 / URP 재질 32개. 개별 파일 위치와 조작법은 `exports/weather-fairies/v001/README.md`.
- 총 142개 뼈, 149개 스키닝 메시, 53개 BlendShape. 각 캐릭터에 RigDemo·Idle·HandsIK·Expressions·Weather·Special 6개 클립. Blender의 1–384프레임을 24fps로 베이크했다.
- 독립 Blender 파일 다섯 개를 재개방해 단일 캐릭터/Armature, 외부 파일 없음, 124개 driver 유효성을 확인했다. 각 파일의 768×768 미리보기와 Unity의 1920×1080 기본/놀람/특수 포즈를 직접 시각 검사했다.
- Unity 6000.3.25f1 / URP 17.3.0에서 Generic Avatar, 스킨 연결, 재질, 실제 정점 변형, 표정 curve 0→100 변화와 수동 표정 조절 확인. Play Mode의 실제 Animator를 7.4초로 이동해 다섯 캐릭터 모두 초기화/놀란 표정 100을 확인했다. 최종 재가져오기·컴파일·Play·렌더 후 콘솔 오류/경고 0개.
- 원본 두 `.blend` SHA-256 동일. 발 원점 오차 0.000002 미만. Unity 패키지의 각 자산 바이트가 전달 폴더와 동일한지 비교하고 ZIP 전체 CRC 검사를 수행한다.
- 결과 묶음은 `WeatherFairies-Models-v001.zip`, Unity용은 `WeatherFairies-Unity6-URP-v001.unitypackage`. `delivery-verification.json`에 파일 해시와 실제 검사 범위를 기록한다.
- 마지막 브리찌 변경 작업 `20261006T064244-e551531056`은 `ok=true`, 원래 중립 Scene 복귀 및 미리보기 직접 검사 완료. 기존 원본과 무관한 작업 파일은 변경 대상에서 제외했다.

## 재현과 수정

1. 브리찌에서 `01_export_characters.py` 실행. 출력 파일이 이미 존재하면 멈추므로 다음 제작은 버전 경로를 변경한다. 전용 Scene과 원본을 독립 복제하며 익스포트용 n-gon만 삼각화한다.
2. Blender 백그라운드 독립 프로세스에서 `02_verify_native.py` 실행. native 원본의 화면을 정리해 저장한 후 임시 카메라/조명을 추가해 검사용 이미지만 렌더한다.
3. `python workflows/weather-unity/03_stage_unity.py --project <Unity프로젝트>`로 두 전용 자산 폴더를 복사한다. 초기 반입용이며 기존 대상이 있으면 중단한다.
4. uni MCP로 refresh/컴파일을 요청하고 오류를 확인한다. Editor API의 `WeatherFairies.Editor.WeatherFairySetup.BuildAssets()`, `CreateShowcase()`, `Verify(<증거폴더>)`를 순서대로 실행한다. Scene 생성은 이미 존재하면 중단한다.
5. `RenderShowcase(<PNG경로>, seconds)`에 0, 7.4, 13.3초를 전달한다. 실제 Play Mode의 Animator도 검사하고 종료 후 중립 자세 Scene을 저장한다. `ExportPackage(<패키지경로>)`는 두 전용 폴더만 포함한다.
6. `python workflows/weather-unity/06_package_delivery.py --project <Unity프로젝트> --evidence <증거폴더>`로 최종 자산/검증 파일을 회수하고 묶음을 검증한다.

04/04b는 rest pose 진단, 05/05b는 이번 초안의 전용 Scene에만 적용한 보정 기록이다. 후속 신규 생성 경로에는 같은 보정이 01과 `triangulate.py`에 포함되어 있다.

## 발견한 문제와 해결

- 원점 이동 후 rest data를 명시적으로 갱신하지 않으면 FBX의 rest/animation 기준이 어긋났다. Armature data/object/time update와 해당 Scene/view layer override로 수정했고 실제 Unity 정점의 발 높이로 확인했다.
- Blender 5.2 FBX의 `use_triangles=True`는 메시/Shape Key를 복제하면서 driver로 평가되는 표정 값을 고정시켰다. exporter 삼각화를 끄고 실제 익스포트 메시의 n-gon만 bmesh로 삼각화했다. 정점 순서, 모든 Shape Key 좌표, driver 수가 동일한지 확인했다. 해롱 입의 self-intersecting polygon 경고도 최종 가져오기에서 없어졌다.
- 한 Editor 프레임에서 여러 시점을 `SampleAnimation`/`Camera.Render`하면 스킨 캐시가 이전 화면을 재사용했다. 미리보기 함수에서만 `forceMatrixRecalculationPerRender`를 켰다가 원복하여 세 실제 이미지가 달라지는지 확인했다.
- 최초 복합 장시간 MCP 호출의 응답 연결이 끊겼지만 작업 결과 파일은 완료되어 있었다. 재전송하지 않고 파일/상태를 확인했다. 이후 짧은 호출로 나누었고 최종 호출은 모두 성공 응답을 받았다. 초안 콘솔은 WorkUnity 증거 폴더에 보존한 후 최종 검사 구간을 분리했다.

## 검증 범위

Windows / Blender 5.2.1 LTS / Unity 6.3 LTS / URP / RTX 3090. Blender IK·driver는 native 파일에 유지하며 Unity는 베이크된 Generic 애니메이션과 직접 제어하는 BlendShape다. Unity 실시간 IK, Humanoid 리타게팅, 다른 파이프라인/플랫폼 빌드, LOD·모바일 최적화는 이번 전달 범위에 포함하지 않는다.
