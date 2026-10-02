# vvoori-cafe v004 — 테이블과 의자도 생성 이미지

2026-10-02. 사용자 요청 **“실내에 테이블이나 의자도 실내 이미지로 만들어”**를 반영한다.

## 변경 내용

v003 실내 RGBA를 내장 image_gen으로 편집해 테이블 두 개, 벤트우드 의자 네 개,
커피잔·받침접시·책을 이미지에 포함했다. 기존 우측 안락의자와 화분도 유지한다.
가구를 Blender에서 렌더해 이미지로 바꾼 것이 아니라 **이미지 생성 도구로 그린 실내 그림**이다.

- 새 실내 자산: `assets/vvoori-cafe/v004/ai-furnished-interior.png`, RGBA 1672×941.
- [실제 생성 프롬프트](v004-image-prompt.md). 원본 PNG를 수정 없이 보관하고 Blender에 pack한다.
- 공원은 승인된 v003 생성 자산 `assets/vvoori-cafe/v003/ai-oblique-park.png`를 재사용한다.
- 기존 3D 테이블·잔·책 컬렉션은 v004에 포함하지 않는다. 이전 v003은 원본과 영상 모두 보존한다.
- 3D로 남긴 요소는 창틀·창턱, 차량 6대, 낙엽 56개다. 카메라의 50도 사선 구성과 셀 명암을 유지한다.

합성 순서는 `공원 이미지 → 차량/낙엽 3D → 창틀 3D 캐시 → 가구 포함 실내 RGBA`다.
실내 이미지를 마지막에 합성하므로 가구가 창틀을 자연스럽게 가린다.
창틀은 고정 카메라에서 1회 렌더한 packed 캐시를 사용하며 실제 기하는 원본에 유지한다.

## 파일과 제작 순서

- 전용 원본: `scenes/vvoori-cafe-v004.blend`, Scene `Vvoori_Cafe_v004`, 카메라 `VC4_Camera`, 객체 297개.
- 최종 영상: `outputs/vvoori-cafe/v004/vvoori-cafe-toon-20s.mp4` — Full HD / 24fps / 480프레임 / 20초 / 무음.
- 포스터 `poster-fullhd.png`, 재생 페이지 `play-loop.html`, 레이어 확인표 `layers-review.jpg`는 같은 결과 폴더.
- 미리보기 [v004-preview.jpg](v004-preview.jpg), [레이어 확인표](v004-layers-review.jpg).

1. 가구를 포함한 실내 PNG 생성 후 assets 폴더에 보관한다.
2. v003 Scene이 있는 브리찌에서 `19_apply_furnished_interior.py`로 독립 v004와 창틀 캐시를 만든다.
3. `20_render_furnished_movie.py`로 전체 프레임을 렌더한다.
4. 일반 Python에서 `21_package_furnished_movie.py`로 MP4 인코딩·전체 프레임/루프/정적 영역 검증.
5. 독립 Blender에서 `22_finalize_furnished_source.py`로 전용 원본을 정상 저장하고, 다시 열어 `23_verify_furnished_reopen.py`로 렌더 검증.

이미 생성된 Scene/프레임 위에서 제작 스크립트를 무조건 재실행하지 않는다.
전용 `.blend`에는 공원/실내/창틀 캐시 세 장이 pack되어 별도 이미지 파일 없이도 렌더할 수 있다.
기본 편집 뷰는 `VC4_EditAll3D`, 출력용 뷰는 `VC4_Motion`이다. 가구 위치를 바꾸려면 실내 이미지를 편집한다.
카메라/창틀을 바꾸면 이미지 투시와 창틀 캐시도 갱신해야 한다.

## 검증 기록

12개 실내 고정 영역을 480장 전체에서 검사해 PNG 채널 변화 0을 확인했다.
MP4 전체 디코딩 정상, 시작/끝 프레임 픽셀 동일, 별도 렌더 끝점도 차이 0이다.
압축 후 고정 영역의 평균 차이는 최대 0.233 미만(8비트 채널 기준)이다.
62개 애니메이션의 시작/끝 변환 오차 0, 생성 PNG의 packed SHA-256 일치,
v003 원본/영상 해시 보존, 별도 프로세스의 원본 재개방 및 실제 Full HD 렌더를 확인했다.
실측 결과는 `v004-verification-summary.json`과 `v004-source-verification.json`에 기록했다.

최종 생성 이미지·원본·영상·포스터·재생 페이지와 제작 코드는 Git에 포함한다.
480개 중간 PNG와 브리찌 백업은 로컬 보관한다. Windows / Blender 5.2.1 / RTX 3090 OptiX 기준이다.
