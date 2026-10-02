"""vvoori-cafe: autumn-cafe에서 공원/카페를 이미지로, 차량/낙엽만 3D로 분리.

사용자 요청(2026-10-02): 제작 방식을 비교해 추천하고 독립 프로젝트 생성.
브리찌로 실행한다. 원본 Scene/객체를 수정하지 않고 새 Scene만 생성한다.
"""
import hashlib
import json
import time

import bpy

source = bpy.data.scenes['Autumn_Cafe_v001']
assert source.camera.name == 'AC_Camera'
assert 'Vvoori_Cafe_v001' not in bpy.data.scenes, 'Use a revision script for an existing project.'
# Session-only device selection; no save_userpref or global settings changes.
prefs = bpy.context.preferences.addons['cycles'].preferences
prefs.compute_device_type = 'OPTIX'
prefs.get_devices()
assert any(d.type == 'OPTIX' for d in prefs.devices)
for device in prefs.devices:
    device.use = device.type == 'OPTIX'
root = PROJECT_ROOT
out = root / 'outputs/vvoori-cafe/v001'
assets = root / 'assets/vvoori-cafe/v001'
out.mkdir(parents=True, exist_ok=True)
assets.mkdir(parents=True, exist_ok=True)
assert not list(assets.glob('*.exr')), 'Existing plates must be versioned.'
prior = {s.name: sorted(o.name for o in s.objects) for s in bpy.data.scenes}
old_files = [root/'scenes/autumn-cafe-v001.blend',
             root/'outputs/autumn-cafe/v001/autumn-cafe-20s-loop.mp4']
old_hashes = {str(p.relative_to(root)): hashlib.sha256(p.read_bytes()).hexdigest() for p in old_files}

# This temporary Scene shares read-only geometry, with independent View Layer flags.
# Indirect-only preserves lighting/shadows without including that set in camera rays.
bake = source.copy()
bake.name = 'VC_PlateBake_Temporary'
bake.compositing_node_group = None
bpy.context.window.scene = bake
layer = bake.view_layers.new('VC_PlateBake')
for other in list(bake.view_layers):
    if other != layer:
        bake.view_layers.remove(other)
bpy.context.window.view_layer = layer
for child in layer.layer_collection.children:
    child.exclude = False
    child.holdout = False
    child.indirect_only = False
for name in ['AC_Traffic', 'AC_FallingLeaves', 'AC_StaticGlass']:
    layer.layer_collection.children[name].exclude = True
bake.render.resolution_percentage = 100
bake.cycles.samples = 160
bake.cycles.use_adaptive_sampling = False
bake.cycles.use_animated_seed = False
bake.render.image_settings.file_format = 'OPEN_EXR'
bake.render.image_settings.color_mode = 'RGBA'
bake.render.image_settings.color_depth = '16'
bake.frame_set(1)
plates = {}
timings = {}
for key, hidden, transparent in [
    ('park-background', 'AC_Interior', False),
    ('cafe-foreground', 'AC_Park', True),
]:
    for name in ['AC_Interior', 'AC_Park']:
        layer.layer_collection.children[name].indirect_only = name == hidden
    bake.render.film_transparent = transparent
    path = assets / (key + '.exr')
    bake.render.filepath = str(path)
    start = time.monotonic()
    bpy.ops.render.render(write_still=True)
    timings[key] = time.monotonic() - start
    image = bpy.data.images.load(str(path), check_existing=False)
    image.name = 'VC_' + key
    image.pack()
    image.filepath = '//../assets/vvoori-cafe/v001/' + path.name
    plates[key] = image
    # PNGs are display-referred review/interchange files, not the linear master.
    bake.render.image_settings.file_format = 'PNG'
    bake.render.image_settings.color_depth = '16'
    image.save_render(str(assets / (key + '.png')), scene=bake)
    bake.render.image_settings.file_format = 'OPEN_EXR'
    bake.render.image_settings.color_depth = '16'
    print('VVOORI PLATE', key, timings[key], flush=True)

scene = source.copy()
scene.name = 'Vvoori_Cafe_v001'
bpy.context.window.scene = scene
for child in list(scene.collection.children):
    scene.collection.children.unlink(child)
fx = scene.view_layers.new('VC_MovingCarsAndLeaves')
for other in list(scene.view_layers):
    if other != fx:
        scene.view_layers.remove(other)
bpy.context.window.view_layer = fx
scene.world = source.world.copy()
scene.world.name = 'VC_AfternoonWorld'
objects = {}
materials = {}
for old_collection, new_name in [
    ('AC_Traffic', 'VC_Traffic'),
    ('AC_FallingLeaves', 'VC_FallingLeaves'),
    ('AC_LightingCamera', 'VC_LightingCamera'),
]:
    collection = bpy.data.collections.new(new_name)
    scene.collection.children.link(collection)
    for old in bpy.data.collections[old_collection].objects:
        new = old.copy()
        new.name = 'VC_' + old.name.removeprefix('AC_')
        if old.data:
            new.data = old.data.copy()
            new.data.name = new.name
            if hasattr(new.data, 'materials'):
                for i, material in enumerate(new.data.materials):
                    if material:
                        if material not in materials:
                            materials[material] = material.copy()
                            materials[material].name = 'VC_' + material.name.removeprefix('AC_')
                        new.data.materials[i] = materials[material]
        collection.objects.link(new)
        objects[old] = new
for old, new in objects.items():
    if old.parent:
        new.parent = objects[old.parent]
scene.camera = objects[source.camera]
scene.camera.data.show_background_images = True
for key, depth in [('park-background', 'BACK'), ('cafe-foreground', 'FRONT')]:
    bg = scene.camera.data.background_images.new()
    bg.image = plates[key]
    bg.display_depth = depth
    bg.alpha = 1
    bg.frame_method = 'FIT'

ng = bpy.data.node_groups.new('VC_Park + CarsLeaves + Cafe', 'CompositorNodeTree')
ng.interface.new_socket(name='Image', in_out='OUTPUT', socket_type='NodeSocketColor')
park = ng.nodes.new('CompositorNodeImage')
park.name = '01_ParkBackground'; park.label = '01 | Park background (linear EXR)'
park.image = plates['park-background']; park.location = (-620, 160)
moving = ng.nodes.new('CompositorNodeRLayers')
moving.name = '02_CarsAndLeaves'; moving.label = '02 | 3D cars, contact shadows, leaves'
moving.scene = scene; moving.layer = fx.name; moving.location = (-620, -80)
under = ng.nodes.new('CompositorNodeAlphaOver')
under.name = '03_MotionOverPark'; under.location = (-320, 160)
ng.links.new(park.outputs['Image'], under.inputs['Background'])
ng.links.new(moving.outputs['Image'], under.inputs['Foreground'])
cafe = ng.nodes.new('CompositorNodeImage')
cafe.name = '04_CafeForeground'; cafe.label = '04 | Cafe and window frame (RGBA EXR)'
cafe.image = plates['cafe-foreground']; cafe.location = (-320, -140)
over = ng.nodes.new('CompositorNodeAlphaOver')
over.name = '05_CafeOverMotion'; over.location = (0, 160)
ng.links.new(under.outputs['Image'], over.inputs['Background'])
ng.links.new(cafe.outputs['Image'], over.inputs['Foreground'])
output = ng.nodes.new('NodeGroupOutput'); output.location = (260, 160)
ng.links.new(over.outputs['Image'], output.inputs['Image'])
scene.compositing_node_group = ng
scene.render.film_transparent = True
scene.render.resolution_percentage = 100
scene.render.image_settings.file_format = 'PNG'
scene.render.image_settings.color_mode = 'RGB'
scene.render.image_settings.color_depth = '8'
scene.render.filepath = '//../outputs/vvoori-cafe/v001/master-frames/'
scene.cycles.samples = 32
scene['project_name'] = 'vvoori-cafe'
scene['background_plate'] = 'assets/vvoori-cafe/v001/park-background.exr'
scene['foreground_plate'] = 'assets/vvoori-cafe/v001/cafe-foreground.exr'
scene['workflow'] = 'Two packed still images with an independent 3D motion layer'
scene['source_project'] = 'autumn-cafe v001; independently copied moving objects/materials/world'
scene.frame_set(2); scene.frame_set(1)
bpy.context.view_layer.update()
bpy.data.scenes.remove(bake)
assert not set(scene.objects).intersection(source.objects)
assert all(sorted(o.name for o in bpy.data.scenes[name].objects) == names for name, names in prior.items())
assert all(hashlib.sha256((root/p).read_bytes()).hexdigest() == h for p, h in old_hashes.items())
assert all(im.packed_file for im in plates.values())
for screen in bpy.data.screens:
    for area in screen.areas:
        if area.type == 'VIEW_3D':
            area.spaces.active.region_3d.view_perspective = 'CAMERA'
report = {
    'ok': True, 'scene': scene.name, 'camera': scene.camera.name,
    'source_objects': len(source.objects), 'new_objects': len(scene.objects),
    'collections': [c.name for c in scene.collection.children],
    'packed_plates': [im.name for im in plates.values()],
    'plate_seconds': timings, 'source_hashes': old_hashes,
    'source_scenes_preserved': True, 'shared_objects': 0,
    'width': 1920, 'height': 1080, 'fps': 24, 'frames': 480,
}
(out/'project-build.json').write_text(json.dumps(report, indent=2), encoding='utf-8')
print(json.dumps(report, indent=2))
