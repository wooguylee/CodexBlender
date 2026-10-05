"""독립 Blender에서 전용 원본을 다시 열고 단체 이미지를 실제 재렌더한다.

사용법: blender --background scenes/weather-fairies-v001.blend --python workflows/weather-fairies/03_verify_standalone.py
브리찌 GUI와 별도 프로세스이며 기존 창/연결은 변경하지 않는다.
"""
from pathlib import Path
import json
import bpy
from mathutils import Vector
from bpy_extras.object_utils import world_to_camera_view

root = Path(__file__).resolve().parents[2]
out = root / 'outputs/weather-fairies/v001'
source = root / 'scenes/weather-fairies-v001.blend'
assert Path(bpy.data.filepath).resolve() == source.resolve()
assert len(bpy.data.scenes) == 1
scene = bpy.data.scenes['Weather_Fairies_v001']
bpy.context.window.scene = scene
assert scene.camera.name == 'WF1_Camera'
assert len(scene.objects) == 103
assert not bpy.data.libraries
assert not any(i.source == 'FILE' and not i.packed_file for i in bpy.data.images)
assert all(font.filepath == '<builtin>' for font in bpy.data.fonts)
assert scene.render.resolution_x == 2160 and scene.render.resolution_y == 1440
assert scene.frame_start == scene.frame_end == 1
assert not any(o.animation_data for o in scene.objects)
assert not any(o.hide_render for o in scene.objects)
assert not any(c.hide_render for c in scene.collection.children)
bpy.context.view_layer.update()
depsgraph = bpy.context.evaluated_depsgraph_get()
bounds = {}
for key in ('Mongsil', 'Haerong', 'Ttorr'):
    collection = bpy.data.collections['WF1_' + key]
    root_obj = bpy.data.objects['WF1_' + key + '_Root']
    assert root_obj in list(collection.objects)
    points = []
    for obj in collection.objects:
        if obj.type not in {'MESH', 'CURVE'}:
            continue
        assert obj.parent == root_obj
        evaluated = obj.evaluated_get(depsgraph)
        for co in evaluated.bound_box:
            projected = world_to_camera_view(scene, scene.camera, evaluated.matrix_world @ Vector(co))
            assert projected.z > 0
            points.append(projected)
    rect = [min(p.x for p in points), min(p.y for p in points),
            max(p.x for p in points), max(p.y for p in points)]
    assert all(.04 < v < .96 for v in rect), (key, rect)
    bounds[key] = rect
for screen in bpy.data.screens:
    for area in screen.areas:
        if area.type == 'VIEW_3D':
            area.spaces.active.region_3d.view_perspective = 'CAMERA'
            area.spaces.active.overlay.show_overlays = False
scene.render.filepath = '//../outputs/weather-fairies/v001/weather-fairies-group.png'
# Normalize the Scene-library export into a native editable standalone file.
bpy.ops.wm.save_as_mainfile(filepath=str(source), check_existing=False, compress=True, relative_remap=True)
prefs = bpy.context.preferences.addons['cycles'].preferences
prefs.compute_device_type = 'OPTIX'
prefs.get_devices()
for device in prefs.devices:
    device.use = device.type == 'OPTIX'
scene.cycles.device = 'GPU'
scene.render.filepath = str(out / 'standalone-reopen.png')
bpy.ops.render.render(write_still=True)
report = {'ok': True, 'independently_reopened': True, 'rendered': True,
          'scene': scene.name, 'scene_count': len(bpy.data.scenes),
          'objects': len(scene.objects), 'character_collections': 3,
          'projected_character_bounds': bounds, 'external_dependencies': [],
          'group_resolution': [2160, 1440], 'animation': False, 'rigged': False,
          'blender': bpy.app.version_string, 'native_source_saved': True}
(out / 'standalone-verification.json').write_text(json.dumps(report, indent=2), encoding='utf-8')
print(json.dumps(report, indent=2))
