# 현재 제작: vvoori-cafe v003 — 50도 사선 통창과 만화풍 3D

2026-10-02. 새 이미지 생성·3D 구도·Full HD 전체 영상·독립 원본 검증 완료.

- 사용자 요청: 통창을 정면에서 약 50도 옆으로 바라보는 구도, 이미지와 Blender 모두 만화풍, 실제 3D 활용 확대.
- 카메라 `VC3_Camera`의 창면 정면 대비 수평각 실측 49.9999976도. Scene `Vvoori_Cafe_v003`, 객체 316개.
- 공원 RGB/실내 RGBA를 built-in image_gen으로 새로 생성. `assets/vvoori-cafe/v003/`, 각 1672×941.
- 실제 3D: 창틀·창턱·테이블·책·커피잔/받침·차량 6대·낙엽 56개. 두 단계 셀 명암 적용.
- 도로 그림에 맞춘 3D 차선 경로와 거리감. 먼 차량과 지면의 낙엽은 점진적으로 작아져 순환 시 튀지 않게 처리.
- 생성 공원 → 움직이는 3D → 생성 실내 → 고정 3D 창틀/가구 캐시 합성.
- 고정 3D 기하를 원본에 유지. 카메라/가구 변경 시 정적 캐시도 다시 렌더해야 한다.
- 원본 `scenes/vvoori-cafe-v003.blend`, 생성 이미지 2장과 고정 3D 캐시 모두 pack.
- 기본 편집 뷰 `VC3_EditAll3D`, 출력용 뷰 `VC3_Motion`. 실제 3D가 보이는 편집 화면 유지.
- 최종 영상 `outputs/vvoori-cafe/v003/vvoori-cafe-toon-20s.mp4`: **1920×1080 / 24fps / 480프레임 / 20초 / 무음**.
- 480장 PNG와 MP4 전체 검사. 10개 실내 정적 영역의 PNG 변화 0, MP4 시작/끝 픽셀 동일.
- 별도 렌더한 끝점도 첫 프레임과 동일. 62개 애니메이션 끝점 변환 오차 0.
- 새 Blender 프로세스에서 정상 원본 저장 후 다시 열어 Full HD 렌더 성공. 생성 PNG/packed 해시 일치.
- v001/v002/autumn-cafe 원본 파일 해시 유지. 기존 작업 Scene/미커밋 변경 보존.
- 원본·생성 자산·최종 MP4·포스터·재생 페이지를 Git에 포함. 480개 프레임과 중간 작업은 로컬 보관.
- 제작/프롬프트/검증: `workflows/vvoori-cafe/v003-README.md`, `v003-image-prompts.md`, `v003-*-verification*.json`.
- 마지막 브리찌 작업 `20261002T083751-aa74787bf0`, ok=true. 미리보기 직접 확인.
- 다음 단계: 사용자 피드백. 현재 구성은 고정 카메라용이며 Resolve 변경은 없다.

<!-- VVOORI_CAFE_V003_END -->

# 이전 제작: vvoori-cafe v002 — 새 AI 생성 이미지 적용

2026-10-02. 사용자 정정 반영, 이미지 생성·적용·20초 검토 영상·원본 검증 완료.

- 정확한 의도: **공원과 카페를 이미지 생성 도구로 새로 만들고, 그 이미지를 활용**한다.
  v001의 Blender 렌더 추출 방식은 사용자의 의도와 달랐던 초기 해석이다.
- built-in image_gen으로 새 공원 RGB와 투명 카페 RGBA PNG를 생성했다. 각 1672×941.
- 생성 자산 `assets/vvoori-cafe/v002/ai-autumn-park.png`, `ai-cafe-foreground.png`.
- Scene `Vvoori_Cafe_v002`, 카메라 `VC2_Camera`, 원본 `scenes/vvoori-cafe-v002.blend`.
- 생성 공원 → 차량/낙엽 3D → 생성 카페 순서로 합성. 차량/낙엽 62개 움직임과 기존 CG 모델 형태 유지.
- sRGB PNG에 추가 AgX 변환을 하지 않으며, 생성 알파는 합성 노드에서 정규화한다.
- 두 PNG를 원본 그대로 보존하고 pack했으며 **packed 바이트 SHA-256이 생성 PNG와 동일**함을 확인했다.
- 원본 1920×1080 / 24fps / 480프레임. 검토 영상은 **960×540 / 12fps / 240프레임 / 20초 / 무음**.
- 영상 `outputs/vvoori-cafe/v002/vvoori-cafe-review-20s.mp4`, 2,574,204바이트.
- Full HD 포스터 및 레이어 확인표·재생 페이지를 같은 결과 폴더에 저장했다.
- 전체 PNG 10개 정적 ROI 변화 0, MP4 전체 디코딩/시작끝 픽셀 일치, 애니메이션 끝점 오차 0 확인.
- 독립 원본 재개방과 실제 렌더 검증 완료. v001과 autumn-cafe 파일 해시 유지.
- 생성 프롬프트 `workflows/vvoori-cafe/v002-image-prompts.md`, 설명 `v002-README.md`.
- 마지막 제작 작업 `20261002T075428-8f68b62e50`, ok=true, 최종 미리보기 직접 확인.
- 다음 단계: 사용자 피드백. 고화질 1080p24 전체 MP4는 아직 출력하지 않았다.

<!-- VVOORI_CAFE_V002_END -->

# 이전 제작: vvoori-cafe v001 이미지 배경 + 3D 움직임

2026-10-02. 새 독립 프로젝트와 20초 검토 영상 생성·검증 완료.

- 요청: autumn-cafe의 공원과 카페·통창을 이미지로 처리하고 차량/낙엽만 Blender로 제작.
- 선택: Blender에서 이미지 2장 + 3D 움직임 합성. 음악/긴 반복/색보정은 필요할 때 Resolve 후반 작업.
- Scene `Vvoori_Cafe_v001`, 카메라 `VC_Camera`, 전용 원본 `scenes/vvoori-cafe-v001.blend`.
- `scenes/current.blend`에는 새 Scene과 기존 Scene을 함께 보존한다.
- 공원/카페 RGBA EXR 두 장은 pack. 객체 2,120개 → 289개, 정적 기하 제거, 움직임/재질/월드 독립 복사.
- 원본 설정 1920×1080 / 24fps / 480프레임 / 20초. Full HD 포스터 출력.
- **검토 영상은 960×540 / 12fps / 240프레임 / 20초 / 무음**이다. 고화질 1080p24 MP4는 미출력.
- 결과 `outputs/vvoori-cafe/v001/vvoori-cafe-review-20s.mp4`, `play-loop.html`, `layers-review.jpg`.
- 실제 240장 전체 9개 정적 ROI 변화 0, MP4 전체 디코딩·시작/끝 픽셀 일치 통과.
- 애니메이션 62개 시작/끝 변환 오차 0, 독립 원본 재개방·packed 합성 재렌더 통과.
- autumn-cafe 별도 원본과 영상 SHA-256 유지. 기존 미커밋 변경은 커밋에서 분리한다.
- 졸부의 실제 18개 도구/현지 문서 검토. Resolve 조작 또는 새 Resolve 프로젝트 생성은 하지 않았다.
- 제작·비교·재현·제한: `workflows/vvoori-cafe/README.md`.
- 마지막 브리찌 제작 작업 `20261002T072752-9707c22914`, ok=true, 미리보기 직접 확인.
- 다음 단계: 사용자 피드백에 따라 공원/카페 이미지를 교체하거나 1080p24 고화질 출력.
  현 버전은 기존 구도를 이미지로 분리한 것으로, 새 실사 이미지 제작본은 아니다.

<!-- VVOORI_CAFE_V001_END -->

# 이전 제작: 가을 공원을 바라보는 카페 20초 루프

2026-10-02. 브리찌로 **제작·출력·검증 완료**.

- 요청: 코지한 카페 통창 너머 가을 공원, 맑은 오후 3시, 좁은 도로의 불규칙 차량과 낙엽.
- Scene `Autumn_Cafe_v001`, 카메라 `AC_Camera`, 현재 원본 `scenes/current.blend`.
- 별도 완성 원본 `scenes/autumn-cafe-v001.blend`. 다른 PC에서는 이 파일을 명시하여 연다.
- 1920×1080 / 24fps / 480장 / 정확히 20초 / 무음. MP4의 첫·마지막 프레임 픽셀 동일 확인.
- 제작/재현 코드와 설명: `workflows/autumn-cafe/`.
- 영상: `outputs/autumn-cafe/v001/autumn-cafe-20s-loop.mp4` (10,455,437바이트).
- 같은 폴더에 반복 플레이어, 포스터, GIF, `verification.json`과 원본 검증 기록을 보관한다.
- 차량 6대와 낙엽 56개의 1/480프레임 변환 오차 0 확인.
- 정적 카페/공원은 160 samples의 packed EXR, 움직임은 32 samples로 분리 합성한다.
- PNG 480장 무결성·MP4 전체 디코딩 통과. 9개 정적 ROI는 모든 원본 프레임에서 변화 0.
- MP4 정적 ROI의 최대 프레임 평균 편차는 0.080/255 미만. H.264 고화질 QP 6 사용.
- 별도 원본을 새 Blender 프로세스에서 열어 pack, 카메라, 실제 움직임, 1/480 일치를 검증했다.
- 기존 장면은 현재 작업 파일에도 보존하며 기존 별도 원본 4개의 SHA-256이 유지됨을 확인했다.
- 다음 단계: 사용자 피드백. 현재 장면에 생성 스크립트 재실행 금지.
- 기존 별도 원본/출력과 아래 과거 기록은 보존한다. 기존 미커밋 변경은 이번 커밋에서 분리한다.

<!-- AUTUMN_CAFE_V001_END -->

# 현재 개발: Model Auto Routing

2026-10-02. 기존 브리찌를 유지하는 독립 Python 모델 라우팅 계층을 추가했다.

- 실제 기존 구조: Codex → CLI → 파일 큐 → bpy. MCP 서버/자체 LLM 호출은 없었다.
- 새 진입점: `python -m router route|run|chat|inspect-job`.
- `router/`: 설정·점수·모델 선택·상태·retry/escalation·로그/통계.
- `llm/`: Responses API. `adapters/`: 기존 CLI 호출, 코드 보존, 이미지 전달.
- `/model luna|sol|astra|auto`와 `--model` 지원. 기본 모델명/effort/문턱/한도는 JSON 설정.
- pending/부분 변경/렌더 실패를 구분하며 동일 변경을 자동 재실행하지 않는다.
- 실제 Blender 회귀는 `.runtime/`의 독립 사본에서 수행. 현재 제작 Scene은 보존한다.
- 실제 유료 LLM 호출 및 계정 모델 접근권은 검증하지 않았다. API 실행에는 환경변수 키가 필요하다.
- 기존 `bridge/`·실행 스크립트·기존 테스트·설정은 변경하지 않았다.
- 사용자 후속 지시로 이번 구현·문서·Git 마무리 규칙을 커밋·푸시한다. 이후 모든 작업도 검증 후 커밋·푸시와 원격 반영 확인까지 마무리한다.
- 사용법/구조/추가 파일/검증 범위: `docs/model-routing.md`.
- 작업 계획/실행 검증 기록: `docs/model-routing-plan.md`.
- 실제 Blender 검증 기록: `outputs/verification/router-smoke.json`, `router-preview.png`.
- 최종 `BLENDER_E2E=1` 전체 테스트 **58개 통과, skip 없음**. 로그: `outputs/verification/model-routing-tests.log`.

이 기능은 새 CLI에서 요청할 때만 적용된다. 현재 Codex 앱 대화 모델을 자동 전환하지 않는다.
아래 제작 작업 기록과 현재 원본 `scenes/current.blend`는 그대로 이어간다.

---

# 현재 작업 상태

기록일: 2026-09-10 (한국 시간). 실제 연결 여부는 매번 `status`로 확인한다.

## 사용자 목표

Blender를 잘 모르는 사용자가 Codex에게 말로 지시하여 결과물을 만들고, 옆의 Blender 창과 대화의 미리보기로 중간 결과를 확인한다. 도구·제작 코드·원본·작업 기록을 이 프로젝트에 저장하고 Git clone으로 다른 PC에서도 이어간다.

## 현재 작업: v007 추출된 심벌에서 더가치로 직접 확장

최신 사용자 수정: 기존 6초 영상에 붙이는 연결이 어색하므로, 집에서 ㄷ/ㅊ이 된 상태에서
바로 더가치 워드마크로 확장한다. **기존 영상 전체를 그대로 연결한다는 이전 요구를 대체한다.**

- 현재 Scene: `Thegachi_Opening_v007`, 원본 `scenes/current.blend`.
- 결과 폴더: `outputs/thegachi-opening/v007/`, 별도 원본 `scenes/thegachi-opening-v007.blend`.
- 전체 8초 / 192프레임 / 24fps / Full HD / 무음, 단일 Blender 애니메이션.
- 보행·손인사·추출 1~108프레임 유지. 108~156프레임에서 동일한 ㄷ/ㅊ 객체가 위치와 크기를 이어받아 글자로 확장, 156~192프레임 홀드.
- 축소 퇴장/재등장/기존 MP4 연결을 제거. 나머지 글자는 128~156프레임에 공간이 생긴 뒤 등장.
- 코드: 현재 v006에서 `17_direct_wordmark.py` → `18_refine_letter_reveal.py` → `05_render_master.py` → `06_package_video.py --version v007`.
- 연속성 검증: 기존 1~108프레임 객체 변환 및 카메라 배율 최대 오차 0, 추출 후 심벌 최소 배율 1.0으로 사라지는 구간 없음.
- **최종 출력 및 검증 완료**: `thegachi-opening-v007.mp4`, 1,737,494바이트. 192개 PNG 무결성/해상도, 8초/24fps/192프레임 및 MP4 전체 디코딩 통과.
- 완성 MP4에서 추출한 확장 화면과 6컷 스토리보드를 직접 확인.
- 마지막 렌더 작업: `outputs/jobs/20260909T162844-271134d890/`, `ok: true`.
- 검증: `video-verification.json`, `continuity-verification.json`, `previous-results-preservation.json`.
- 이전 v006 및 v002 원본/영상은 디스크에 보존한다. 이후 수정은 이 v007을 기준으로 한다.
- 소형 GIF 추가: `outputs/thegachi-opening/v007/thegachi-opening-v007-90x30.gif`, 90×30px / 8초 / 20fps / 무한 반복 / 60,042바이트.
- 전체 MP4를 비율 유지 53×30px로 축소하고 좌우 남색 여백으로 중앙 배치하여 크롭 없이 보존. 160프레임/8초/전체 디코딩과 확대 확인용 시트를 검사했다.
- 변환 코드: `19_export_small_gif.py`; 검증: `gif-90x30-verification.json`. MP4 원본 변경 없음.

## 이전 v006 걷기·손인사·심벌 추출과 본편 연결

최신 사용자 요청: 사람이 오른쪽에서 기준 그림의 위치까지 걸어와 머리 위로 손을 흔들고,
파란 집/노란 사람이 로고의 ㄷ/ㅊ으로 뽑혀 나온 뒤 기존 6초 영상으로 연결.

- 현재 Scene: `Thegachi_Opening_v006`; 원본 `scenes/current.blend`.
- 별도 원본: `scenes/thegachi-opening-v006.blend` (5초 신규 도입부 Scene).
- 결과 폴더: `outputs/thegachi-opening/v006/`.
- 신규 도입부 5초 + v002 원본 6초 = 총 11초, 24fps, Full HD, 무음.
- 코드: `12_walk_wave_extract.py` → `13_extraction_polish.py` → `15_transition_render_quality.py` → `16_visibility_review.py` → `05_render_master.py` → `14_join_original_master.py --version v006`.
- v005 시안의 보이지 않는 추출 객체가 그림자를 드리우던 문제를 등장 시점별 숨김으로 수정. v005 출력은 보존.
- 움직임 검증: 집 앞 도착 x=1.2, 보행 중 바닥 침범 없음, 손이 머리보다 높이 올라가는 파형 확인.
- **최종 출력 및 검증 완료**: `thegachi-opening-v006.mp4`, 2,260,831바이트, 1920×1080 / 24fps / 264프레임 / 11초 / H.264 / 무음.
- 기존 v002를 재인코딩 없이 스트림 복사로 연결. 원본 144개 디코딩 프레임 해시가 연결 영상의 후반 144개와 모두 동일하며 원본 파일 SHA-256도 유지.
- MP4 전체 디코딩 통과. 완성 영상에서 추출한 손인사·추출 화면과 6컷 스토리보드를 직접 확인.
- 검증 기록: `outputs/thegachi-opening/v006/video-verification.json`, `visibility-verification.json`. 보행 수치 검증은 동작이 같은 v005의 `motion-verification.json` 참조.
- 마지막 렌더 작업: `outputs/jobs/20260909T161731-c5af17357d/`, `ok: true`.
- 다음 단계: 완성된 v006을 기준으로 사용자 피드백 반영. 수정 출력은 새 버전으로 보존.
- v004 기준 그림과 v002 원본은 디스크에 보존한다.

## 이전 v004 집과 사람 기준 그림

사용자는 v003 결과가 전혀 마음에 들지 않는다고 명시했다. **v003은 채택되지 않은 시안**이다.
새 요청은 더가치 로고의 ㄷ과 닮은 집에 사람이 앞에 서 있는 그림을 먼저 만드는 것이다.
그 그림에서 브랜드의 ㄷ/ㅊ 심벌이 나와야 하며, **기존 v002의 6초 영상 전체는 그대로 연결**해야 한다.
v003의 정자 ㄷ/ㅊ 도입부나 기존 첫 프레임을 바꾼 연결 방식을 재사용하지 않는다.

- 먼저 제작하는 그림: 파란 집 프레임에 현관·창문·계단이 있고, 노란 재킷을 입은 사람이 집 앞 오른쪽에 서 있는 입체 미니어처.
- 코드: `workflows/thegachi-opening/09_house_person_picture.py`.
- Scene: `Thegachi_HousePerson_v004`; 최종 기준 원본: `scenes/thegachi-house-person-v004-final.blend`.
- 출력 폴더: `outputs/thegachi-opening/v004/`.
- 당시 단계: **기준 그림 렌더 및 시각 확인 완료**. 후속 연결 영상은 위 v006에서 완료.
- 최종 그림: `outputs/thegachi-opening/v004/house-person-picture-final.png` (1920×1080).
- 시각 QA: `10_picture_camera_review.py`에서 Y-up 장면의 카메라 수평을 바로잡고, `11_picture_finish.py`에서 겹친 계단 블록을 하나의 메시로 정리.
- 마지막 작업: `outputs/jobs/20260909T155621-4f958c3c31/`, `ok: true`. PNG 무결성과 v002 MP4 원본 해시 유지 확인.
- 후속 작업: 이 구도를 바탕으로 v006의 보행·손인사·심벌 분리 장면을 제작했다.
- 후반에는 v002 MP4를 재배치/재타이밍하지 않고 전체 6초를 연결하며, 원본 파일 해시를 검증한다.

## 채택되지 않은 v003 기록

최신 후속 요청: 집 그림과 사람 그림이 ㄷ/ㅊ으로 바뀌는 부분을 기존 영상 앞에 약 1초 추가.

- 현재 Scene: `Thegachi_Opening_v003`; 현재 원본: `scenes/current.blend`.
- 결과 원본: `scenes/thegachi-opening-v003.blend`.
- 결과 폴더: `outputs/thegachi-opening/v003/`; MP4: `thegachi-opening-v003.mp4`.
- 전체 길이: **7초 / 168프레임 / 24fps / 1920×1080 / 무음**.
- 새 도입부: 지붕·문·창문이 있는 집과 머리·팔다리가 있는 사람이 ㄷ과 ㅊ으로 변형된 뒤 기존 심벌에 연결.
- 수정 코드: `workflows/thegachi-opening/08_prepend_meaning_morph.py`.
- 기존 25–144프레임 → 새 49–168프레임: 매 프레임 객체 위치·회전·크기 오차 0으로 검증.
- **v003 최종 출력과 검증 완료**. 168개 PNG 해상도/무결성, H.264/yuv420p/24fps/7초, MP4 전체 디코딩 통과.
- 완성된 MP4의 ㄷ/ㅊ 화면과 6컷 스토리보드를 직접 확인했다.
- 기존 영상 대표 5프레임과 비교: 마지막 화면은 픽셀 단위 동일, 나머지는 극소수 채널에서 최대 1/255 차이만 관찰.
- 최종 영상 크기: 1,333,611바이트. 검증은 `video-verification.json`, `tail-image-comparison.json` 참조.
- 마지막 렌더 작업: `outputs/jobs/20260909T154325-8b51be9dd4/` (`ok: true`).
- v002 결과는 보존. 다음 수정 결과는 v004에 저장하며, 08번 스크립트를 현재 Scene에서 재실행하지 않는다.

## 이전 제작 v002 기록

2026-09-10 사용자 요청: 브리찌로 더가치 로고의 오프닝 영상을 단계적으로 제작.
사용자가 확인한 의미는 **파란 집 = 더의 ㄷ**, **노란 사람 = 치의 ㅊ**.
기존 프런트엔드의 실제 벡터 워드마크로 입체화했으며, 폰트로 대체하지 않았다.

- 원본: `scenes/current.blend`; 전용 Scene `Thegachi_Opening_v002`.
- 별도 결과 원본: `scenes/thegachi-opening-v002.blend`.
- 결과 폴더: `outputs/thegachi-opening/v002/`.
- 제작 코드·설계·재실행 지침: `workflows/thegachi-opening/README.md`.
- 원본 자산·색상·출처: `assets/thegachi/`.
- 구성: 집과 사람의 결합 심벌 → 펼쳐지는 더가치 워드마크 → 조명 이동 → 정면 홀드.
- 출력 설정: 6초, 24fps, 1920×1080, 무음 H.264 MP4.
- 진행: **v002 영상 출력과 검증 완료**. v001 시각 QA에서 발견한 초반 배경 겹침을 수정했으며, 전체 144프레임의 배경 간격도 검증했다.
- 최종 영상: `outputs/thegachi-opening/v002/thegachi-opening-v002.mp4` (1,162,653바이트).
- 마지막 이미지: `outputs/thegachi-opening/v002/final-logo.png`; 심벌: 같은 폴더의 `symbol-3d.png`.
- 검증: 144개 PNG 해상도/무결성, H.264/yuv420p/24fps/6초, MP4 전체 디코딩 통과. MP4에서 추출한 초반/심벌/완성 프레임 시각 검사.
- 마지막 렌더 작업: `outputs/jobs/20260909T153206-f050ee060a/` (`ok: true`).
- 검증 JSON: `outputs/thegachi-opening/v002/video-verification.json`, `clearance-verification.json`.
- 이전 데모 Scene 및 객체 보존. 외부 폰트/텍스처/애드온 의존 없음.
- Git 커밋·푸시는 이 제작 요청에 포함되지 않아 수행하지 않음.

다음 단계는 사용자 피드백에 따른 속도/두께/배경/조명 수정 또는 요청 시 효과음 추가다.
현재 납품본은 무음이며 실제 검증 환경은 Windows/Blender 5.2.1 LTS/RTX 3090이다.

후속 수정에서는 실제 Scene을 조회하고 위 README를 읽는다. 이미 만들어진 장면에
`01_build_logo.py`를 재실행하지 않고 대상 객체만 수정하며, 새 결과는 `v003` 등에 보존한다.

## 구현된 환경

로컬 파일 큐를 사용하는 Blender 연결, Windows 자동 탐색 실행기, 상태/장면/수정/저장/미리보기/연결 종료 CLI를 구성했다. 의존성은 Blender와 Python 표준 라이브러리다. 최초 설치 PC는 Blender 5.2.1 LTS, Windows에서 검증했다.

`AGENTS.md`에 후속 에이전트의 실행·백업·범위 보호·결과 확인 규칙이 있다. 새 세션에서는 이 파일의 상태를 사실로 단정하지 말고 CLI로 확인한다.

사용자 지정 이름은 **브리찌**다. 사용자의 메모리 요청은 Codex 메모리와 프로젝트 메모리에 함께 기록한다. `docs/memory/MEMORY.md`에 명칭과 기록 규칙을 저장했으며 `AGENTS.md`의 세션 시작 절차에서 필수로 읽도록 연결했다.

## 보존된 초기 시연 장면

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

각 작업에 실행 코드 사본, 요청/결과 JSON, 로그, 변경 전후 `.blend`, PNG를 저장했다. `outputs/latest.json`이 최신 미리보기를 가리킨다. 이후 제작은 사용자 요구에 맞춰 새 `workflows/<작업명>/` 코드를 추가한다. 초기 예제는 제어 시연이며, 현재 제작 주제는 위의 더가치 3D 오프닝이다.

## 다음 PC / 다음 대화

Blender 설치 → 저장소 clone → `Start-Blender.cmd` → `status`와 `scene` 확인 → 사용자 요청의 제작 진행. 이미 저장된 작업을 보려면 예제를 다시 만들지 말고 `start`로 현재 원본을 연다.

원격 저장소: `https://github.com/wooguylee/CodexBlender.git`, 기본 브랜치: `main`. 사용자의 추가 요청에 따라 초기 코드·문서·원본·미리보기를 Git으로 관리한다. `.runtime/`, PC별 경로 설정, 캐시는 제외한다. 동기화 상태는 `git status`와 원격 refs로 확인한다.

검증 상세는 `verification.md`, 설계는 `design.md`, 조작법은 루트 `README.md`를 참고한다.
