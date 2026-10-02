"""20초 전체 동작을 960x540/12fps 검토본으로 출력; 1080p24 편집 원본 설정 유지.

최종 출력은 1920x1080/24fps/32 samples로 별도 렌더한다. 기존 출력 덮어쓰기 금지.
"""
import json
import shutil
import time

import bpy

scene = bpy.context.scene
assert scene.name == 'Vvoori_Cafe_v001'
out = PROJECT_ROOT / 'outputs/vvoori-cafe/v001'
folder = out / 'review-frames'
folder.mkdir(exist_ok=True)
assert not list(folder.glob('*.png')), 'Do not overwrite or automatically resume an existing run.'
animated = [o for o in scene.objects if o.animation_data and o.animation_data.drivers]

def transforms(frame):
    scene.frame_set(frame)
    bpy.context.view_layer.update()
    deps = bpy.context.evaluated_depsgraph_get()
    deps.update()
    return {o.name: [float(x) for row in o.evaluated_get(deps).matrix_world for x in row] for o in animated}

a, b, middle = transforms(1), transforms(480), transforms(241)
endpoint = max(abs(x-y) for k in a for x, y in zip(a[k], b[k]))
motion = max(abs(x-y) for k in a for x, y in zip(a[k], middle[k]))
assert endpoint < 1e-5 and motion > 1
assert len(animated) == 62
assert not any(not fc.is_valid for o in animated for fc in o.animation_data.drivers)
(out/'motion-verification.json').write_text(json.dumps({
    'ok': True, 'animated_objects': len(animated), 'endpoint_max_error': endpoint,
    'midpoint_motion': motion, 'original_frames': [1, 480],
}, indent=2), encoding='utf-8')

start = time.monotonic()
scene.render.resolution_percentage = 50
scene.cycles.samples = 12
try:
    for i in range(239):
        # Sample all of the original 479-frame period; include its duplicate endpoint.
        scene.frame_set(int(1 + 479*i/239), subframe=(479*i/239) % 1)
        scene.render.filepath = str(folder / f'{i+1:04d}.png')
        bpy.ops.render.render(write_still=True)
        elapsed = time.monotonic() - start
        (out/'review-progress.json').write_text(json.dumps({
            'frame': i+1, 'total': 240, 'elapsed_seconds': round(elapsed, 1),
            'estimated_remaining_seconds': round(elapsed/(i+1)*(239-i)),
        }), encoding='utf-8')
    scene.frame_set(480)
    scene.render.filepath = str(out/'review-independent-endpoint.png')
    bpy.ops.render.render(write_still=True)
    shutil.copyfile(folder/'0001.png', folder/'0240.png')
finally:
    scene.frame_set(1)
    scene.render.resolution_percentage = 100
    scene.cycles.samples = 32
    scene.render.filepath = '//../outputs/vvoori-cafe/v001/master-frames/'

path = PROJECT_ROOT / 'scenes/vvoori-cafe-v001.blend'
assert not path.exists()
bpy.data.libraries.write(str(path), {scene}, path_remap='RELATIVE_ALL', fake_user=True, compress=True)
(out/'review-render.json').write_text(json.dumps({
    'ok': True, 'frames': 240, 'fps': 12, 'duration_seconds': 20,
    'width': 960, 'height': 540, 'samples': 12,
    'render_seconds': time.monotonic()-start,
    'master_settings': '1920x1080 / 24fps / 480 frames / 32 samples',
    'full_quality_movie_rendered': False,
}, indent=2), encoding='utf-8')
