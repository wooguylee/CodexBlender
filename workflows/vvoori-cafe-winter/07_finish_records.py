"""실제 검증 결과를 프로젝트 기록으로 모으고, 완료한 겨울 작업만 현재 상태에 추가."""
from pathlib import Path
import json,hashlib,shutil
import numpy as np
from PIL import Image
root=Path(__file__).resolve().parents[2];out=root/'outputs/vvoori-cafe-winter/v001'
workflow=root/'workflows/vvoori-cafe-winter'
reports={name:json.loads((out/f'{name}.json').read_text(encoding='utf-8')) for name in [
 'verification','source-verification','native-reopen-verification','motion-audit','render-report','edge-fix-verification']}
assert all(r['ok'] for r in reports.values())
a=np.array(Image.open(out/'poster-fullhd.png'));b=np.array(Image.open(out/'native-reopen-preview.png'))
assert np.array_equal(a,b)
comparison={'ok':True,'independent_native_render_pixel_identical':True,'maximum_channel_difference':0}
(out/'native-render-comparison.json').write_text(json.dumps(comparison,indent=2),encoding='utf-8')
for name in ['source-verification','native-reopen-verification','motion-audit','native-render-comparison','edge-fix-verification']:
    shutil.copyfile(out/f'{name}.json',workflow/f'v001-{name}.json')
verification=reports['verification']
section=f'''<!-- VVOORI_CAFE_WINTER_V001_BEGIN -->
# 현재 제작: vvoori-cafe-winter v001 — 겨울 공원과 통창 카페

2026-10-02. 새 이미지 생성·Full HD 전체 렌더·독립 원본 검증 완료.

- 공원 RGB와 가구/창 외곽 테두리 포함 실내 RGBA를 built-in image_gen으로 각각 새로 생성했다.
- 생성 원본 두 장은 `assets/vvoori-cafe-winter/v001/`, 각 1672×941. 원본 PNG를 그대로 보존하고 pack했다.
- 합성은 공원 → 실제 Blender 차량 6대/눈 280개 → 실내 이미지. 정적 실내 3D나 렌더 캐시는 없다.
- 전용 원본 `scenes/vvoori-cafe-winter-v001.blend`, Scene `Vvoori_Cafe_Winter_v001`, 카메라 `VWC1_Camera`, 객체 527개.
- 실제 카메라 수평각 약 50도, 차도 접지 7,289개 표본 검사. 차량 순환은 화면 밖/벽 뒤, 눈 순환은 화면 위/아래 밖이다.
- 완성 영상 `outputs/vvoori-cafe-winter/v001/vvoori-cafe-winter-20s.mp4`: **1920×1080 / 24fps / 480프레임 / 정확히 20초 / 무음**.
- 모든 480프레임을 실제 렌더했다. 주기는 480프레임으로, frame 481=frame 1이다. 마지막 프레임을 첫 프레임으로 복제하지 않았다.
- 모든 PNG의 14개 실내 ROI 변화 0. 불투명 실내 {verification['opaque_mask_pixels']:,}픽셀 전체 검사에서는 480장 중 총 {verification['static_single_lsb_pixel_events']}개의 단일 픽셀/채널에만 최대 1/255 양자화 차이가 있었다. MP4 전체 디코딩과 사양 검사 통과.
- 별도 Blender 프로세스에서 외부 이미지 경로를 의도적으로 끊고 packed 자산만으로 재렌더한 결과가 최종 PNG와 픽셀 동일.
- 최초 검사의 화면 상단 한 줄 alpha 문제는 Scale 노드 Clip→Extend로 보정하고 480장 전체를 재렌더했다.
- 기존 vvoori-cafe 원본/MP4 10개 SHA-256 유지. 기존 장면과 무관한 미커밋 변경 보존.
- 제작·프롬프트·검증 설명: `workflows/vvoori-cafe-winter/README.md`, `v001-*-verification.json`.
- 최종 포스터/반복 재생: `outputs/vvoori-cafe-winter/v001/poster-fullhd.png`, `play-loop.html`.
- 다음 단계: 사용자 피드백. 수정 시 이 v001을 기준으로 새 버전에 저장한다. Windows/RTX 3090 외 환경은 미검증.

<!-- VVOORI_CAFE_WINTER_V001_END -->

'''
path=root/'docs/current-state.md';existing=path.read_text(encoding='utf-8')
assert 'VVOORI_CAFE_WINTER_V001_BEGIN' not in existing
path.write_text(section+existing,encoding='utf-8')
(out/'current-state-section.md').write_text(section,encoding='utf-8')
plan=workflow/'v001-PLAN.md';text=plan.read_text(encoding='utf-8')
text=text.replace('- [ ]','- [x]',5)
plan.write_text(text,encoding='utf-8')
files=[root/'scenes/vvoori-cafe-winter-v001.blend',out/'vvoori-cafe-winter-20s.mp4',out/'poster-fullhd.png',
 root/'assets/vvoori-cafe-winter/v001/ai-winter-park.png',root/'assets/vvoori-cafe-winter/v001/ai-winter-cafe.png']
manifest={p.relative_to(root).as_posix():{'bytes':p.stat().st_size,'sha256':hashlib.sha256(p.read_bytes()).hexdigest()} for p in files}
(out/'deliverable-manifest.json').write_text(json.dumps(manifest,indent=2),encoding='utf-8')
print(json.dumps({'ok':True,'opaque_static_pixels':verification['opaque_mask_pixels'],'video_bytes':verification['video_bytes'],'source_bytes':files[0].stat().st_size},indent=2))
