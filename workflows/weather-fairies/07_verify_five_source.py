"""독립 Blender에서 v002 원본의 5개 캐릭터와 단체 재렌더를 검사한다."""
from pathlib import Path
import json
import bpy
from mathutils import Vector
from bpy_extras.object_utils import world_to_camera_view

root = Path(__file__).resolve().parents[2]
out = root / 'outputs/weather-fairies/v002'
source = root / 'scenes/weather-fairies-v002.blend'
manifest = json.loads((out / 'render-manifest.json').read_text(encoding='utf-8'))
assert Path(bpy.data.filepath).resolve() == source.resolve()
assert len(bpy.data.scenes) == 1
scene = bpy.data.scenes[manifest['scene']]
bpy.context.window.scene = scene
assert scene.camera.name == manifest['camera']
assert len(scene.objects) == manifest['objects']
assert not bpy.data.libraries
assert not any(i.source == 'FILE' and not i.packed_file for i in bpy.data.images)
assert all(font.filepath == '<builtin>' for font in bpy.data.fonts)
assert (scene.render.resolution_x, scene.render.resolution_y) == (3200, 1600)
assert scene.frame_start == scene.frame_end == 1
assert not any(o.animation_data for o in scene.objects)
assert not any(o.hide_render for o in scene.objects)
assert not any(c.hide_render for c in scene.collection.children)
assert all(o.name.startswith('WF2_') for o in scene.objects)
bpy.context.view_layer.update()
depsgraph = bpy.context.evaluated_depsgraph_get()
bounds = {}
for key in manifest['characters']:
    collection = bpy.data.collections['WF2_' + key]
    root_obj = bpy.data.objects['WF2_' + key + '_Root']
    points = []
    for obj in collection.objects:
        if obj.type not in {'MESH', 'CURVE'}:
            continue
        assert obj.parent == root_obj
        evaluated = obj.evaluated_get(depsgraph)
        for corner in evaluated.bound_box:
            p = world_to_camera_view(scene, scene.camera, evaluated.matrix_world @ Vector(corner))
            assert p.z > 0
            points.append(p)
    rect = [min(p.x for p in points), min(p.y for p in points), max(p.x for p in points), max(p.y for p in points)]
    assert all(.03 < v < .97 for v in rect), (key, rect)
    bounds[key] = rect
assert sum(o.name.startswith('WF2_Songsong_CrystalSpoke_') for o in scene.objects) == 6
assert sum(o.name.startswith('WF2_Songsong_CrystalFork_') for o in scene.objects) == 12
assert bpy.data.objects['WF2_Solsol_BreezeBody'].type == 'MESH'
assert 'WF2_Solsol_SpiralCrest' not in bpy.data.objects  # fused into the continuous body
assert {'WF2_Solsol_UpperScarfTail', 'WF2_Solsol_LowerScarfTail'} <= set(scene.objects.keys())
for screen in bpy.data.screens:
    for area in screen.areas:
        if area.type == 'VIEW_3D':
            area.spaces.active.region_3d.view_perspective = 'CAMERA'
            area.spaces.active.overlay.show_overlays = False
scene.render.filepath = '//../outputs/weather-fairies/v002/weather-fairies-five.png'
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
          'scene': scene.name, 'scene_count': len(bpy.data.scenes), 'objects': len(scene.objects),
          'character_count': 5, 'projected_bounds': bounds, 'external_dependencies': [],
          'snow_spokes': 6, 'snow_forks': 12, 'wind_body_and_spiral_fused': True,
          'blender': bpy.app.version_string, 'native_source_saved': True, 'animation': False, 'rigged': False}
(out / 'standalone-verification.json').write_text(json.dumps(report, indent=2), encoding='utf-8')
print(json.dumps(report, indent=2))
