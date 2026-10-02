"""독립 Blender 프로세스에서 전용 .blend를 정상 프로젝트로 저장하고 검증.

blender --background scenes/vvoori-cafe-v001.blend --python workflows/.../04_*.py
다른 프로젝트의 Scene은 로드되지 않는다. 기존 파일의 최초 포맷 변환만 허용한다.
"""
from pathlib import Path
import hashlib
import json
import shutil

import bpy

root = Path(__file__).resolve().parents[2]
out = root/'outputs/vvoori-cafe/v001'
source_path = root/'scenes/vvoori-cafe-v001.blend'
assert Path(bpy.data.filepath).resolve() == source_path.resolve()
scene = bpy.data.scenes['Vvoori_Cafe_v001']
assert len(bpy.data.scenes) == 1
bpy.context.window.scene = scene
bpy.context.window.view_layer = scene.view_layers['VC_MovingCarsAndLeaves']
assert len(scene.objects) == 289
assert scene.camera.name == 'VC_Camera'
assert (scene.render.resolution_x, scene.render.resolution_y, scene.render.resolution_percentage,
        scene.render.fps, scene.frame_end) == (1920, 1080, 100, 24, 480)
assert {c.name for c in scene.collection.children} == {'VC_Traffic', 'VC_FallingLeaves', 'VC_LightingCamera'}
assert not any(o.name.startswith('AC_') for o in scene.objects)
images = [n.image for n in scene.compositing_node_group.nodes if n.type == 'IMAGE']
assert len(images) == 2 and all(im.packed_file for im in images)
assert all(im.size[:] == (1920, 1080) for im in images)
animated = [o for o in scene.objects if o.animation_data and o.animation_data.drivers]

def values(frame):
    scene.frame_set(frame)
    bpy.context.view_layer.update()
    deps = bpy.context.evaluated_depsgraph_get()
    deps.update()
    return {o.name: [float(x) for row in o.evaluated_get(deps).matrix_world for x in row] for o in animated}

a, b, middle = values(1), values(480), values(241)
endpoint = max(abs(x-y) for k in a for x, y in zip(a[k], b[k]))
motion = max(abs(x-y) for k in a for x, y in zip(a[k], middle[k]))
assert len(animated) == 62 and endpoint < 1e-5 and motion > 1
assert not any(not fc.is_valid for o in animated for fc in o.animation_data.drivers)
assert not scene.camera.animation_data
assert not any(o.animation_data or o.data.animation_data for o in scene.objects if o.type == 'LIGHT')
old_hashes = json.loads((out/'project-build.json').read_text())['source_hashes']
assert all(hashlib.sha256((root/p).read_bytes()).hexdigest() == h for p, h in old_hashes.items())
scene.frame_set(1)
for screen in bpy.data.screens:
    for area in screen.areas:
        if area.type == 'VIEW_3D':
            area.spaces.active.region_3d.view_perspective = 'CAMERA'
backup = out/'source-library-before-finalize.blend'
assert not backup.exists()
shutil.copyfile(source_path, backup)
bpy.ops.wm.save_as_mainfile(filepath=str(source_path), check_existing=False, compress=True, relative_remap=True)
report = {'ok': True, 'reopened_in_new_process': True, 'scene': scene.name,
          'objects': len(scene.objects), 'animated_objects': len(animated),
          'endpoint_transform_error': endpoint, 'midpoint_motion': motion,
          'packed_images': [im.name for im in images], 'original_autumn_files_unchanged': True,
          'full_quality_movie_rendered': False}
(out/'saved-source-verification.json').write_text(json.dumps(report, indent=2), encoding='utf-8')
(root/'workflows/vvoori-cafe/source-verification.json').write_text(json.dumps(report, indent=2), encoding='utf-8')
print(json.dumps(report, indent=2))
