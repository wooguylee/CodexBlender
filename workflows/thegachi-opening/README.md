# 더가치 3D 오프닝 — 현재 v007 심벌에서 글자로 직접 확장

## v007: 걷기 → 손인사 → 추출 → 바로 더가치 확장

90×30px GIF 파생본: `19_export_small_gif.py` 실행 결과는
`outputs/thegachi-opening/v007/thegachi-opening-v007-90x30.gif`다.
전체 프레임을 53×30px로 축소하고 좌우 남색 여백에 중앙 배치하여 잘림을 방지한다.
8초 / 20fps / 160프레임 / 무한 반복 / 60,042바이트, 전체 디코딩 및 시각 확인 완료.
MP4 원본은 유지한다. 자세한 검증은 `gif-90x30-verification.json` 참조.

사용자는 v006에서 기존 영상에 맞추는 연결이 어색하다고 판단하여, 추출된 ㄷ/ㅊ 상태에서
곧바로 더가치로 펼치도록 요청했다. 기존 6초 영상 전체를 연결한다는 이전 제약은 이 요청으로 대체된다.

- 결과: `outputs/thegachi-opening/v007/thegachi-opening-v007.mp4`, 8초 / 192프레임 / Full HD / 24fps / 무음.
- 전체 애니메이션 원본: `scenes/thegachi-opening-v007.blend`.
- v006을 이어 `17_direct_wordmark.py` → `18_refine_letter_reveal.py` → `05_render_master.py` → `06_package_video.py --version v007` 실행.
- 1~108프레임 걷기/손인사/추출을 유지하며, 이후 같은 집과 사람 심벌이 156프레임까지 완성 글자의 위치와 크기로 이동한다.
- 나머지 원본 벡터 글자는 128~156프레임에 드러난다. 156~192프레임은 완성 로고 홀드.
- 단일 PNG 시퀀스를 인코딩한다. MP4 이어붙이기, 심벌 축소 퇴장 및 재등장 없음.
- `continuity-verification.json`: 앞 108프레임 변환/카메라 최대 오차 0, 추출 후 최소 심벌 배율 1.0.
- 이전 원본과 영상은 보존한다. 17번 스크립트는 v006에서 시작해야 하며 v007에 재실행하지 않는다.

최종 출력 및 검증 완료: 1,737,494바이트, 192개 PNG 무결성/해상도 및 MP4 전체 디코딩 통과.
완성 MP4에서 추출한 확장 장면과 6컷 스토리보드를 직접 확인했다.
렌더 작업은 `outputs/jobs/20260909T162844-271134d890/`, `ok: true`.
결과 SHA-256은 `38a4eafaef503cbb7b82ed67f19e629ff5e785bca9d01cd5ee836ff6668b8079`.
v002/v006 MP4 파일 해시 유지도 확인했다. 자세한 결과는 v007의 `video-verification.json`,
`continuity-verification.json`, `previous-results-preservation.json` 참조.

## v006: 걸어오기 → 머리 위 손인사 → 로고 추출

사용자가 v004 집/사람 그림을 바탕으로 사람이 오른쪽에서 현재 위치까지 걸어와 머리 위로
손을 흔들다가 ㄷ/ㅊ 심벌로 추출되고 기존 영상으로 이어지는 동작을 요청했다.

- 새 도입부: 120프레임/5초. 걷기 약 2초, 머리 위 손인사, 마지막 약 1.3초 심벌 추출과 연결.
- 뒤의 v002 144프레임/6초는 원본 MP4를 **재인코딩하지 않고 스트림 복사**한다.
- 최종 결과: `outputs/thegachi-opening/v006/thegachi-opening-v006.mp4`, 264프레임/11초.
- 새 도입부 원본: `scenes/thegachi-opening-v006.blend`.
- 기존 본편 원본: `scenes/thegachi-opening-v002.blend` 및 같은 버전 MP4.
- 코드는 `12_walk_wave_extract.py`, `13_extraction_polish.py`, `15_transition_render_quality.py`,
  `16_visibility_review.py`, 공통 `05_render_master.py`, `14_join_original_master.py --version v006` 순서다.
- 완성 MP4의 뒤 144프레임과 v002의 모든 디코딩 프레임 해시가 동일해야 검증을 통과한다.
- v004 그림과 v002 원본은 보존한다. 현재 Scene에 12번 도입부 제작 스크립트를 재실행하지 않는다.

보행은 바닥을 침범하지 않도록 발 높이를 보정하고, 머리 위 손인사는 어깨·팔꿈치를 분리하여
회전시켰다. 정지 위치는 기준 그림의 x=1.2다. 집은 실제 건축 프레임이 앞으로 빠져나오며
얇은 브랜드 심벌로 바뀌고, 사람 위치에서 원본 노란 ㅊ 윤곽이 나온다.
투명 전환의 그림자/중첩 설정을 조정하고 전환 구간만 256샘플로 렌더한다.
v005 완성 영상 검사에서 발견한 비가시 추출 객체의 그림자는 16번 스크립트로 수정했다.
등장 전 로고와 배경을 숨기고, 사라진 사람/건축물도 렌더에서 제외한다. v005는 중간 시안으로 보존한다.

연결용 도입부의 마지막 한 프레임은 v002의 첫 원본 PNG로 맞춰 배경 단절을 줄인다.
이전 Blender 렌더 프레임은 `seam/intro-rendered-last.png`에 별도로 보관하며 본편은 건드리지 않는다.

### v006 최종 검증 (2026-09-10)

- Full HD / 24fps / 264프레임 / 11초 / H.264 / 무음, 2,260,831바이트.
- 원본 v002 파일 SHA-256 유지 및 연결 영상 후반 144개 디코딩 프레임 전체 동일.
- 완성 MP4 전체 디코딩, 120개 도입부 PNG 무결성과 해상도 검사 통과.
- 완성 MP4에서 추출한 머리 위 손인사·심벌 추출 화면 및 스토리보드 직접 확인.
- 렌더 작업: `outputs/jobs/20260909T161731-c5af17357d/`, `ok: true`.
- 결과 SHA-256: `609eb999be624116c43e2f2445ac9d69579a2b0561ade2688bf1625327715f7a`.
- 자세한 수치: `outputs/thegachi-opening/v006/video-verification.json` 및 `visibility-verification.json`.
- `.blend`는 새 5초 도입부 원본이며, 뒤 6초는 보존된 v002와 `concat.txt`로 연결한다.

## v004 기준 그림 기록

## 최신 사용자 방향 수정

사용자가 v003을 거절했다. v003은 채택되지 않은 시안으로 보존하며 재사용하지 않는다.
요청은 **더가치 로고의 ㄷ과 비슷한 집과 그 집 앞에 사람이 서 있는 그림을 먼저 제작**하는 것이다.
그 장면에서 로고의 ㄷ/ㅊ이 나오고 **원래 v002의 6초 영상 전체를 그대로** 연결해야 한다.
분리된 막대 아이콘, 정자 ㄷ/ㅊ을 별도로 보여주는 v003 방식은 요구와 맞지 않는다.

`09_house_person_picture.py`는 별도 Scene에서 원본 집 벡터 윤곽을 건축 프레임으로 확장하고,
현관·유리창·계단·화분 및 노란 재킷을 입은 사람을 배치한다. 사람이 집 앞에 서 있는 하나의 구도다.
최종 그림은 `outputs/thegachi-opening/v004/house-person-picture-final.png`, 원본은
`scenes/thegachi-house-person-v004-final.blend`에 저장한다. 이 단계는 영상이 아닌 **기준 그림**이다.
10번 스크립트로 Y-up 장면의 카메라 수평을 정렬하고, 11번 스크립트로 겹친 계단 블록을 단일 메시로 수정했다.
Full HD 그림을 직접 검사했으며 PNG 무결성과 v002 MP4 해시 유지도 검증했다.
최종 작업은 `outputs/jobs/20260909T155621-4f958c3c31/`, `ok: true`다.
후속 심벌 추출/연결은 이 기준 그림을 먼저 보여준 뒤 진행한다.

v002 6초 원본의 SHA-256 기준:
`88f565048f0e29ae0ab3d4246d29f93a0d8c78ab47260cf657e421c3d105b41a`.
후반 영상 자체를 수정하거나 처음 1초를 재구성하지 않는다.

## 채택되지 않은 v003 기록

## v003: 집·사람 그림이 ㄷ·ㅊ으로 바뀌는 도입부

2026-09-10 후속 요청: 현재 영상 앞부분에 집과 사람이 ㄷ/ㅊ으로 바뀌는 구간을 약 1초 추가.
`08_prepend_meaning_morph.py`로 지붕·벽·문·창문이 있는 집과 머리·몸통·팔다리가 있는 사람을
프로젝트 안에서 직접 만들었다. 지붕이 수평으로 펴지고 오른쪽 벽/문/창문이 사라져 ㄷ이 되며,
사람 머리가 짧은 획이 되고 팔·다리가 이동해 ㅊ이 된다. 이 형태를 기존 브랜드 심벌로 연결한다.

- 24프레임 추가: **168프레임, 24fps, 7초**. Full HD, 무음.
- 1–5프레임: 집/사람 그림. 5–16프레임: 자음으로 변화. 16–18프레임: ㄷ/ㅊ.
- 18–26프레임: 브랜드 심벌로 전환. 기존 첫 등장 동작의 연결 부분은 자연스럽게 조정.
- 기존 25–144프레임은 새 49–168프레임으로 이동. 객체 위치/회전/크기를 프레임별로 검사했고 최대 오차 0.
- v002 원본·영상·프레임 보존. 새 Scene은 `Thegachi_Opening_v003`.
- 결과: `outputs/thegachi-opening/v003/thegachi-opening-v003.mp4`.
- 원본: `scenes/thegachi-opening-v003.blend`, 현재 작업본 `scenes/current.blend`.
- 변환 미리보기: `outputs/thegachi-opening/v003/storyboard/frame-001.png`, `frame-018.png`.
- 검증: 같은 폴더의 `prefix-verification.json`, `render-result.json`, `video-verification.json`.

실행: v002 Scene에서 `08_prepend_meaning_morph.py` → `05_render_master.py` →
`python workflows/thegachi-opening/06_package_video.py --version v003`.
앞의 두 스크립트는 기존과 같이 브리찌 `run --script ...`로 실행한다.
현재 제작된 Scene에 도입부 스크립트를 재실행하지 않는다. 후속 변경은 v004에 저장한다.

v003 검증 완료: 168개 PNG 무결성/Full HD, 24fps, 7초, H.264/yuv420p, MP4 전체 디코딩 통과.
MP4에서 추출한 ㄷ/ㅊ 화면과 실제 프레임 스토리보드를 확인했다.
기존 구간 대표 5프레임 비교에서 마지막 로고는 픽셀 단위 동일했고, 나머지 프레임도 극소수 채널의
최대 1/255 차이만 있었다. `tail-image-comparison.json`에 수치를 보존했다.
영상 크기 1,333,611바이트, SHA-256:
`6f4b4cef7458d808062f4c076a197e0992f9d784f54a7070448dd6b7b002adda`.
최종 렌더: `outputs/jobs/20260909T154325-8b51be9dd4/`, `ok: true`.
이번 수정에서 외부 자산 다운로드, Git 커밋·푸시는 수행하지 않았다.

## 이전 v002 기록

첫 전달 버전은 **v002**다. v001의 시각 QA에서 초반 회전 장면의 집 일부가
배경면(z=-0.65) 뒤에 들어가는 현상을 발견했다. `07_backdrop_clearance.py`로 원인을 계측하고,
배경 색은 유지한 채 면만 z=-4로 옮겼다. 전체 144프레임에서 최소 간격 2.626을 확인했다.
v001 결과/원본/프레임은 비교용으로 보존한다.

## 사용자 요청과 디자인

2026-09-10: 브리찌를 사용해 기존 더가치 로고를 오프닝 영상으로 단계적으로 제작한다.
사용자가 설명한 의미는 **파란 집 = 더의 ㄷ**, **노란 사람 = 치의 ㅊ**이다.
앞선 대화에서 노란 모양을 별이라고 설명한 것은 잘못이며, 이 제작에서는 사람으로 해석한다.

기존 프로젝트의 `Front/src/compo/ThegachiTypo.jsx`에서 실제 워드마크 6개 벡터 경로를 추출했다.
새 글꼴로 대체하지 않는다. 원본 파란 그라디언트 `#036eb8 → #171c61`,
노란색 `#f9b341`, 회색 `#b5b5b6`를 재질의 기준 색으로 사용한다.
3D 조명과 AgX 색 변환 때문에 렌더의 픽셀 값은 평면 로고 색상과 달라진다.
웹 UI에 사용된 흰색 1px 외곽선은 제외하고, 실제 채워진 벡터 형태에 두께와 작은 모서리 곡면을 준다.

처음 등장하는 결합 심벌은 사용자가 확인한 `logoThegachi.png`의 상대 배치를 참고해
워드마크의 집과 사람 벡터를 각각 확대·배치한 것이다. 저해상도 PNG를 픽셀 단위로 복제한 것은 아니다.
완성되는 워드마크는 기존 SVG 경로와 원래 배치에 정확히 대응한다.

## 구성

| 시간 | 동작 |
|---|---|
| 0–1.25초 | 입체 집과 사람이 서로 다른 방향에서 등장해 심벌을 구성 |
| 1.25–1.8초 | 결합된 심벌을 잠깐 보여줌 |
| 1.8–3.6초 | 집과 사람이 양옆으로 펼쳐지고 나머지 글자가 합류 |
| 3.6–5초 | 완성된 워드마크 위로 조명이 이동 |
| 5–6초 | 정면 로고를 고정해 다음 영상과 연결할 여유 확보 |

짙은 남색 배경, 파란색/노란색의 코팅 재질, 은색 글자.
1920×1080, 24fps, 144프레임, 6초, H.264 MP4, 무음.
음원·효과음은 이 버전에 포함하지 않는다.

## 결과 위치

- 영상: `outputs/thegachi-opening/v002/thegachi-opening-v002.mp4`
- 마지막 화면: `outputs/thegachi-opening/v002/final-logo.png`
- 심벌 화면: `outputs/thegachi-opening/v002/symbol-3d.png`
- 6컷 스토리보드: `outputs/thegachi-opening/v002/storyboard.png`
- 원본 프레임: `outputs/thegachi-opening/v002/frames/0001.png`–`0144.png`
- 별도 Blender 원본: `scenes/thegachi-opening-v002.blend`
- 현재 작업 원본: `scenes/current.blend`
- 검증: 같은 출력 폴더의 `keyframe-verification.json`, `render-result.json`, `video-verification.json`

## 단계별 실행 코드

1. `prepare_sources.py`: 로컬 원본 경로를 인수로 받아 `assets/thegachi/`에 자산/출처/해시 보존.
2. `01_build_logo.py`: 원본 SVG 경로로 입체 곡선 생성. 이전 Scene은 보존하고 새 전용 Scene 생성.
3. `02_material_lighting.py`: 기본 재질·스튜디오 조명.
4. `03_animate_opening.py`: 최종 색감·배경 조정, 6초 애니메이션과 타임라인 마커.
5. `04_review_keyframes.py`: 주요 장면 렌더와 완성 위치/원본 Scene 보존 확인.
6. `05_render_master.py`: Full HD 프레임 렌더, 별도 원본 저장.
7. `06_package_video.py`: 로컬 FFmpeg 인코딩, 전체 디코딩, 프레임/시간/코덱 검사, 미리보기 정리.
8. `07_backdrop_clearance.py`: v001 원본에서 배경 간격을 계측/수정하고 v002 주요 프레임 재검증.
   이후 `05_render_master.py`를 다시 실행하고 `python workflows/thegachi-opening/06_package_video.py --version v002`로 패키징.

Blender용 단계는 프로젝트 루트에서 다음 형식으로 실행한다.

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File scripts/blender.ps1 run --script workflows/thegachi-opening/01_build_logo.py --label "더가치 1단계 입체화"
```

완성된 Scene에서 1단계를 다시 실행하지 않는다. 스크립트에는 기존 Scene/출력 덮어쓰기 방지 검사가 있다.
후속 수정은 실제 Scene/객체를 확인하고 새 단계 스크립트와 `v003` 등 새 출력 폴더를 사용한다.
Blender 코드의 공유 경로는 `PROJECT_ROOT`와 상대 경로만 사용한다.
패키징 도구는 시스템의 Python/Pillow 및 FFmpeg/ffprobe를 필요로 한다.
장면 자체는 외부 폰트·텍스처·애드온 없이 열린다.

## 보존과 검증 범위

전용 Scene: `Thegachi_Opening_v002`. 주요 객체: `TG_house_d`, `TG_person_ch`,
`TG_eo`, `TG_g`, `TG_a`, `TG_i`, `TG_LogoRig`, `TG_Camera`.
초기 시연 Scene 및 객체를 삭제하지 않는다. 브리찌가 각 단계의 변경 전후 `.blend`와 실행 코드를
`outputs/jobs/`에 보존한다. 원본 데모와 출력 파일을 덮어쓰지 않는다.

실제 검증 환경은 Windows, Blender 5.2.1 LTS, NVIDIA RTX 3090, EEVEE.
브리찌 도구 코드는 변경하지 않았다. 도구 단위테스트 대신 실제 제작 Scene과 렌더/영상 출력을 검증한다.
이 작업에서 외부 다운로드, 업로드, 애드온 설치, Git 커밋·푸시는 수행하지 않는다.

최종 v002 검증 완료: 144개 PNG 무결성/1920×1080, 24fps, 6초, H.264/yuv420p,
MP4 전체 디코딩 통과. MP4에서 추출한 등장/심벌/완성 화면도 직접 확인했다.
영상 크기 1,162,653바이트. SHA-256:
`88f565048f0e29ae0ab3d4246d29f93a0d8c78ab47260cf657e421c3d105b41a`.
최종 렌더 작업은 `outputs/jobs/20260909T153206-f050ee060a/`이며 `ok: true`다.
자세한 실행 결과는 출력 폴더의 JSON을 기준으로 확인한다.
