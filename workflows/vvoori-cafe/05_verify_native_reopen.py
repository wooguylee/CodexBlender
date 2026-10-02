"""최종 저장된 일반 프로젝트를 다시 열어 실제 시작 Scene과 packed 합성을 렌더 검증."""
from pathlib import Path
import json

import bpy

root = Path(__file__).resolve().parents[2]
version = globals().get('VERSION', 'v001')
assert version in {'v001', 'v002'}
prefix = 'VC' if version == 'v001' else 'VC2'
scene = bpy.context.scene
assert scene.name == 'Vvoori_Cafe_'+version
assert len(bpy.data.scenes) == 1 and len(scene.objects) == 289
assert scene.camera.name == prefix+'_Camera'
assert scene.render.resolution_percentage == 100 and scene.render.fps == 24
images = [n.image for n in scene.compositing_node_group.nodes if n.type == 'IMAGE']
assert len(images) == 2 and all(im.packed_file for im in images)
assert next(n for n in scene.compositing_node_group.nodes if n.type == 'R_LAYERS').scene == scene
prefs = bpy.context.preferences.addons['cycles'].preferences
prefs.compute_device_type = 'OPTIX'; prefs.get_devices()
for device in prefs.devices:
    device.use = device.type == 'OPTIX'
scene.render.resolution_percentage = 50
scene.cycles.samples = 12
scene.frame_set(2); scene.frame_set(1)
scene.render.filepath = str(root/'outputs/vvoori-cafe'/version/'native-reopen-preview.png')
bpy.ops.render.render(write_still=True)
report = {'ok': True, 'native_default_scene': scene.name, 'packed_images': len(images),
          'rendered_after_reopen': True, 'source_file_modified': False}
(root/'outputs/vvoori-cafe'/version/'native-reopen-verification.json').write_text(json.dumps(report, indent=2), encoding='utf-8')
print(json.dumps(report, indent=2))
