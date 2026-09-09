"""3단계: 6초/24fps. 집과 사람 심벌 등장 → 펼쳐지는 더가치 → 조명 이동 → 정지.

사용자가 설명한 ㄷ/ㅊ의 의미를 유지하며 원본 심벌 비율을 기준으로 결합한다.
"""
import json
import math
from mathutils import Vector

scene = bpy.context.scene
assert scene.name == 'Thegachi_Opening_v001'
assert not scene.objects['TG_house_d'].animation_data, 'Animation exists; inspect before modifying.'
collection = bpy.data.collections['Thegachi_Opening_v001']

# Keep the palette saturated; restrained highlights leave the original colors legible.
for name in ['TG_Blue_Gradient','TG_Yellow_Person']:
    p = bpy.data.materials[name].node_tree.nodes['Principled BSDF']
    p.inputs['Metallic'].default_value = .16
    p.inputs['Roughness'].default_value = .34
    p.inputs['Specular IOR Level'].default_value = .26
    p.inputs['Coat Weight'].default_value = .12
scene.objects['TG_Key'].data.energy = 750
scene.objects['TG_Fill'].data.energy = 400
scene.objects['TG_Top'].data.energy = 650
scene.objects['TG_Sweep'].data.energy = 0
scene.view_settings.exposure = -.35

# An unlit radial background remains a quiet navy, independent of the sweeping lamp.
back = bpy.data.materials['TG_Backdrop']
nodes, links = back.node_tree.nodes, back.node_tree.links
halo = next(n for n in nodes if n.type == 'VALTORGB')
emission = nodes.new('ShaderNodeEmission')
emission.inputs['Strength'].default_value = .75
links.new(halo.outputs['Color'], emission.inputs['Color'])
links.new(emission.outputs[0], nodes.get('Material Output').inputs['Surface'])

rig = bpy.data.objects.new('TG_LogoRig', None)
collection.objects.link(rig)
rig.empty_display_type = 'PLAIN_AXES'
parts = [scene.objects['TG_' + n] for n in ['house_d','person_ch','eo','g','a','i']]
for obj in parts:
    obj.parent = rig


def key(obj, frame, loc=None, scale=None, rot=None):
    if loc is not None:
        obj.location = loc
        obj.keyframe_insert('location', frame=frame)
    if scale is not None:
        obj.scale = (scale,)*3 if isinstance(scale, (int,float)) else scale
        obj.keyframe_insert('scale', frame=frame)
    if rot is not None:
        obj.rotation_euler = tuple(math.radians(v) for v in rot)
        obj.keyframe_insert('rotation_euler', frame=frame)


house, person = scene.objects['TG_house_d'], scene.objects['TG_person_ch']
# Map the original wordmark vector coordinates to the user-confirmed 209x192 icon.
# The icon's blue house is ~1.79x, yellow person ~1.26x the wordmark SVG shapes.
ICON_UNIT = .0235
for obj, factor, offset_x, offset_y in [
    (house, 1.79, 0., 0.),
    (person, 1.26, 100.-256.27*1.26, 86.-5.77*1.26),
]:
    cx, cy = obj['svg_center']
    icon_pos = ((cx*factor+offset_x-104.5)*ICON_UNIT,
                (96.-cy*factor-offset_y)*ICON_UNIT, .14 if obj == person else 0.)
    icon_scale = factor*ICON_UNIT/.025
    obj['icon_location'] = list(icon_pos)
    obj['icon_scale'] = icon_scale
    final_pos = list(obj['final_location'])
    key(obj, 1, loc=(icon_pos[0] + (-.9 if obj==house else 1.1), icon_pos[1]-.25, icon_pos[2]+.45), scale=.0001, rot=(0,-35 if obj==house else 35,0))
    key(obj, 10 if obj==house else 17, loc=(icon_pos[0] + (-.4 if obj==house else .5), icon_pos[1],icon_pos[2]+.18), scale=icon_scale*.82, rot=(0,-14 if obj==house else 14,0))
    key(obj, 24 if obj==house else 30, loc=icon_pos, scale=icon_scale, rot=(0,0,0))
    key(obj, 44, loc=icon_pos, scale=icon_scale, rot=(0,0,0))
    key(obj, 84, loc=final_pos, scale=1., rot=(0,0,0))
    key(obj, 144, loc=final_pos, scale=1., rot=(0,0,0))

for obj, start in zip([scene.objects['TG_'+n] for n in ['eo','g','a','i']], [51,55,59,63]):
    end = list(obj['final_location'])
    key(obj, 1, loc=(end[0],end[1]-.4,-.15), scale=.0001, rot=(0,-22,0))
    key(obj, start, loc=(end[0],end[1]-.4,-.15), scale=.0001, rot=(0,-22,0))
    key(obj, start+23, loc=end, scale=1., rot=(0,0,0))
    key(obj, 144, loc=end, scale=1., rot=(0,0,0))

key(rig, 1, rot=(12,-20,-4))
key(rig, 26, rot=(6,-10,-2))
key(rig, 44, rot=(3,-5,0))
key(rig, 86, rot=(0,0,0))
key(rig, 144, rot=(0,0,0))
cam = scene.camera
for frame, scale in [(1,11.5),(30,11.5),(44,11.5),(86,12.7),(144,12.7)]:
    cam.data.ortho_scale = scale
    cam.data.keyframe_insert('ortho_scale', frame=frame)

sweep = scene.objects['TG_Sweep']
for frame, x, energy in [(1,-6,0),(84,-6,0),(90,-5,220),(104,0,220),(119,5.5,0),(144,5.5,0)]:
    key(sweep, frame, loc=(x,1.,4.))
    sweep.data.energy = energy
    sweep.data.keyframe_insert('energy', frame=frame)

# Set ease handles on all action slots (Blender 5's layered Action representation).
def curves(action):
    for layer in action.layers:
        for strip in layer.strips:
            for bag in strip.channelbags:
                yield from bag.fcurves

for obj in [*parts, rig, sweep, sweep.data, cam.data]:
    if obj.animation_data and obj.animation_data.action:
        for fc in curves(obj.animation_data.action):
            for k in fc.keyframe_points:
                k.interpolation = 'BEZIER'
                k.handle_left_type = k.handle_right_type = 'AUTO_CLAMPED'

for frame, title in [(1,'01 등장'),(30,'02 집과 사람'),(44,'03 펼치기'),(86,'04 더가치 완성'),(104,'05 빛의 이동'),(120,'06 최종 홀드')]:
    scene.timeline_markers.new(title, frame=frame)
scene.frame_start, scene.frame_end, scene.render.fps = 1,144,24
scene.frame_set(120)
scene['opening_duration_seconds'] = 6
scene['opening_story'] = '집과 사람이 만남 → 심벌에서 더가치로 펼쳐짐 → 조명 이동 → 정면 홀드'
scene['audio'] = 'Silent master; no music or external assets.'
scene.render.resolution_x, scene.render.resolution_y = 1280,720
report = {'frames':144,'fps':24,'duration_seconds':6,'scene':scene.name,
          'animated_objects':[o.name for o in parts],
          'original_scene_preserved':'Scene' in bpy.data.scenes,
          'timeline':[{'frame':m.frame,'name':m.name} for m in scene.timeline_markers]}
(OUTPUT_DIR/'animation.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps(report,ensure_ascii=False))
