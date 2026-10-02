"""사용자 정정: 직접 생성한 공원/카페 PNG를 활용한다. 렌더 추출본을 재사용하지 않는다.

v001 Scene/원본은 보존하고, 이미지와 3D 움직임을 v002에서 독립 합성한다.
"""
import hashlib
import json

import bpy

source = bpy.data.scenes['Vvoori_Cafe_v001']
assert source.camera.name == 'VC_Camera'
assert 'Vvoori_Cafe_v002' not in bpy.data.scenes
out = PROJECT_ROOT/'outputs/vvoori-cafe/v002'
assets = PROJECT_ROOT/'assets/vvoori-cafe/v002'
old_paths = ['scenes/vvoori-cafe-v001.blend', 'scenes/autumn-cafe-v001.blend',
             'outputs/vvoori-cafe/v001/vvoori-cafe-review-20s.mp4']
hashes = {p: hashlib.sha256((PROJECT_ROOT/p).read_bytes()).hexdigest() for p in old_paths}
prior = {s.name: sorted(o.name for o in s.objects) for s in bpy.data.scenes}
scene = source.copy()
scene.name = 'Vvoori_Cafe_v002'
bpy.context.window.scene = scene
for collection in list(scene.collection.children):
    scene.collection.children.unlink(collection)
objects, materials = {}, {}
for old_collection in source.collection.children:
    collection = bpy.data.collections.new(old_collection.name.replace('VC_', 'VC2_', 1))
    scene.collection.children.link(collection)
    for old in old_collection.objects:
        new = old.copy()
        new.name = old.name.replace('VC_', 'VC2_', 1)
        if old.data:
            new.data = old.data.copy()
            new.data.name = new.name
            if hasattr(new.data, 'materials'):
                for i, material in enumerate(new.data.materials):
                    if material:
                        if material not in materials:
                            materials[material] = material.copy()
                            materials[material].name = material.name.replace('VC_', 'VC2_', 1)
                        new.data.materials[i] = materials[material]
        collection.objects.link(new)
        objects[old] = new
for old, new in objects.items():
    if old.parent:
        new.parent = objects[old.parent]
scene.camera = objects[source.camera]
scene.world = source.world.copy()
scene.world.name = 'VC2_AfternoonWorld'
ng = source.compositing_node_group.copy()
ng.name = 'VC2_AI park + 3D traffic + AI cafe'
scene.compositing_node_group = ng
moving = ng.nodes['02_CarsAndLeaves']
moving.scene = scene
images = {}
for node_name, filename in [('01_ParkBackground', 'ai-autumn-park.png'),
                             ('04_CafeForeground', 'ai-cafe-foreground.png')]:
    image = bpy.data.images.load(str(assets/filename), check_existing=False)
    image.name = 'VC2_'+filename
    image.colorspace_settings.name = 'sRGB'
    image.alpha_mode = 'STRAIGHT'
    image.pack()
    image.filepath = '//../assets/vvoori-cafe/v002/'+filename
    ng.nodes[node_name].image = image
    ng.nodes[node_name].label = 'AI generated | '+filename
    images[node_name] = image

# The generated RGBA has solid surfaces around alpha=253/255. Preserve the PNG,
# normalize only the compositor alpha so cars cannot leak through solid furniture.
# Values below the ceiling retain antialiased fractional coverage.
cafe = ng.nodes['04_CafeForeground']
fit = ng.nodes['04_CafeForeground_FitRenderSize']
alpha = ng.nodes.new('ShaderNodeMath')
alpha.name = 'VC2_NormalizeGeneratedAlpha'
alpha.operation = 'MULTIPLY'
alpha.use_clamp = True
alpha.inputs[1].default_value = 255/250
ng.links.new(cafe.outputs['Alpha'], alpha.inputs[0])
set_alpha = ng.nodes.new('CompositorNodeSetAlpha')
set_alpha.name = 'VC2_CafeAlpha'
set_alpha.inputs['Type'].default_value = 'Replace Alpha'
ng.links.new(cafe.outputs['Image'], set_alpha.inputs['Image'])
ng.links.new(alpha.outputs[0], set_alpha.inputs['Alpha'])
ng.links.new(set_alpha.outputs['Image'], fit.inputs['Image'])

# PNGs are display-referred photographs: Standard provides one sRGB decode/encode,
# preventing an additional AgX tone-map from changing the generated images.
scene.view_settings.view_transform = 'Standard'
scene.view_settings.look = 'None'
scene.view_settings.exposure = 0
scene.view_settings.gamma = 1
scene.render.image_settings.file_format = 'PNG'
scene.render.image_settings.color_mode = 'RGB'
scene.render.resolution_percentage = 100
scene.cycles.samples = 32
prefs = bpy.context.preferences.addons['cycles'].preferences
prefs.compute_device_type = 'OPTIX'; prefs.get_devices()
for device in prefs.devices:
    device.use = device.type == 'OPTIX'
scene.cycles.device = 'GPU'
for bg in list(scene.camera.data.background_images):
    scene.camera.data.background_images.remove(bg)
for key, depth in [('01_ParkBackground', 'BACK'), ('04_CafeForeground', 'FRONT')]:
    bg = scene.camera.data.background_images.new()
    bg.image = images[key]; bg.alpha = 1; bg.display_depth = depth; bg.frame_method = 'FIT'
scene['workflow'] = 'Built-in image_gen PNGs + Blender 3D cars/leaves'
scene['source_project'] = 'vvoori-cafe v001 motion only; newly AI-generated static images'
scene['background_plate'] = 'assets/vvoori-cafe/v002/ai-autumn-park.png'
scene['foreground_plate'] = 'assets/vvoori-cafe/v002/ai-cafe-foreground.png'
scene['static_images_are_ai_generated'] = True
scene.render.filepath = '//../outputs/vvoori-cafe/v002/master-frames/'
scene.frame_set(2); scene.frame_set(1)
bpy.context.view_layer.update()
assert not set(scene.objects).intersection(source.objects)
assert all(sorted(o.name for o in bpy.data.scenes[n].objects) == old for n, old in prior.items())
assert all(hashlib.sha256((PROJECT_ROOT/p).read_bytes()).hexdigest() == h for p, h in hashes.items())
report = {'ok': True, 'scene': scene.name, 'camera': scene.camera.name,
          'objects': len(scene.objects), 'generated_static_images': True,
          'images': {n: {'file': im.filepath, 'size': list(im.size), 'packed': bool(im.packed_file)} for n, im in images.items()},
          'source_hashes': hashes, 'alpha_ceiling': 250/255,
          'view_transform': scene.view_settings.view_transform}
(out/'project-build.json').write_text(json.dumps(report, indent=2), encoding='utf-8')
print(json.dumps(report, indent=2))
