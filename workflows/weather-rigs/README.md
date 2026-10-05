# 날씨 요정 맞춤 리깅 v001

사용자 승인: 기존 오디오 제작 방법을 설명하고 앞서 추천한 다섯 캐릭터의 맞춤 리깅을 적용한다.
기존 제작 흐름과 디자인을 보강하는 작업이다. 기존 캐릭터·영상·Scene은 보존하며 전용 `Weather_Rigs_v001` Scene과 `WR1_` 객체를 만든다.

## 승인된 구성

- 공통: 실제 Armature 뼈대, 몸 컨트롤, 손발 IK 목표, 눈/입 표정 조절, 몸 눌림/늘림.
- 몽실: 숨쉬기, 쿠션과 안기 조절.
- 해롱: 손 흔들기와 햇살 흔들기/펼치기.
- 또르: 몸 늘리기/눌리기와 물방울 꼭지 흔들기.
- 송송: 팔다리와 눈 결정 접기/펼치기.
- 솔솔: 몸 휘기, 소용돌이와 스카프 움직임.
- 기본 자세의 재사용 원본과 별도 애니메이션 시연 원본/MP4를 제공한다. 외부 설치·다운로드·서비스는 사용하지 않는다.

## 진행 및 검증

- [x] 실제 v002 객체·형상·곡선 경로 조사.
- [x] 캐릭터별 독립 복제, 뼈대/스키닝/조작 컨트롤/표정과 특수 동작 설정.
- [x] 기본 자세 원형 유지, 모든 메시의 뼈대 연결, IK 목표 이동과 특수 동작의 실제 변형 검사.
- [x] 독립 원본 재개방 및 driver 유효성 확인. 기본 자세와 복합 변형 자세 렌더 직접 확인.
- [x] 짧은 리깅 시연 영상 전체 렌더·디코딩·프레임/국소 배경 안정성 확인.
- [x] 사용 설명·오디오 제작 설명·현재 상태 기록. 관련 변경을 작업 커밋에 포함하며 푸시 결과는 완료 응답에 기록한다.

## 앞선 다섯 영상의 오디오

`workflows/weather-shorts/06_package_movies.py`의 `audio()`가 Python/NumPy로 파형을 직접 합성했다.

1. 5음계(C/D/E/G/A, C는 옥타브 중복) 패턴을 짧게 감쇠하는 사인파와 배음으로 연주한다. 저음과 약한 잡음 타악음을 더한다. 1·2편은 104 BPM, 3·4·5편은 92 BPM이다.
2. 종소리·찰칵·거품·바람·점프·미끄러짐·비·얼음·코골이·재채기 느낌의 효과음을 사인파, 주파수 변화, 잡음과 음량 곡선으로 만든다. 녹음 음원이나 성우 목소리는 아니다.
3. `stories.py`의 편별 `sfx` 타임라인에 맞춰 효과음을 더하고 좌우 위치와 음량을 조절한다. 시작 0.15초와 끝 1초는 페이드한다.
4. 48kHz/16bit/스테레오 WAV로 저장한 뒤 FFmpeg로 AAC 160kbps로 변환하여 MP4에 넣는다. 이 합성음은 간단한 전자 장난감 같은 음색이며, 실제 악기나 자연음 녹음의 질감을 목표로 한 사운드는 아니다.
5. `audio-manifest.json`에는 효과음 종류·시각·길이와 WAV 피크/RMS, `output-verification.json`에는 MP4에서 다시 디코딩한 오디오 피크/RMS를 남겼다. 기존 5편의 피크는 0.272–0.299, 잘린 파형(clipping)은 검출되지 않았다.

## 결과 파일과 조작법

- `scenes/weather-rigs-v001.blend`: 기본 자세의 재사용 원본, Scene `Weather_Rigs_v001`. 애니메이션을 넣기 전에 이 파일을 복사하여 새 버전으로 작업한다.
- `scenes/weather-rig-demo-v001.blend`: 실제 컨트롤에 키프레임을 넣은 16초 시연, Scene `Weather_Rig_Demo_v001`.
- `outputs/weather-rigs/v001/weather-rig-demo-16s.mp4`: 1920×1080 / 24fps / 384프레임, 한국어 안내 포함, 무음.
- `outputs/weather-rigs/v001/rig-neutral.png`, `rig-expression-special-test.png`: 기본 자세와 표정/특수 조절 조합 검사 이미지.
- `outputs/weather-rigs/v001/rig-demo-contact.png`: 최종 MP4에서 추출한 6개 시점.

1. 재사용 원본을 열면 몽실의 뼈대가 **Pose Mode**로 선택되어 있다. 다른 캐릭터는 Object Mode에서 해당 `WR1_<캐릭터>_RIG`를 선택한 후 Pose Mode로 바꾼다. `Mongsil / Haerong / Ttorr / Songsong / Solsol`이 각각 몽실 / 해롱 / 또르 / 송송 / 솔솔이다.
2. 손·발의 작은 원형 `CTRL_Hand.L/R`, `CTRL_Foot.L/R`를 선택하고 **G**로 이동한다. 짧은 팔다리가 두 관절 IK로 따라간다. IK는 팔다리를 무한히 늘리지 않으므로 원래 팔·다리 길이 안에서 포즈를 잡는다. `.L/.R`은 화면 왼쪽/오른쪽이다.
3. 몸의 `CTRL_Body`는 이동/회전할 수 있다. **N → Item → Custom Properties**의 `squash`는 0이 기본, 양수는 세로 늘림, 음수는 눌림이다. 일반 Scale보다 이 값을 사용한다. `CTRL_Root`는 캐릭터 전체를 이동한다.
4. 얼굴 위 왼쪽 다이아몬드 `CTRL_Face`를 선택한다. 같은 Custom Properties에서 `awake`로 눈 뜨기, `blink`로 눈 감기, `smile`로 미소, `surprise`로 놀란 입을 조절한다. 각각 0–1이다. 기본 눈을 뜨고 있는 해롱·또르에는 `awake`가 따로 변형을 만들지 않는다. 몽실·솔솔의 졸린 눈과 송송의 윙크는 기본 0에서 원래 디자인을 유지한다.
5. 얼굴 위 오른쪽 다이아몬드 `CTRL_Extras`에 각 캐릭터의 특수 조절값이 있다. 변형값에 마우스를 두고 **I**를 눌러 키프레임을 넣을 수 있다. 시연 파일의 타임라인에는 이런 값들이 실제로 기록되어 있다.

| 캐릭터 | 뼈 수 | 특수 조절값 | 의미 |
|---|---:|---|---|
| 몽실 | 24 | `breath`, `hug`, `CTRL_Cushion` | 숨 들이쉬기; 0은 팔 벌림/1은 원래 쿠션 안기; 쿠션 직접 이동/회전 |
| 해롱 | 35 | `ray_sway`, `ray_phase`, `ray_spread` | 햇살 흔들림 크기/진행/펼침; 펼침 범위 −0.10–0.12 |
| 또르 | 23 | `tip_sway` | 물방울 꼭지 좌우 휘기, −1–1 |
| 송송 | 29 | `crystal_fold` | 0은 원래 눈 결정, 1은 몸 쪽으로 접기 |
| 솔솔 | 31 | `body_bend`, `crest_curl`, `scarf_wave`, `scarf_phase` | 몸과 소용돌이 휘기, 스카프 흔들림 크기/진행 |

`ray_phase`와 `scarf_phase`는 진행값이므로 타임라인에 서로 다른 값을 키프레임으로 넣어야 계속 흔들린다. 복원은 위치/회전을 초기화하고 얼굴/특수 값을 0으로, 몽실 `hug`만 1로 되돌린다. 기본 원본을 다시 여는 방법도 있다.

Controls 컬렉션만 보이고 Deform/Mechanism은 숨겨 두었다. 실제 변형 뼈와 보조 뼈는 삭제된 것이 아니며, Armature의 Bone Collections에서 표시할 수 있다. 149개 메시 모두 실제 Armature modifier와 정규화된 가중치로 연결되어 있다. 별도 애드온이나 Python 실행 허용 없이 Blender의 기본 뼈대·IK·shape key·단순 식 driver로 움직인다.

## 검증과 재현

- 실제 브리찌 제작과 독립 Blender 재개방을 구분하여 확인했다. 총 5개 Armature / 142개 뼈 / 149개 스키닝 메시 / 124개 유효 driver다.
- 20개 손발 IK 목표 이동 검사 통과, 목표와 끝 관절의 최대 거리 오차 약 0.000032 Blender 단위. 기본 자세 메시와 중립 변형 결과의 최대 점 차이 약 0.0000022 단위다.
- 몸 늘림, 표정 키, 각 특수 조절이 실제 메시를 변경하는지 검사했다. 렌더를 직접 보고 해롱 햇살 펼침 범위를 줄였다. 무제한 변형이나 임의 극단 조합을 보장하는 범용 인체 리그는 아니다.
- `03_verify_rigs.py`가 독립 원본의 스키닝·IK·driver와 기본/복합 자세를 검사한다. `04_build_demo.py`는 중립 원본의 독립 복사에 282개 animation curve를 만들고, `05_render_demo.py`가 별도 Blender에서 모든 프레임을 렌더한다.
- `06_package_and_verify.py`는 한국어 설명 합성, 모든 PNG/MP4 디코딩, 5곳의 국소 고정 배경, 중립 원본과 이전 파일 보존을 검사한다. 사용한 한글 폰트는 실행 PC에 설치된 맑은 고딕이며, 결과 영상에는 글자가 이미 합성되어 있다. `.blend` 원본에는 외부 폰트/이미지 의존성이 없다.
- 최종 384개 PNG와 MP4 전체 디코딩 검사 통과. 고정 배경 5곳은 모든 프레임에서 채널 차이 0. 이전 별도 원본/영상 33개 SHA-256 동일하며, 과거 커밋의 날씨 요정 자산 72개도 Git blob과 일치했다. 중립 원본은 시연 제작 후에도 SHA-256이 동일하다. 최종 영상 추출 6개 시점과 대표 장면을 직접 확인했다.
- 첫 제작은 Blender 5.2에서 `Bone.select`가 없어 마지막 선택 단계에서 멈췄다. 기존에 완성된 뼈대를 중복 생성하지 않고 `02b_finish_initial_save.py`로 저장을 완료했다. 이후 소스는 `PoseBone.select`로 수정하고 재개방/렌더까지 검사했다.
- Windows / Blender 5.2.1 LTS / RTX 3090에서 확인했다. 기존 다섯 코미디 영상의 애니메이션을 이 새 뼈대로 자동 변환한 것은 아니며, 기존 영상과 원본은 그대로 보존한다.

실행은 저장소 루트에서 한다. 새 제작 버전으로 재사용할 때 Scene/접두사/출력 경로를 바꾼다. 기존 결과에 생성 스크립트를 중복 실행하지 않는다.

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File scripts/blender.ps1 run --script workflows/weather-rigs/02_build_rigs.py --label "날씨 요정 맞춤 리깅" --timeout 1200
# 아래는 Blender 실행 파일이 PATH에 있는 환경의 독립 검증/출력 명령이다.
blender --background scenes/weather-rigs-v001.blend --python-exit-code 1 --python workflows/weather-rigs/03_verify_rigs.py
powershell -NoProfile -ExecutionPolicy Bypass -File scripts/blender.ps1 run --script workflows/weather-rigs/04_build_demo.py --label "실제 리깅 시연" --timeout 1200
blender --background scenes/weather-rig-demo-v001.blend --python-exit-code 1 --python workflows/weather-rigs/05_render_demo.py
python workflows/weather-rigs/06_package_and_verify.py
```

독립 검증은 새로 제작한 원본을 정규화하여 다시 저장하므로 시연을 만들기 전에 실행한다. 결과의 백업·실제 렌더 프레임·중간 합성 파일·로그는 로컬 `outputs/weather-rigs/v001/`와 브리찌 job 폴더에 보존한다. Git에는 전용 원본·최종 영상/검증 이미지·핵심 검증 JSON·제작 코드만 선택하여 반영한다.
