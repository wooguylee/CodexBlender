# vvoori-cafe

현재 v005 구성을 한 번의 요청으로 제작하기 위한 [통합 제작 프롬프트](vvoori-cafe-one-shot-prompt.txt).
파일 전체를 복사해 이미지 생성과 Blender 제어가 가능한 Codex에 전달한다. 공원·실내 이미지 생성부터 20초 영상 출력까지 포함하며,
재생성 특성상 구도와 분위기의 재현을 목표로 한다. 기존 결과와 픽셀 단위로 동일한 출력을 보장하는 프롬프트는 아니다.

## 최신 v005 — 넓은 통창과 테두리도 실내 이미지

3D 창틀·창턱과 그 렌더 캐시를 제외했다. 세로 기둥 없이 넓게 이어지는 통창으로 수정하고,
바깥 테두리와 가구는 실내 생성 이미지에 포함했다. Blender에서는 차량과 낙엽만 렌더한다.
원본 `scenes/vvoori-cafe-v005.blend`, Full HD 24fps 20초 결과 `outputs/vvoori-cafe/v005/`.
[v005 제작·검증 설명](v005-README.md), [실제 생성 프롬프트](v005-image-prompt.md).

## 이전 v004 — 가구도 실내 생성 이미지로 처리

테이블 두 개와 의자 네 개, 커피잔·책을 새 실내 RGBA에 포함했다. v004에는 3D 가구를 넣지 않고,
3D 창틀·차량·낙엽과 50도 사선 구도를 유지한다.
원본 `scenes/vvoori-cafe-v004.blend`, Full HD 24fps 20초 결과 `outputs/vvoori-cafe/v004/`.
[v004 제작·검증 설명](v004-README.md), [실제 생성 프롬프트](v004-image-prompt.md).

## 이전 v003 — 50도 사선 통창과 만화풍 3D

공원과 실내를 **새 만화풍 생성 이미지**로 교체하고, 카메라를 창면 정면에서 수평 50도 회전한 구성으로 바꿨다.
창틀·원형 테이블·커피잔·책은 실제 3D이며, 차량 6대와 낙엽 56개도 셀 명암으로 렌더한다.
최종 영상은 **1920×1080 / 24fps / 480프레임 / 20초**이며 검토용 저해상도 출력이 아니다.

- 원본 `scenes/vvoori-cafe-v003.blend`, 생성 자산 `assets/vvoori-cafe/v003/`.
- 영상 `outputs/vvoori-cafe/v003/vvoori-cafe-toon-20s.mp4`, 재생 페이지 `play-loop.html`.
- [v003 제작·편집·검증 설명](v003-README.md), [실제 생성 프롬프트](v003-image-prompts.md).

## 이전 v002 — 사용자 의도 정정 반영

사용자의 의미는 **Blender 렌더 추출이 아니라 이미지 생성 도구로 공원과 카페를 새로 만든 후 활용**하는 것이다.
v002는 built-in `image_gen`으로 만든 공원 RGB와 카페 RGBA PNG를 사용한다.
원본 `scenes/vvoori-cafe-v002.blend`, 결과 `outputs/vvoori-cafe/v002/`.
[v002 제작/검증 설명](v002-README.md), [실제 생성 프롬프트](v002-image-prompts.md).

아래 v001은 초기 해석과 제작 이력이다. 렌더 추출 이미지 방식은 사용자가 요청한 최종 방향이 아니다.

## 이전 v001 — Blender 렌더 추출 이미지

2026-10-02. 사용자 요청: autumn-cafe의 공원을 배경 이미지로, 카페·통창 프레임을
전경 이미지로 처리하고 차량과 낙엽만 Blender에서 움직이는 새 프로젝트.
Blender 단독 제작과 졸부(DaVinci Resolve) 사용을 비교하여 적합한 방식을 선택한다.

## 선택한 제작 방식

**고정 이미지 2장 + Blender의 움직이는 3D 레이어 + Blender 합성**을 기본으로 한다.
음악, 장시간 반복 편집, 여러 장면 연결, 최종 색보정이 필요할 때 Resolve를 후반에 사용한다.

| 방법 | 장점 | 이 프로젝트에서의 판단 |
|---|---|---|
| 전체 3D를 매 프레임 렌더 | 이동 카메라, 실제 반사·그림자 상호작용 | 고정 카메라에는 비용이 크며 정적 영역 노이즈 관리 필요 |
| 이미지 + 3D, Blender에서 합성 | 빠른 수정, 배경 조명 안정, 한 원본으로 재현 | **현재 선택** |
| 이미지 + Blender RGBA 출력, Resolve Fusion 합성 | 음악·편집·색보정·긴 영상에 편리 | 후반 작업 규모가 커질 때 유용 |

최종 결과가 2D라는 사실만으로 모든 장면을 이미지화할 수 있는 것은 아니다.
이 장면은 카메라·조명이 고정되어 있어 적합하다. 카메라 이동, 창유리 굴절과 움직이는
차량 반사, 공원에 떨어지는 낙엽 그림자가 중요해지면 해당 요소를 3D로 유지해야 한다.

확인 결과 autumn-cafe v001도 이미 단일 정적 EXR 위에 차량/낙엽을 합성하고 있었다.
새 프로젝트의 차이는 **공원과 카페를 교체 가능한 두 이미지로 분리**하고, 실제 제작 Scene에서
정적 기하를 제거했으며 움직이는 객체·재질·카메라·월드를 독립 복사했다는 점이다.
이름 변경만 한 프로젝트나 기존 MP4 복사본이 아니다. 첫 버전은 기존 구도를 재사용한다.
실사 사진이나 AI로 새로 생성한 공원 이미지로 바꾼 버전은 아니다.

## 레이어와 원본

1. `01_ParkBackground`: 공원·도로·보도·고정된 그림자, packed linear EXR.
2. `02_CarsAndLeaves`: 차량 6대, 차량 접촉 그림자, 낙엽 56개. 투명 배경에 3D 렌더.
3. `04_CafeForeground`: 가구·카페 내부·창틀, 창문 영역이 투명한 packed RGBA EXR.
4. 두 Alpha Over 노드로 순서대로 합성하고 AgX를 한 번 적용한다.

- Scene: `Vvoori_Cafe_v001`, 카메라: `VC_Camera`.
- 전용 편집 원본: `scenes/vvoori-cafe-v001.blend`.
- 현장 원본: `scenes/current.blend`; 기존 Scene도 보존한다.
- 자산: `assets/vvoori-cafe/v001/park-background.exr`, `cafe-foreground.exr`.
- 같은 위치의 PNG는 16-bit 표시용/교환용 자산. EXR은 scene-linear, PNG는 표시 변환 적용 상태다.
  두 형식을 임의로 섞거나 PNG에 AgX를 다시 적용하지 않는다.
- 최종 합성 이미지는 `outputs/vvoori-cafe/v001/poster-fullhd.png`.
- 20초 검토본은 `outputs/vvoori-cafe/v001/vvoori-cafe-review-20s.mp4`.
- 재생 페이지는 같은 폴더의 `play-loop.html`.

새 원본은 **객체 289개**로, 원래 2,120개에서 정적 객체를 제외했다.
카페·공원 객체를 holdout으로 매 프레임 렌더하지 않는다. 전경 이미지의 알파가 가림을 처리한다.
차량 접촉 그림자는 기존의 부드러운 절차적 메시 방식이며 실제 지면 shadow catcher는 아니다.
창유리는 기존의 거의 완전히 투명한 설정을 이어받아 별도 굴절/반사를 만들지 않는다.

## 출력과 검증 범위

- 편집 원본: 1920×1080, 24fps, 480프레임, 20초, 32 samples.
- 이번 검토 영상: **960×540, 12fps, 240프레임, 20초, 12 samples, 무음**.
- 고화질 1080p24 전체 MP4는 이번에 렌더하지 않았다. Full HD 포스터는 렌더했다.
- 검토 영상의 12fps 움직임은 최종 24fps의 부드러움 판정 자료로 사용하지 않는다.
- 원본의 1/480프레임이 같은 동작 위상이다. 검토본은 전체 위상을 샘플링하고 끝점을 복제한다.
  반복 경계에 검토본 1/12초, 원본 1/24초 길이의 중복 끝점이 있다.
- 240장 모두의 무결성·정적 ROI·움직임, MP4 전체 디코딩과 길이, 독립 원본 재개방을 검사한다.
- 실제 수치는 `verification-summary.json`, `source-verification.json`을 따른다.
- Windows / Blender 5.2.1 / RTX 3090 환경. 다른 OS/GPU는 검증하지 않았다.

## 재현 및 수정

브리찌 `run --script workflows/vvoori-cafe/<파일>`:

1. `01_create_layered_project.py`: autumn-cafe Scene에서 두 이미지를 생성하고 독립 Scene 생성.
2. `01b_prepare_review.py`: 현재 5.2 API로 이미지 크기를 Render Size에 맞추고 Full HD 포스터 출력.
3. `02_render_review.py`: 20초 검토 프레임과 전용 원본 생성.
4. 일반 Python에서 `03_package_verify.py`: 전체 프레임 검사, MP4/플레이어/레이어 확인표 생성.
5. 새 Blender 프로세스에서 전용 원본을 열고 `04_finalize_and_verify_source.py`: 정상 프로젝트 저장/검증.
6. 최종 원본을 다시 열고 `05_verify_native_reopen.py`: 실제 시작 Scene과 packed 이미지 합성 재렌더 검증.

이미 만들어진 Scene에 01/01b를 재실행하지 않는다. 새 결과는 v002 등으로 버전 관리한다.
다른 PC에서 `scripts/blender.ps1 start --file scenes/vvoori-cafe-v001.blend`로 연다.
두 EXR은 pack되어 있으므로 외부 assets 폴더 없이 원본을 열 수 있다.
검토 PNG/영상은 `.gitignore`의 outputs 제외 정책을 유지하고, 코드·전용 원본·미리보기·검증 요약을 Git에 보관한다.

배경 교체 시 이미지의 원근·지평선·도로 위치를 현재 카메라와 맞춰야 한다.
전경 교체 시 창틀의 불투명 부분과 투명 창문 알파가 필요하다. 같은 EXR 이름을 덮어쓰기보다
새 이미지를 로드해 해당 노드에 연결하고 pack한다. 카메라 이동은 이미지 재제작을 요구한다.

## 졸부 검토

2026-10-02 실제 노출된 jolbu 도구 18개와 VVooDvinci의 `doc/resolve-mcp.md`를 확인했다.
`resolve_*` 4개는 상태/프로젝트/페이지, `demo_*` 8개는 test1/MCP_Demo 전용,
`music1_*` 6개는 VVooMusic1 전용이다. 범용 신규 프로젝트 레이어 합성 도구는 없다.
Fusion 자체는 합성이 가능하지만 이 프로젝트 제어에는 공식 Scripting API 작업 또는 전용 MCP 도구가 필요하다.
이번 작업에서 Resolve를 조작하거나 새로운 Resolve 프로젝트를 만든 것은 아니다.
향후 졸부를 사용할 때는 실제 Windows 창 표시 상태를 확인/복원하고 MCP·공식 API만 사용한다.

근거: [Blender Alpha Over](https://docs.blender.org/manual/en/latest/compositing/types/color/alpha_over.html),
[Blackmagic Fusion](https://www.blackmagicdesign.com/products/davinciresolve/fusion).

## 실행 이력

첫 이미지 크기 설정에서 이전 API인 `scale.space`가 Blender 5.2에 없어 실패했다.
`diagnose_scale_node.py`로 실제 입력을 조회하고 `scale.inputs['Type']='Render Size'`로 수정했다.
실패 시 만들어진 미연결 Scale 노드는 같은 이름으로 이어서 연결했으며 원본 Scene에는 영향이 없다.
초기 배경 이미지 렌더는 세션 GPU 선택 전 실행되어 약 227초가 걸렸다.
재현 스크립트에는 OptiX 세션 선택을 포함했고, 이후 검토 영상은 OptiX를 사용한다.
전역 사용자 환경설정을 저장하지 않았다.
