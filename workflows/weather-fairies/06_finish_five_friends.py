"""눈송이/바람 실제 미리보기 검토 반영 및 v002 최종 정지 이미지 출력.

바람의 소용돌이·머리·몸 경계를 매끈하게 융합하고 눈송이 대비를 보정한다.
5인조 단체 2종, 신규 듀오 1종, 신규 개별 2종을 저장한다.
"""
import json
from mathutils import Vector
from bpy_extras.object_utils import world_to_camera_view

scene = bpy.data.scenes['Weather_Fairies_v002']
assert bpy.context.scene == scene
out = PROJECT_ROOT / 'outputs/weather-fairies/v002'
assert not (out / 'weather-fairies-five.png').exists()
keys = ('Mongsil', 'Haerong', 'Ttorr', 'Songsong', 'Solsol')
studio = bpy.data.collections['WF2_Studio']


def rgb(h):
    values = [int(h[i:i + 2], 16) / 255 for i in (0, 2, 4)]
    return tuple(v / 12.92 if v <= .04045 else ((v + .055) / 1.055) ** 2.4 for v in values)


# The wind's three original parts become one smooth, editable mesh.
body = bpy.data.objects['WF2_Solsol_BreezeBody']
crest = bpy.data.objects['WF2_Solsol_SpiralCrest']
cap = bpy.data.objects['WF2_Solsol_HeadSweep']
bpy.ops.object.select_all(action='DESELECT')
crest.select_set(True)
bpy.context.view_layer.objects.active = crest
bpy.ops.object.convert(target='MESH')
crest = bpy.context.object
bpy.ops.object.select_all(action='DESELECT')
for obj in (body, crest, cap):
    obj.select_set(True)
bpy.context.view_layer.objects.active = body
bpy.ops.object.join()
bpy.ops.object.transform_apply(location=False, rotation=True, scale=True)
remesh = body.modifiers.new('Continuous_breeze_surface', 'REMESH')
remesh.mode = 'VOXEL'
remesh.voxel_size = .023
remesh.use_smooth_shade = True
bpy.ops.object.modifier_apply(modifier=remesh.name)
smooth = body.modifiers.new('Smooth_spiral_junctions', 'SMOOTH')
smooth.factor = 1.0
smooth.iterations = 5
sub = body.modifiers.new('Silky_breeze_surface', 'SUBSURF')
sub.levels = sub.render_levels = 1
mat = bpy.data.materials['WF2_Snow_pearl']
mat.diffuse_color = (*rgb('C5DCF3'), 1)
mat.node_tree.nodes['Principled BSDF'].inputs['Base Color'].default_value = (*rgb('C5DCF3'), 1)

scene.render.resolution_x = 3200
scene.render.resolution_y = 1600
scene.cycles.samples = 96
scene.cycles.adaptive_threshold = .015
camera = scene.camera
camera_position = camera.location.copy()
camera_rotation = camera.rotation_euler.copy()
camera_scale = camera.data.ortho_scale

# Camera-facing native lettering, with the same typography as the first edition.
typography = bpy.data.collections.new('WF2_Typography')
scene.collection.children.link(typography)
text_mat = bpy.data.materials['WF1_TypographyInk'].copy()
text_mat.name = 'WF2_TypographyInk'


def label(name, text, u, v, size, spacing=1.1):
    q = camera.rotation_euler.to_quaternion()
    right, up, forward = q @ Vector((1, 0, 0)), q @ Vector((0, 1, 0)), q @ Vector((0, 0, -1))
    plane = camera.location + forward * 12
    width = camera.data.ortho_scale
    height = width * scene.render.resolution_y / scene.render.resolution_x
    data = bpy.data.curves.new('WF2_' + name, 'FONT')
    data.body = text
    data.align_x = data.align_y = 'CENTER'
    data.size = size
    data.space_character = spacing
    data.resolution_u = 12
    obj = bpy.data.objects.new('WF2_' + name, data)
    typography.objects.link(obj)
    obj.location = plane + right * ((u - .5) * width) + up * ((.5 - v) * height)
    obj.rotation_euler = camera.rotation_euler
    data.materials.append(text_mat)
    obj.visible_shadow = obj.visible_diffuse = obj.visible_glossy = obj.visible_transmission = False
    return obj


label('Title', "TODAY'S WEATHER", .5, .13, .43, 1.16)
label('Subtitle', 'FIVE LITTLE FRIENDS, EVERY DAY.', .5, .18, .14, 1.16)
bpy.context.view_layer.update()
descriptions = ('THE SLEEPY CLOUD', 'A LITTLE SUNSHINE', 'THE SHY RAINDROP', 'THE PLAYFUL SNOWFLAKE', 'A GENTLE BREEZE')
for key, description in zip(keys, descriptions):
    base = bpy.data.objects['WF2_' + key + '_Plinth']
    u = world_to_camera_view(scene, camera, base.location).x
    label(key + '_Label', key.upper(), u, .815, .177, 1.15)
    label(key + '_Subtitle', description, u, .852, .088, 1.12)
label('Edition', 'WEATHER FAIRIES   /   THE COMPLETE FIVE', .5, .942, .093, 1.15)
scene.render.filepath = str(out / 'weather-fairies-five.png')
bpy.ops.render.render(write_still=True)
typography.hide_render = True
scene.render.filepath = str(out / 'weather-fairies-five-clean.png')
bpy.ops.render.render(write_still=True)

# New-character presentation and closeups use the same actual geometry.
props = [o for o in studio.objects if o.type not in {'LIGHT', 'CAMERA'} and o.name != 'WF2_Studio_Floor']


def show_only(selected):
    for key in keys:
        bpy.data.collections['WF2_' + key].hide_render = key not in selected
    for obj in props:
        obj.hide_render = True
    for key in selected:
        index = keys.index(key)
        bpy.data.objects['WF2_' + key + '_Plinth'].hide_render = False
        bpy.data.objects['WF2_Plinth_trim_' + str(index)].hide_render = False


show_only(('Songsong', 'Solsol'))
target = Vector((4.98, .05, 1.79))
camera.location = target + Vector((1.6, -22, 6.3))
camera.rotation_euler = (target - camera.location).to_track_quat('-Z', 'Y').to_euler()
camera.data.ortho_scale = 8.2
scene.render.resolution_x, scene.render.resolution_y = 2160, 1440
scene.render.filepath = str(out / 'snow-and-wind.png')
bpy.ops.render.render(write_still=True)
for key in ('Songsong', 'Solsol'):
    show_only((key,))
    origin = bpy.data.objects['WF2_' + key + '_Root'].location
    target = Vector((origin.x + (.14 if key == 'Solsol' else 0), origin.y, 1.82))
    camera.location = target + Vector((1.6, -20, 5.7))
    camera.rotation_euler = (target - camera.location).to_track_quat('-Z', 'Y').to_euler()
    camera.data.ortho_scale = 4.45
    scene.render.resolution_x = scene.render.resolution_y = 1080
    scene.render.filepath = str(out / (key.lower() + '.png'))
    bpy.ops.render.render(write_still=True)

for key in keys:
    bpy.data.collections['WF2_' + key].hide_render = False
for obj in props:
    obj.hide_render = False
typography.hide_render = False
camera.location = camera_position
camera.rotation_euler = camera_rotation
camera.data.ortho_scale = camera_scale
scene.render.resolution_x, scene.render.resolution_y = 3200, 1600
scene.render.filepath = '//../outputs/weather-fairies/v002/weather-fairies-five.png'
bpy.context.view_layer.update()
source = PROJECT_ROOT / 'scenes/weather-fairies-v002.blend'
assert not source.exists()
bpy.data.libraries.write(str(source), {scene}, path_remap='RELATIVE', fake_user=True, compress=True)
manifest = {'ok': True, 'scene': scene.name, 'camera': camera.name, 'objects': len(scene.objects),
            'characters': list(keys), 'new_characters_ko': ['송송', '솔솔'],
            'source': 'scenes/weather-fairies-v002.blend', 'samples': 96,
            'files': {'weather-fairies-five.png': [3200, 1600],
                      'weather-fairies-five-clean.png': [3200, 1600],
                      'snow-and-wind.png': [2160, 1440],
                      'songsong.png': [1080, 1080], 'solsol.png': [1080, 1080]},
            'external_dependencies': [], 'animation': False, 'rigged': False}
(out / 'render-manifest.json').write_text(json.dumps(manifest, indent=2, ensure_ascii=False), encoding='utf-8')
print(json.dumps({'ok': True, 'objects': len(scene.objects), 'images': 5}, indent=2))
