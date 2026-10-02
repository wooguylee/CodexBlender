# vvoori-cafe v002: AI 생성 이미지 + Blender 움직임

2026-10-02. 사용자가 v001의 해석을 정정했다.

> 배경과 카페 이미지는 렌더링이 아니라 니가 이미지를 생성할 수 있으니 그걸로 만들어서 추가하고 그 이미지를 활용하라는 의미야.

이에 따라 **공원과 카페를 built-in image_gen으로 새로 생성**하고, PNG 원본을 Blender 합성 노드에 직접 연결했다.
v001에서 Blender 장면을 구워 만든 EXR은 v002의 이미지 노드에 사용하지 않는다.
기존 autumn-cafe/v001 장면과 파일은 보존한다.

## 실제 생성 자산

- `assets/vvoori-cafe/v002/ai-autumn-park.png`: 새 가을 공원·도로 사진풍 이미지, RGB, 1672×941.
- `assets/vvoori-cafe/v002/ai-cafe-foreground.png`: 새 카페 내부·가구·창틀 이미지, RGBA, 1672×941.
- 생성 도구: built-in `image_gen`. 별도 CLI/API 호출이나 외부 사진 다운로드는 없다.
- 두 최종 PNG는 원본 그대로 보관하고 전용 `.blend`에도 pack한다. 두 파일은 이 작업의 핵심 자산으로 Git에 명시적으로 포함한다.
- 카페 초안은 창턱이 높아 한 번 수정 생성했다. 버려진 초안은 로컬 assets 폴더에만 보존한다.
- 최종 프롬프트와 수정 프롬프트: [v002-image-prompts.md](v002-image-prompts.md).

## 합성

`생성 공원 PNG → Blender 차량/낙엽 → 생성 카페 RGBA PNG` 순서로 Alpha Over한다.
차량이 창틀 뒤로 지나가고 카페 전경은 고정된다. 차량 6대와 낙엽 56개는 이전의 3D 모델/움직임을 독립 복사했다.
이미지는 사진풍으로 바뀌었지만, 기존 차량 모델의 단순화된 CG 형태는 유지한다.

생성 PNG는 sRGB 표시 이미지이므로 Standard/exposure 0으로 합성한다.
AgX를 추가 적용하여 이미지를 다시 톤 매핑하지 않는다. 두 이미지는 렌더 크기에 맞춰 스케일된다.

카페의 실제 alpha는 창문 안 0, 대부분의 고체 표면 250–253/255다.
원본 RGBA 파일을 수정하지 않고 합성 노드에서 `min(alpha * 255/250, 1)`로 처리하여
고체 창틀·가구에 차량이 비치지 않게 한다. 얇은 잎/유리 꽃병 가장자리는 일부 반투명도를 유지한다.
이는 임의 배경 제거가 아니라 생성된 alpha의 합성 정규화다.

## 파일과 재현

- 전용 Scene `Vvoori_Cafe_v002`, 카메라 `VC2_Camera`, 객체 289개.
- 독립 편집 원본 `scenes/vvoori-cafe-v002.blend`.
- Full HD 포스터 `outputs/vvoori-cafe/v002/poster-fullhd.png`.
- 20초 검토 영상 `outputs/vvoori-cafe/v002/vvoori-cafe-review-20s.mp4`.
- 재생 페이지 `outputs/vvoori-cafe/v002/play-loop.html`.
- 원본은 1920×1080 / 24fps / 480프레임. 검토 영상은 960×540 / 12fps / 240프레임.
- 고화질 1080p24 전체 영상은 이번 출력 범위에 포함하지 않는다.

1. 이미지 생성 도구로 위 두 PNG를 만든다. 원본 PNG를 복사하거나 Git의 생성 자산을 사용한다.
2. 브리찌에서 `06_apply_generated_images.py`: v001의 움직임을 독립 복사하고 생성 이미지 적용.
3. 브리찌에서 `07_render_generated_review.py`: v002 포스터/검토 프레임/전용 원본 출력.
4. 일반 Python에서 `08_package_generated_review.py`: 전체 프레임·정적 영역·끝점·MP4 검증 및 패키징.
5. 새 Blender에서 전용 원본을 열고 `09_finalize_generated_source.py`: 원본 검증/정상 프로젝트 저장.
6. 다시 새 Blender에서 `10_verify_generated_reopen.py`: 저장된 기본 Scene/pack/실제 렌더 검증.

공통 02–05번 스크립트는 `VERSION` 기본값 v001을 유지하며 07–10번에서만 v002를 지정한다.
이미 생성된 Scene에 06번을 재실행하지 않는다. 수정은 다음 버전으로 보존한다.

## 검증 기준

240장 전체 PNG 무결성, 실제 움직임, 10개 카페 정적 ROI의 변화 0, MP4 전체 디코딩/길이/첫끝 픽셀 일치,
62개 애니메이션 끝점 변환, 독립 원본 재개방을 확인한다.
전용 원본에 pack된 PNG 데이터의 SHA-256을 실제 생성 PNG 원본과 비교한다.
기존 원본과 v001 검토 영상의 SHA-256을 유지한다.
실측 결과는 `v002-verification-summary.json`, `v002-source-verification.json`을 따른다.

초기 합성 구성은 Blender 5.2에서 제거된 `CompositorNodeMath` 때문에 중단됐다.
실제 API를 조회해 `ShaderNodeMath`와 Set Alpha의 `Type` 입력을 사용하도록 수정했다.
`06b_finish_generated_composite.py`는 그 지점 이후만 이어서 완료한 이력이며 정상 재현에는 필요 없다.

검증 환경은 Windows / Blender 5.2.1 / RTX 3090이다.
