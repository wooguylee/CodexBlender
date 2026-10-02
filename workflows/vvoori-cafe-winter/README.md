# vvoori-cafe-winter v001

사용자 요청: 겨울 오후 3시, 50도 사선 통창으로 눈 덮인 공원을 보는 고정 카메라의
손그림 애니메이션 풍경. 새 이미지 생성부터 실제 1920×1080/24fps/20초 무음 영상까지 제작.
원문은 `vvoori-cafe-winter-one-shot-prompt.txt`다.

## 구성과 파일

- `assets/vvoori-cafe-winter/v001/ai-winter-park.png`: 새로 생성한 불투명 RGB 공원/도로, 1672×941.
- `assets/vvoori-cafe-winter/v001/ai-winter-cafe.png`: 새로 생성한 RGBA 실내/가구/외곽 창 테두리, 1672×941.
- 이미지 도구: built-in `image_gen`. 생성/수정 프롬프트는 이 폴더의 `v001-*-prompt.txt`에 보존.
- `scenes/vvoori-cafe-winter-v001.blend`: 전용 Scene 하나, 두 이미지 pack, 상대 경로.
- `outputs/vvoori-cafe-winter/v001/`: 최종 MP4, 포스터, 반복 재생 HTML, 검증 JSON.
- 생성 초안과 도로 배치 가이드는 로컬에 보존한다. 최종 합성에 들어가는 정적 이미지는 위 두 장뿐이다.

합성 순서는 **공원 → 실제 Blender 차량과 눈 → 실내 이미지**다.
창틀/창턱/벽/천장/바닥/테이블/의자/잔/책의 3D 모델이나 정적 3D 렌더 캐시는 없다.
527개 객체는 차량 구성요소와 차량 윤곽/접지 그림자, 눈 280개, 차량 이동 Empty와 카메라다.
기존 카페의 차량 메시 형태만 독립 복사했고, 새 색상·셀 명암·차선·주기로 구성했다.
기존 Scene 객체 수와 기존 vvoori-cafe 원본/MP4 10개의 SHA-256을 보존한다.

## 움직임과 색/알파

- 카메라의 창면 정면 대비 수평각은 실제 측정 약 50도다. 카메라/노출/조명은 고정이다.
- 6대 차량이 두 차선에서 반대 방향으로 움직인다. 불규칙 위상, 실제 3D 원근과 접지 그림자를 사용한다.
- 눈은 실제 3D 입자 280개이며 차량 앞/뒤 공간을 분리하여 차체 관통을 피한다.
  서로 다른 깊이·크기·위상·약한 좌우 흔들림을 사용한다. 적설은 정적 공원 이미지에만 있다.
- 모든 움직임의 주기는 **480프레임**이다. 출력은 1~480을 모두 렌더하고, 검사용 다음 주기 시작은 481이다.
  첫 프레임을 마지막에 복제하지 않는다. 480→1은 정상적인 한 프레임 이동이다.
- 생성 실내 원본의 alpha 252~253 영역은 합성 노드에서 1로 정규화한다.
  얇은 안티앨리어싱 경계는 보존한다. 원본 PNG 바이트는 변경하지 않는다.
- sRGB 이미지를 선형 합성 후 Standard sRGB로 출력한다. 추가 AgX/노출 보정은 없다.
- 최초 추가 검사에서 Scale 노드의 기본 `Clip`이 화면 맨 위 한 줄을 반투명하게 만드는 문제를 발견했다.
  `Extension X/Y = Extend`로 고친 뒤 전체 480프레임을 재렌더했다.
  최초 출력과 소스는 `initial-frames-before-edge-fix/`, `source-before-edge-fix.blend`로 로컬 보존한다.

## 제작 순서와 재현

기존 겨울 결과가 있으면 새 버전을 지정한다. 이 빌더를 같은 Scene에서 재실행하지 않는다.
브리찌는 프로젝트 루트에서 실행하며 변경 전후 백업과 코드 사본을 보존한다.

1. `00_prepare.py`: 기존 결과 해시와 이미지 생성용 단순 도로 구도 가이드.
2. `01_build_winter_scene.py`: 브리찌 `run --script`로 새 Scene과 두 이미지 합성.
3. `02_refine_and_audit.py`: 차량 윤곽, 전체 프레임 차도 접지, 화면 밖 순환, Full HD 미리보기.
4. `03_render_master.py`: 480장 Full HD와 481 검사용 렌더, 전용 Scene library 저장.
5. `05_finalize_source.py`: 별도 `blender --background scenes/vvoori-cafe-winter-v001.blend --python ...`로
   라이브러리 파일을 기본 Scene이 올바르게 선택된 편집용 일반 `.blend`로 저장.
6. `06_verify_reopen.py`: 다시 별도 Blender로 열고 이미지 외부 경로를 의도적으로 사용할 수 없게 바꾼 뒤
   packed 데이터만으로 실제 Full HD 재렌더. 이 검증은 원본 파일을 저장/변경하지 않는다.
7. `04_package_verify.py`: 로컬 Python(Pillow/NumPy)과 FFmpeg로 모든 프레임 검사, H.264 MP4와 HTML 작성.

이번 제작의 경계 보정은 `diagnose_static_mask.py` → `diagnose_scale.py` → `02b_fix_image_edges.py`
→ `03b_rerender_fixed_edges.py` 순서였다. 새 제작의 `01_build_winter_scene.py`에는 수정이 이미 포함된다.

## 검증 기록

- `motion-audit.json`: 286개 움직임의 1/481 및 0/480 변환 비교, 차도 접지와 순환 가림.
- `verification.json`: 480개 PNG, 고정 실내 전체 마스크/14개 ROI, MP4 480프레임/20초/무음/전체 디코딩.
- `source-verification.json`: 전용 Scene, 527개 객체, 이미지 두 장 packed SHA-256 및 경로.
- `native-reopen-verification.json`, `native-render-comparison.json`: 독립 재개방 실제 렌더와 원본 PNG 비교.
- `edge-fix-verification.json`: 화면 최상단 보간 알파 문제 재현과 보정 증거.
- 실제 검증 환경은 Windows, Blender 5.2.1 LTS, NVIDIA RTX 3090/OptiX다. 다른 OS/GPU는 미검증이다.

정적 PNG의 고정 영역 변화와 손실압축 MP4의 미세한 코덱 차이는 별도로 기록한다.
전체 불투명 마스크는 944,831픽셀이다. 480프레임 전체에서 14개 명명된 ROI는 픽셀 동일하며,
전체 마스크에는 199/247/364프레임의 각 한 픽셀 파랑 채널에만 1/255 차이가 남았다.
위치는 각각 (1130,718), (162,1023), (1106,718)이다. 이 세 개의 단일 단계 양자화 차이는
`mask-rounding-diagnosis.json`에 보존하고, 검증은 최대 1단계/프레임당 2픽셀/총 10개 이하로 제한한다.
광범위한 색 변화나 국소 조명 깜빡임은 이 허용 범위에 포함하지 않는다.
후속 피드백은 이 v001 원본을 기준으로 새 버전을 만들어 반영한다.
