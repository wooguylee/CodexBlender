"""첫 실제 렌더 검토 반영: 파스텔 대비, 해롱 웃음, 단체/개별 정지 이미지.

새 WF1 객체만 수정한다. 기존 첫 시안/결과는 삭제하지 않는다.
"""
import json
import math
from mathutils import Vector

scene = bpy.data.scenes['Weather_Fairies_v001']
assert bpy.context.scene == scene
out = PROJECT_ROOT / 'outputs/weather-fairies/v001'
assert not (out / 'weather-fairies-group.png').exists()
studio = bpy.data.collections['WF1_Studio']


def rgb(h):
    values = [int(h[i:i + 2], 16) / 255 for i in (0, 2, 4)]
    return tuple(v / 12.92 if v <= .04045 else ((v + .055) / 1.055) ** 2.4 for v in values)


scene.view_settings.exposure = 0
for name, color in [('Sun_butter', 'FFCA4F'), ('Sun_mango', 'F8A33F'),
                    ('Raindrop_blue', '50BDE3'), ('Sleep_lilac', 'AD9FDA')]:
    mat = bpy.data.materials['WF1_' + name]
    mat.diffuse_color = (*rgb(color), 1)
    mat.node_tree.nodes['Principled BSDF'].inputs['Base Color'].default_value = (*rgb(color), 1)

# Replace only this version's initial oval mouth with a proper open smile.
old = bpy.data.objects['WF1_Haerong_OpenSmile']
parent = old.parent
bpy.data.objects.remove(old, do_unlink=True)
points = [(-.16, 0), (-.08, -.012), (0, -.016), (.08, -.012), (.16, 0)]
points += [(.16 * math.cos(math.pi * i / 24), -.145 * math.sin(math.pi * i / 24))
           for i in range(1, 25)]
mesh = bpy.data.meshes.new('WF1_Haerong_SmileMesh')
mesh.from_pydata([(x, -.53, 1.988 + z) for x, z in points], [], [tuple(range(len(points)))])
mesh.update()
mouth = bpy.data.objects.new('WF1_Haerong_OpenSmile', mesh)
bpy.data.collections['WF1_Haerong'].objects.link(mouth)
mouth.parent = parent
mesh.materials.append(bpy.data.materials['WF1_Expression_cocoa'])
mod = mouth.modifiers.new('Soft_inlaid_smile', 'SOLIDIFY')
mod.thickness = .012
tongue = bpy.data.objects['WF1_Haerong_Tongue']
tongue.location = (0, -.543, 1.867)
tongue.scale = (.087, .012, .029)

# Flat native text sits in the camera plane, keeping artwork self-contained.
typography = bpy.data.collections.new('WF1_Typography')
scene.collection.children.link(typography)
text_mat = bpy.data.materials.new('WF1_TypographyInk')
text_mat.diffuse_color = (*rgb('62536A'), 1)
text_mat.use_nodes = True
nodes = text_mat.node_tree.nodes
nodes.clear()
emission = nodes.new('ShaderNodeEmission')
emission.inputs['Color'].default_value = (*rgb('62536A'), 1)
output = nodes.new('ShaderNodeOutputMaterial')
text_mat.node_tree.links.new(emission.outputs[0], output.inputs['Surface'])
camera = scene.camera
q = camera.rotation_euler.to_quaternion()
right, up, forward = q @ Vector((1, 0, 0)), q @ Vector((0, 1, 0)), q @ Vector((0, 0, -1))
plane_center = camera.location + forward * 12
width = camera.data.ortho_scale
height = width / 1.5


def label(name, text, u, v, size, spacing=1.1):
    data = bpy.data.curves.new('WF1_' + name, 'FONT')
    data.body = text
    data.align_x = 'CENTER'
    data.align_y = 'CENTER'
    data.size = size
    data.space_character = spacing
    data.resolution_u = 12
    o = bpy.data.objects.new('WF1_' + name, data)
    typography.objects.link(o)
    o.location = plane_center + right * ((u - .5) * width) + up * ((.5 - v) * height)
    o.rotation_euler = camera.rotation_euler
    data.materials.append(text_mat)
    o.visible_shadow = False
    o.visible_diffuse = False
    o.visible_glossy = False
    o.visible_transmission = False
    return o


label('Title', "TODAY'S WEATHER", .5, .112, .39, 1.16)
label('Subtitle', 'LITTLE FRIENDS, EVERY DAY.', .5, .157, .115, 1.20)
for u, name, description in [(.237, 'MONGSIL', 'THE SLEEPY CLOUD'),
                             (.506, 'HAERONG', 'A LITTLE SUNSHINE'),
                             (.764, 'TTORR', 'THE SHY RAINDROP')]:
    label(name + '_Label', name, u, .847, .165, 1.18)
    label(name + '_Subtitle', description, u, .875, .086, 1.12)
label('Edition', 'WEATHER FAIRIES   /   FIRST EDITION', .5, .953, .077, 1.22)

scene.render.resolution_x = 2160
scene.render.resolution_y = 1440
scene.cycles.samples = 96
scene.cycles.adaptive_threshold = .015
scene.render.filepath = str(out / 'weather-fairies-group.png')
bpy.ops.render.render(write_still=True)

# The clean plate is useful for further character work without typography.
typography.hide_render = True
scene.render.filepath = str(out / 'weather-fairies-clean.png')
bpy.ops.render.render(write_still=True)

group_camera_position = camera.location.copy()
group_camera_rotation = camera.rotation_euler.copy()
group_scale = camera.data.ortho_scale
studio_props = [o for o in studio.objects if o.type not in {'LIGHT', 'CAMERA'} and o.name != 'WF1_Studio_Floor']
for o in studio_props:
    o.hide_render = True
portraits = []
for index, key in enumerate(('Mongsil', 'Haerong', 'Ttorr')):
    for character in ('Mongsil', 'Haerong', 'Ttorr'):
        bpy.data.collections['WF1_' + character].hide_render = character != key
    for name in (f'WF1_{key}_Plinth', f'WF1_Plinth_trim_{index}'):
        bpy.data.objects[name].hide_render = False
    root = bpy.data.objects[f'WF1_{key}_Root']
    target = Vector((root.location.x, root.location.y, 1.72))
    camera.location = target + Vector((2.5, -20, 5.8))
    camera.rotation_euler = (target - camera.location).to_track_quat('-Z', 'Y').to_euler()
    camera.data.ortho_scale = 4.5 if key != 'Ttorr' else 4.05
    scene.render.resolution_x = scene.render.resolution_y = 1080
    scene.render.filepath = str(out / (key.lower() + '.png'))
    bpy.ops.render.render(write_still=True)
    portraits.append(key.lower() + '.png')
    for name in (f'WF1_{key}_Plinth', f'WF1_Plinth_trim_{index}'):
        bpy.data.objects[name].hide_render = True

# Leave the user in the final group composition; the bridge also renders its preview.
for key in ('Mongsil', 'Haerong', 'Ttorr'):
    bpy.data.collections['WF1_' + key].hide_render = False
for o in studio_props:
    o.hide_render = False
typography.hide_render = False
camera.location = group_camera_position
camera.rotation_euler = group_camera_rotation
camera.data.ortho_scale = group_scale
scene.render.resolution_x = 2160
scene.render.resolution_y = 1440
scene.render.filepath = '//../outputs/weather-fairies/v001/weather-fairies-group.png'
bpy.context.view_layer.update()

# Write only this new Scene and its dependencies, excluding unrelated scene history.
source = PROJECT_ROOT / 'scenes/weather-fairies-v001.blend'
assert not source.exists()
bpy.data.libraries.write(str(source), {scene}, path_remap='RELATIVE', fake_user=True, compress=True)
report = {'ok': True, 'scene': scene.name, 'objects': len(scene.objects),
          'group': 'weather-fairies-group.png', 'clean': 'weather-fairies-clean.png',
          'portraits': portraits, 'resolution_group': [2160, 1440],
          'resolution_portraits': [1080, 1080], 'samples': 96,
          'source': 'scenes/weather-fairies-v001.blend',
          'source_export_method': 'Single Scene dependency closure; independent reopen required',
          'external_assets': [], 'animation': False, 'rigged': False}
(out / 'render-manifest.json').write_text(json.dumps(report, indent=2), encoding='utf-8')
print(json.dumps(report, indent=2))
