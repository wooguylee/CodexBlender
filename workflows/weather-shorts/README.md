# 오늘의 날씨 요정들 — 코미디 단편 5편

사용자 승인: “5개 모두 만들어봐”. 몽실·해롱·또르·송송·솔솔의 기존 3D 디자인을 독립 복제해 다섯 이야기를 제작한다. 정지 이미지에 카메라 이동을 준 영상이 아니라 몸, 손발, 눈, 소품과 날씨가 움직이는 Blender 애니메이션이다.

| 편 | 제목 | 길이 | 사건과 반전 |
|---|---|---:|---|
| 1 | 단체사진 대소동 | 24초 | 포즈를 잡던 요정들이 바람에 뒤엉킨 순간 사진이 찍힌다. |
| 2 | 몽실의 별 쿠션을 잡아라 | 30초 | 재채기에 날아간 별을 쫓다가 얼음길에서 미끄러진다. 몽실은 계속 잔다. |
| 3 | 꽃 한 송이 키우기 | 32초 | 과한 햇살·비·눈을 거쳐 협력으로 꽃을 피우지만 꽃가루를 뒤집어쓴다. |
| 4 | 오늘의 날씨는 누구? | 28초 | 날씨 방송의 주인공을 다투다가 잠든 몽실이 화면을 가득 채운다. |
| 5 | 절대 터뜨리면 안 돼! | 26초 | 조심히 지키던 거품을 몽실이 껴안는다. 작은 거품 다섯 개가 모자가 된다. |

총 140초 / 3,360프레임. 1920×1080, 24fps, H.264/yuv420p + AAC/48kHz/스테레오. 한국어 자막과 직접 수학적으로 합성한 음악·효과음을 포함한다. 사람 목소리나 외부 음원은 사용하지 않았다.

## 원본과 결과

- 캐릭터 원본: `scenes/weather-fairies-v002.blend`의 `WF2_*` 컬렉션.
- 편집 원본: `scenes/weather-short-01-v001.blend`부터 `weather-short-05-v001.blend`까지. 파일마다 제작 Scene 1개, 독립 메시/곡선/재질/키프레임/카메라를 포함한다.
- 원본에는 외부 모델·텍스처·폰트·링크 라이브러리가 없다. Blender 기본 글꼴로 소품 글자만 표현한다.
- 최종 영상: `outputs/weather-shorts/v001/<편별 slug>/<편별 slug>.mp4`.
- 다섯 편 모아보기: `outputs/weather-shorts/v001/weather-fairies-five-stories.mp4` (2분 20초). `five-stories-contact.png`는 최종 영상 5편의 대표 장면을 모은 결과표다.
- 같은 폴더의 `story.json`, `trajectories.json`, `render-result.json`, `render-source.json`, `package.json`, `audio-manifest.json`, `output-verification.json`이 제작·검증 근거다.
- `poster.png`는 최종 MP4에서 추출한 대표 장면, `video-contact.png`는 사건별 최종 영상 확인표다.
- `frames/`의 모든 실제 PNG, `original-score.wav`, 실행 로그, 수정 전 원본과 첫 렌더 시도는 로컬 보존한다. 대용량 중간 프레임과 백업은 Git 추적하지 않는다.
- 저장소의 다른 제작 Scene/원본/미커밋 작업을 덮어쓰지 않았다. `scenes/current.blend`는 브리찌 작업용 전체 묶음으로, 이번 커밋에 포함하지 않는다.

## 제작 방법

`production.py`는 기존 캐릭터 복제, Root/손/발 Empty 컨트롤, 독립 재질, 접지 그림자, 고정 카메라와 조명을 만든다. `stories.py`에 소품과 각 이야기의 연기·사건·자막·효과음 시점을 정의한다. 12Hz로 연기를 굽고 선형 보간하여 24fps로 렌더한다. 뼈대/물리 시뮬레이션 의존 없이 기본 Blender에서 수정·렌더할 수 있다.

EEVEE 16 samples, ray tracing 끄기, 넓은 Area Light 3개와 정적 배경을 사용한다. 바닥과 접지 그림자를 별도로 표현하여 움직이는 캐릭터가 고정 배경의 조명 잡음을 일으키지 않게 했다. 모든 프레임은 실제 렌더하며 후반의 사진 소품만 의도적으로 한 프레임을 재사용한다.

새로 제작할 때는 기존 `Weather_Short_*` Scene 및 같은 이름의 출력 원본이 없는 별도 제작 사본에서 `04_build_films.py`를 실행한다. 이미 존재하면 보호용 assert로 중단한다. `04b_refine_bubbles.py`와 `04c_refine_transitions.py`는 이번 초안의 검토 수정 이력이며, 현재 `stories.py`에는 해당 수정이 반영되어 있다. 새 제작에서는 다시 실행하지 않는다.

브리찌 제작 명령:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File scripts/blender.ps1 run --script workflows/weather-shorts/04_build_films.py --label "날씨 요정 단편 5편 제작" --timeout 1200
```

독립 원본을 렌더·인코딩하는 명령(`--blender`에는 현재 PC의 Blender 실행 파일 경로 지정):

```powershell
python workflows/weather-shorts/run_batch.py --blender <Blender실행파일> --mode full
python workflows/weather-shorts/07_verify_movies.py
python workflows/weather-shorts/08_delivery.py
```

`run_batch.py`는 다섯 편을 순서대로 렌더하고 자막/음악/효과음을 결합한다. `full-queue.json`과 각 편의 `render-progress.json`으로 대기/렌더/인코딩/완료를 구분한다. 기존 프레임은 원본 SHA-256이 같을 때만 재사용한다. 불완전한 PNG는 별도로 보관하고 다시 렌더한다. 실패한 편의 로그를 확인하기 전 같은 작업을 무작정 재전송하지 않는다.

개별 MP4 생성·검증:

```powershell
python workflows/weather-shorts/06_package_movies.py --episode 1
python workflows/weather-shorts/06_package_movies.py --episode 1 --contacts video
python workflows/weather-shorts/07_verify_movies.py --episode 1
```

자막은 Windows에 설치된 맑은 고딕을 FFmpeg로 픽셀화한다. 글꼴 파일은 배포하지 않는다. Python에 NumPy/Pillow, PATH에 FFmpeg/FFprobe가 필요하다. 로컬 HTTP 서버나 외부 서비스는 사용하지 않는다.

## 검토와 검증 범위

- 사건별 스토리보드와 최종 MP4 추출 장면을 직접 확인한다. 제목, 자막 위치, 주요 소품, 다섯 캐릭터와 반전이 보이는지 검사한다.
- 초안에서 발견한 거품 테두리의 낮은 대비를 수정했다. 이동 데이터에서 발견한 동작 구간 경계의 위치 점프를 접근/복귀 곡선 및 경계 조건 수정으로 해결했다. `transition-review.json`에 수정 후 이동량과 2차 차분을 남긴다.
- 모든 PNG를 디코딩하여 누락/크기/불투명 알파를 검사한다. 프레임 간 변화량과 고유 프레임 수를 확인하며, 이를 예술적 품질이나 부드러움 전체를 증명하는 지표로 간주하지 않는다.
- 5개 고정 배경 영역을 프레임 전체에 걸쳐 비교한다. 4편 23초 이후는 몽실이 화면을 채우는 의도된 변화이므로 고정 배경 비교에서 제외한다.
- MP4 전체 디코딩, 정확한 프레임 수/길이/해상도/fps, 오디오 스트림과 유한 샘플/피크/RMS를 확인한다. 주관적인 음질 청취를 자동 검사로 대체했다고 주장하지 않는다.
- 제작 전 별도 원본들의 SHA-256을 최종 상태와 비교한다. Windows / Blender 5.2.1 LTS / RTX 3090에서 확인하며 다른 OS·GPU는 시험하지 않았다.

최종 수치와 결과는 `outputs/weather-shorts/v001/verification-summary.json`을 기준으로 한다.
