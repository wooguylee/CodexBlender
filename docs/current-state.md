<!-- WEATHER_RIGS_V001_BEGIN -->
# 현재 제작: 오늘의 날씨 요정들 — 다섯 캐릭터 맞춤 리깅

2026-10-06 (한국 시간). 사용자 요청: 기존 영상의 오디오 제작 방법 설명과 추천 리깅 실제 적용.

- 중립 원본 `scenes/weather-rigs-v001.blend`, Scene `Weather_Rigs_v001`. 총 5개 Armature / 142개 뼈 / 149개 스키닝 메시 / 124개 유효 driver. 별도 설치나 외부 이미지·폰트·모델 의존성 없음.
- 공통: 손발 두 관절 IK, 몸 이동/회전과 눌림·늘림, 눈 뜨기/깜빡임/미소/놀란 입. 색상과 모양이 다른 조작 컨트롤을 표시하고 내부 변형/보조 뼈는 Bone Collections에서 숨겨 두었다.
- 몽실: 숨쉬기·안기·별 쿠션. 해롱: 햇살 흔들기·펼치기. 또르: 물방울 꼭지 휘기. 송송: 눈 결정 접기. 솔솔: 몸/소용돌이 휘기·스카프 흔들기.
- 시연 원본 `scenes/weather-rig-demo-v001.blend`, Scene `Weather_Rig_Demo_v001`. 새 컨트롤의 실제 키프레임 282개 curve를 재개방해 384프레임 전체 렌더.
- 최종 `outputs/weather-rigs/v001/weather-rig-demo-16s.mp4`: 1920×1080 / 24fps / 16초 / 무음 / 한국어 조작 설명. 기본 자세→손발 IK→표정→몸/특수 동작→쿠션/스카프 순서다.
- 독립 원본의 모든 메시 가중치와 연결, 20개 손발 IK, 표정/특수 조절의 실제 변형 검사를 통과했다. 기본 자세 점 차이 최대 약 0.0000022, IK 끝 관절 목표 오차 최대 약 0.000032 Blender 단위.
- 모든 PNG와 MP4 전체 디코딩 통과. 고정 배경 5곳은 전체 프레임에서 채널 차이 0. 기본/복합 자세와 완성 영상 추출 6개 시점을 직접 시각 검사했다. 해롱 햇살 펼침 범위는 −0.10–0.12로 줄여 과도한 늘림을 방지했다.
- 이전 별도 원본/영상 33개 SHA-256 동일, 과거 커밋의 날씨 요정 관련 자산 72개 Git blob 일치. 기존 다섯 코미디 영상은 보존하며, 새 리그로 자동 변환하지 않았다.
- 기존 오디오는 `workflows/weather-shorts/06_package_movies.py`에서 Python/NumPy로 직접 합성한 음악과 효과음이다. 5음계 멜로디/저음/잡음 타악기와 사건 시각별 효과음을 48kHz 스테레오 WAV로 만든 후 AAC 160kbps로 영상에 합성했다. 성우/실제 악기 녹음이나 외부 AI 음악 서비스 사용 없음.
- 사용법·값별 의미·재현·검증 기록: `workflows/weather-rigs/README.md`. `outputs/weather-rigs/v001/rig-verification.json`, `output-verification.json`, `final-delivery.json`에 실제 검사 결과를 기록했다.
- 현재 브리찌 화면: `Weather_Rigs_v001`, frame 1, 다섯 Armature의 Pose Mode, 몽실 `CTRL_Body` 선택. 최종 작업 `20261005T212745-fca02a82f8`, `ok=true`와 카메라 미리보기 확인.
- Windows / Blender 5.2.1 LTS / RTX 3090에서 검증. 후속 애니메이션은 중립 원본을 복사하여 새 버전으로 작업한다. 이번 관련 파일과 이 추가 기록만 커밋/푸시하며 무관한 기존 미커밋 변경은 유지한다.

<!-- WEATHER_RIGS_V001_END -->

<!-- WEATHER_SHORTS_V001_BEGIN -->
# 현재 제작: 오늘의 날씨 요정들 — 코미디 단편 5편

2026-10-06 (한국 시간). 사용자가 승인한 다섯 시나리오를 실제 Blender 애니메이션으로 제작했다.

- 1편 단체사진 대소동 24초, 2편 몽실의 별 쿠션을 잡아라 30초, 3편 꽃 한 송이 키우기 32초, 4편 오늘의 날씨는 누구? 28초, 5편 절대 터뜨리면 안 돼! 26초.
- 전체 140초 / 3,360프레임. 각 편 1920×1080 / 24fps / H.264 + AAC 스테레오, 한국어 자막과 직접 합성한 음악·효과음 포함.
- 편집 원본은 `scenes/weather-short-01-v001.blend`부터 `weather-short-05-v001.blend`까지. 각 파일의 독립 Scene·캐릭터·소품·키프레임을 재개방해 실제 전체 렌더했다. 외부 모델/텍스처/글꼴 의존성 없음.
- 최종 영상은 `outputs/weather-shorts/v001/01-photo-chaos/`부터 `05-bubble-hats/`까지 편별 폴더의 같은 이름 MP4. 모든 실제 렌더 PNG와 WAV·수정 전 원본은 로컬에 보존한다.
- 모든 3,360 PNG 디코딩·알파·해상도 확인, 5개 MP4 전체 디코딩 및 프레임 수/재생시간 검사 통과. 각 편 오디오 피크 0.272–0.299로 clipping 없음.
- 각 편의 고정 배경 5개 ROI를 모든 해당 프레임에서 비교해 채널 변화 0. 4편 23초 이후는 몽실이 화면을 채우는 의도된 장면이므로 고정 영역 비교 제외.
- 최종 MP4의 사건별 추출 장면과 원본 대표 프레임을 직접 시각 검사했다. 초안의 거품 대비와 동작 경계의 위치 점프를 수정하고 이동 데이터로 재검증했다.
- 제작 전 별도 원본 22개의 SHA-256 동일. 기존 제작 Scene과 무관한 미커밋 작업은 유지한다. 이번 반영에는 전용 원본/최종 영상/검증 기록/작업 코드와 이 추가 기록만 포함한다.
- 모아보기 경로: `outputs/weather-shorts/v001/weather-fairies-five-stories.mp4`; 결과표 `five-stories-contact.png`; 편별 종합 검증 `verification-summary.json`.
- 현재 브리찌 화면: `Weather_Short_05_v001`, frame 577, `WS5_Camera`. 최종 작업 `20261005T205423-8a7953eee0`, `ok=true`와 카메라 미리보기 확인.
- 제작/재현/제한 설명: `workflows/weather-shorts/README.md`. 수학적으로 구성한 연기와 소품 동작이며 유체/천 물리 시뮬레이션은 아니다. Windows / Blender 5.2.1 LTS / RTX 3090에서 검증.
- 다음 단계는 사용자 감상 후 연기·길이·자막·음악 등의 수정이다. 현재 다섯 편과 캐릭터 원본은 보존하고 후속 수정은 새 버전으로 진행한다.

<!-- WEATHER_SHORTS_V001_END -->

<!-- WEATHER_FAIRIES_V002_BEGIN -->
# 현재 제작: 오늘의 날씨 요정들 v002 — 눈송이 송송·바람 솔솔 추가

2026-10-06 (한국 시간). 사용자가 요청한 눈송이·바람 캐릭터와 5인조 단체 시안 제작·검증 완료.

- 송송: 둥근 육각 얼굴, 6개 결정 축과 12개 가지, 윙크, 보라 장갑/신발.
- 솔솔: 몸과 이어지는 민트색 소용돌이, 오므린 입, 휘날리는 살구색 스카프, 한 발을 든 포즈.
- 기존 몽실·해롱·또르의 형태를 유지한 독립 복제본에 추가했다. v001 Scene/원본/결과는 보존한다.
- Scene `Weather_Fairies_v002`, 카메라 `WF2_Camera`, 객체 179개, 캐릭터 컬렉션 5개.
- 독립 원본 `scenes/weather-fairies-v002.blend`, 2,829,952바이트. 외부 이미지/모델/폰트 의존성 없음.
- `outputs/weather-fairies/v002/weather-fairies-five.png`, `weather-fairies-five-clean.png`: 3200×1600.
- 같은 폴더 `snow-and-wind.png`: 2160×1440. `songsong.png`, `solsol.png`: 각각 1080×1080.
- 단체/신규 듀오/개별 2장의 실제 렌더를 직접 검사. 독립 원본 재개방·재렌더 성공, 최대 채널 차이 1/255.
- 최종 5장 PNG 무결성·해상도·알파 확인. 기존 Scene 14개 보존, 원본/이미지 27개 SHA-256 동일.
- 최종 브리찌 작업 `20261005T195131-9eac873606`, `ok=true` 및 카메라 미리보기 확인.
- 제작/재현/검증 설명: `workflows/weather-fairies/v002-README.md`, 결과 폴더 `output-verification.json`.
- 정지 캐릭터 시안이며 뼈대 리깅/애니메이션은 아직 없다. 다음 단계는 사용자 피드백에 따른 새 버전 수정이다.
- 이번 전용 파일과 상태 기록의 추가분만 Git에 반영하고 기존 무관한 미커밋 변경은 유지한다.

<!-- WEATHER_FAIRIES_V002_END -->

<!-- WEATHER_FAIRIES_V001_BEGIN -->
# 현재 제작: 오늘의 날씨 요정들 v001 — 몽실·해롱·또르

2026-10-06 (한국 시간). 첫 3D 캐릭터 시안·단체/개별 이미지 제작과 검증 완료.

- 사용자 요청: 추천 주제 ‘오늘의 날씨 요정들’을 추천안으로 먼저 제작.
- 몽실: 졸린 구름, 별 쿠션, 보라 슬리퍼. 해롱: 손인사하는 햇살. 또르: 두 손을 모은 수줍은 빗방울.
- 전용 Scene `Weather_Fairies_v001`, 카메라 `WF1_Camera`, 객체 103개. 캐릭터별 컬렉션/Root Empty 분리.
- 편집 가능한 전용 원본: `scenes/weather-fairies-v001.blend` (1,233,950바이트).
- 단체 `outputs/weather-fairies/v001/weather-fairies-group.png`, 글자 없는 단체 `weather-fairies-clean.png`: 각각 2160×1440.
- 개별 `mongsil.png`, `haerong.png`, `ttorr.png`: 각각 1080×1080.
- Blender 메시·곡선·재질·기본 내장 글꼴만 사용. 외부 이미지/모델/폰트 의존성 없음.
- 실제 단체와 개별 3장을 직접 시각 검사. 독립 Blender 재개방/재렌더 성공, 원본과 최대 채널 차이 1/255.
- 5장 PNG 무결성·해상도·불투명 알파 확인. 기존 Scene 13개의 객체/변환/카메라 보존, 별도 원본 20개 SHA-256 유지.
- 최종 브리찌 작업 `20261005T192611-7801a0835c`, `ok=true` 및 카메라 미리보기 확인.
- 코드·재현·검증: `workflows/weather-fairies/README.md`; 결과 폴더의 `output-verification.json`.
- 정지 캐릭터 시안이다. 뼈대 리깅/애니메이션과 네 번째 눈송이 캐릭터는 아직 제작하지 않았다.
- 다음 단계: 사용자 피드백에 따라 표정·비율·색 수정 또는 움직임 제작. 기존 결과는 보존하고 새 버전으로 진행한다.
- 기존 미커밋 장면/변경은 유지하며, 이번 Git 반영은 전용 원본·결과·코드와 이 기록의 추가분으로 한정한다.

<!-- WEATHER_FAIRIES_V001_END -->

<!-- VVOORI_CAFE_WINTER_V001_BEGIN -->
# 현재 제작: vvoori-cafe-winter v001 — 겨울 공원과 통창 카페

2026-10-02. 새 이미지 생성·Full HD 전체 렌더·독립 원본 검증 완료.

- 공원 RGB와 가구/창 외곽 테두리 포함 실내 RGBA를 built-in image_gen으로 각각 새로 생성했다.
- 생성 원본 두 장은 `assets/vvoori-cafe-winter/v001/`, 각 1672×941. 원본 PNG를 그대로 보존하고 pack했다.
- 합성은 공원 → 실제 Blender 차량 6대/눈 280개 → 실내 이미지. 정적 실내 3D나 렌더 캐시는 없다.
- 전용 원본 `scenes/vvoori-cafe-winter-v001.blend`, Scene `Vvoori_Cafe_Winter_v001`, 카메라 `VWC1_Camera`, 객체 527개.
- 실제 카메라 수평각 약 50도, 차도 접지 7,289개 표본 검사. 차량 순환은 화면 밖/벽 뒤, 눈 순환은 화면 위/아래 밖이다.
- 완성 영상 `outputs/vvoori-cafe-winter/v001/vvoori-cafe-winter-20s.mp4`: **1920×1080 / 24fps / 480프레임 / 정확히 20초 / 무음**.
- 모든 480프레임을 실제 렌더했다. 주기는 480프레임으로, frame 481=frame 1이다. 마지막 프레임을 첫 프레임으로 복제하지 않았다.
- 모든 PNG의 14개 실내 ROI 변화 0. 불투명 실내 944,831픽셀 전체 검사에서는 480장 중 총 3개의 단일 픽셀/채널에만 최대 1/255 양자화 차이가 있었다. MP4 전체 디코딩과 사양 검사 통과.
- 별도 Blender 프로세스에서 외부 이미지 경로를 의도적으로 끊고 packed 자산만으로 재렌더한 결과가 최종 PNG와 픽셀 동일.
- 최초 검사의 화면 상단 한 줄 alpha 문제는 Scale 노드 Clip→Extend로 보정하고 480장 전체를 재렌더했다.
- 기존 vvoori-cafe 원본/MP4 10개 SHA-256 유지. 기존 장면과 무관한 미커밋 변경 보존.
- 제작·프롬프트·검증 설명: `workflows/vvoori-cafe-winter/README.md`, `v001-*-verification.json`.
- 최종 포스터/반복 재생: `outputs/vvoori-cafe-winter/v001/poster-fullhd.png`, `play-loop.html`.
- 다음 단계: 사용자 피드백. 수정 시 이 v001을 기준으로 새 버전에 저장한다. Windows/RTX 3090 외 환경은 미검증.

<!-- VVOORI_CAFE_WINTER_V001_END -->

# 현재 제작: vvoori-cafe v005 — 창 프레임도 카페 이미지, 넓은 통창

2026-10-02. 사용자 요청 반영, 전체 영상과 독립 원본 검증 완료.

- 요청: **창 프레임은 Blender로 넣지 않고 필요하면 카페 이미지에 포함. 통창에 맞게 구성.**
- built-in image_gen으로 실내를 편집해 창 안쪽 세로 기둥/격자를 없애고 바깥 테두리만 이미지에 포함했다.
- 자산 `assets/vvoori-cafe/v005/ai-panoramic-interior.png`, RGBA 1672×941. 가구와 50도 사선 구도 유지.
- 이전 세로 프레임 위치의 이미지 alpha가 0임을 확인해 외부 시야가 막히지 않게 했다.
- v005에는 3D 창틀/창턱/가구가 없다. 창틀 렌더 캐시 및 해당 합성 노드도 제거했다.
- Blender의 실제 렌더 기하는 차량 6대와 낙엽 56개뿐이다. 공원은 v003 생성 PNG 재사용.
- 합성: 공원 이미지 → 차량/낙엽 3D → 통창/테두리/가구 포함 실내 이미지.
- 전용 원본 `scenes/vvoori-cafe-v005.blend`, Scene `Vvoori_Cafe_v005`, 카메라 `VC5_Camera`, 객체 285개.
- 컬렉션 `VC5_Traffic` / `VC5_Leaves` / `VC5_Rig`, 뷰 레이어 `VC5_Motion`, 합성 이미지 두 장 pack.
- 영상 `outputs/vvoori-cafe/v005/vvoori-cafe-toon-20s.mp4`: **1920×1080 / 24fps / 480프레임 / 20초 / 무음**.
- 전체 프레임의 12개 실내 고정 영역 변화 0, MP4 전체 디코딩 정상, 시작/끝 픽셀 동일.
- 독립 Blender에서 원본 재개방/렌더, 두 생성 이미지 packed SHA-256, 62개 애니메이션 끝점 검증 완료.
- 이전 v004 원본/영상과 v003 원본 해시 유지. 생성 이미지·원본·영상·포스터·재생 페이지와 코드는 Git 포함.
- 제작·프롬프트·실측 보고서: `workflows/vvoori-cafe/v005-README.md`, `v005-image-prompt.md`, `v005-verification-summary.json`.
- 다음 단계: 사용자 피드백. 고정 카메라용 구성이며 창/테두리/가구 수정은 실내 이미지에서 처리한다.

- 통합 제작 프롬프트: `workflows/vvoori-cafe/vvoori-cafe-one-shot-prompt.txt`. 파일 전체를 한 번의 요청으로 전달하여 이미지 생성·3D 움직임·20초 출력·검증을 진행할 수 있도록 작성했다. 기존 픽셀과 완전히 동일한 재생성을 보장하는 것은 아니다.

- 겨울 파생 프로젝트 프롬프트: `workflows/vvoori-cafe-winter/vvoori-cafe-winter-one-shot-prompt.txt`. 50도 사선 통창·가구 포함 실내 이미지는 유지하고 눈 덮인 공원·겨울빛·Blender 자동차와 눈발로 변경했다. 현재는 프롬프트만 작성했으며 겨울 이미지·장면·영상은 아직 제작하지 않았다.

<!-- VVOORI_CAFE_V005_END -->

# 이전 제작: vvoori-cafe v004 — 테이블과 의자도 실내 생성 이미지

2026-10-02. 사용자 요청에 따라 가구 이미지 교체·전체 영상·원본 검증 완료.

- 요청: **실내 테이블과 의자도 실내 이미지로 만든다.**
- built-in image_gen으로 v003 실내를 편집하여 테이블 2개, 의자 4개, 커피잔/받침/책을 생성 이미지에 포함했다.
- 새 자산 `assets/vvoori-cafe/v004/ai-furnished-interior.png`, RGBA 1672×941. 원본 그대로 보관/pack.
- 공원은 v003 생성 PNG 재사용. 50도 사선 카메라와 만화풍, 차량 6대·낙엽 56개의 움직임 유지.
- v004에는 3D 테이블/컵/책이 없다. 3D 창틀/창턱과 움직임만 유지하며, 가구 이미지를 마지막에 합성해 창틀을 가린다.
- 전용 Scene `Vvoori_Cafe_v004`, 카메라 `VC4_Camera`, 객체 297개.
- 원본 `scenes/vvoori-cafe-v004.blend`, 합성 이미지 3장 pack. 별도 Blender 재개방·실제 렌더 성공.
- 영상 `outputs/vvoori-cafe/v004/vvoori-cafe-toon-20s.mp4`: **1920×1080 / 24fps / 480장 / 20초 / 무음**.
- 전체 PNG의 가구/벽/바닥 등 12개 정적 영역 변화 0, MP4 전체 디코딩 정상, 시작/끝 픽셀 일치.
- 62개 애니메이션 끝점 변환 오차 0, 이전 v003 원본/영상 해시 유지.
- 제작·프롬프트·검증 `workflows/vvoori-cafe/v004-README.md`, `v004-image-prompt.md`, `v004-verification-summary.json`.
- 생성 이미지·원본·최종 MP4·포스터·재생 페이지와 코드는 Git 포함. 480장 중간 프레임은 로컬 보관.
- 마지막 브리찌 작업 `20261002T090249-bc86e79b33`, ok=true, 미리보기 직접 확인.
- 다음 단계: 사용자 피드백. 가구 수정은 생성 실내 이미지에서, 창틀/카메라 변경은 캐시/투시도 함께 갱신한다.

<!-- VVOORI_CAFE_V004_END -->

# 이전 제작: vvoori-cafe v003 — 50도 사선 통창과 만화풍 3D

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
