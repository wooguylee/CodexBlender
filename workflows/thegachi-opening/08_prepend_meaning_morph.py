"""사용자 요청: 현재 영상 앞에 집→ㄷ, 사람→ㅊ 변화를 약 1초 추가한다.

v002 보존. 24fps 168프레임 v003. 새 그림/한글 변환 후 기존 심벌 등장에 연결.
기존 25–144프레임의 채널 값을 매 프레임 보존하여 새 49–168프레임으로 이동한다.
"""
import json
import math
from mathutils import Vector

scene = bpy.context.scene
assert scene.name == 'Thegachi_Opening_v002'
assert 'TG_IntroIllustrations' not in bpy.data.collections
names = ['TG_house_d','TG_person_ch','TG_eo','TG_g','TG_a','TG_i','TG_LogoRig','TG_Sweep']
objects = [scene.objects[n] for n in names]
camera = scene.camera
lamp = scene.objects['TG_Sweep'].data
samples = {}
for frame in range(1,145):
    scene.frame_set(frame)
    samples[frame] = {'objects':{o.name:{'location':list(o.location),'rotation_euler':list(o.rotation_euler),'scale':list(o.scale)} for o in objects},
                      'camera_scale':camera.data.ortho_scale,'sweep_energy':lamp.energy}
for owner in [*objects,camera.data,lamp]:
    owner.animation_data_clear()
scene.name = 'Thegachi_Opening_v003'
scene['output_version'] = 'v003'
scene.frame_end = 168
scene['opening_duration_seconds'] = 7
scene['opening_story'] = '집 그림과 사람 그림 → ㄷ과 ㅊ → 기존 심벌 결합 → 더가치 완성'
scene['poster_frame'] = 144
scene['symbol_frame'] = 58
scene['review_frames'] = [1,10,18,28,58,144]
scene['prefix_frames'] = 24
out = PROJECT_ROOT/'outputs/thegachi-opening/v003'
out.mkdir(parents=True,exist_ok=True)


def ease(t):
    t=max(0,min(1,t))
    return t*t*(3-2*t)


intro_pose = {}
for obj in objects:
    pose = {k:list(v) for k,v in samples[24]['objects'][obj.name].items()}
    if obj.name in ['TG_house_d','TG_person_ch']:
        pose = {'location':[-2.15 if obj.name=='TG_house_d' else 2.15,0.,.12],
                'rotation_euler':[0,0,0],'scale':[1.05]*3}
    elif obj.name=='TG_LogoRig':
        pose = {'location':[0,0,0],'rotation_euler':[0,0,0],'scale':[1,1,1]}
    elif obj.name not in ['TG_Sweep']:
        pose['scale']=[.0001]*3
    intro_pose[obj.name]=pose

# Bake only existing animation channels; the tail's per-frame transforms remain identical.
for frame in range(1,169):
    blend = ease((frame-25)/23)
    old = samples[max(1,frame-24)] if frame>=49 else samples[24]
    for obj in objects:
        for channel in ['location','rotation_euler','scale']:
            value = old['objects'][obj.name][channel]
            if frame<49:
                start = intro_pose[obj.name][channel]
                value=[a+(b-a)*blend for a,b in zip(start,value)]
            setattr(obj,channel,value)
            obj.keyframe_insert(channel,frame=frame)
    camera.data.ortho_scale = old['camera_scale'] if frame>=49 else 11.5
    camera.data.keyframe_insert('ortho_scale',frame=frame)
    lamp.energy = old['sweep_energy'] if frame>=49 else 0
    lamp.keyframe_insert('energy',frame=frame)


def action_curves(owner):
    if owner.animation_data and owner.animation_data.action:
        for layer in owner.animation_data.action.layers:
            for strip in layer.strips:
                for bag in strip.channelbags:
                    yield from bag.fcurves


for owner in [*objects,camera.data,lamp]:
    for fc in action_curves(owner):
        for point in fc.keyframe_points:
            point.interpolation='LINEAR'


def opacity(mat, values):
    nodes,links=mat.node_tree.nodes,mat.node_tree.links
    output=nodes.get('Material Output')
    surface=output.inputs['Surface'].links[0].from_socket
    transparent=nodes.new('ShaderNodeBsdfTransparent')
    mix=nodes.new('ShaderNodeMixShader')
    links.new(transparent.outputs[0],mix.inputs[1])
    links.new(surface,mix.inputs[2])
    links.new(mix.outputs[0],output.inputs['Surface'])
    if hasattr(mat,'surface_render_method'):
        mat.surface_render_method='DITHERED'
    for frame,value in values:
        mix.inputs[0].default_value=value
        mix.inputs[0].keyframe_insert('default_value',frame=frame)
    return mix


for name in ['TG_house_d','TG_person_ch']:
    obj=scene.objects[name]
    mat=obj.data.materials[0].copy()
    mat.name='TG_v003_'+name+'_reveal'
    obj.data.materials[0]=mat
    opacity(mat,[(1,0),(18,0),(26,1),(168,1)])

intro=bpy.data.collections.new('TG_IntroIllustrations')
scene.collection.children.link(intro)


def own(obj,name):
    obj.name=name
    for col in list(obj.users_collection):
        col.objects.unlink(obj)
    intro.objects.link(obj)
    return obj


def color(code):
    vals=[int(code[i:i+2],16)/255 for i in (0,2,4)]
    return tuple(v/12.92 if v<=.04045 else ((v+.055)/1.055)**2.4 for v in vals)


def paint(name,code):
    mat=bpy.data.materials.new(name)
    mat.use_nodes=True
    p=mat.node_tree.nodes['Principled BSDF']
    p.inputs['Base Color'].default_value=(*color(code),1)
    p.inputs['Metallic'].default_value=.16
    p.inputs['Roughness'].default_value=.34
    p.inputs['Specular IOR Level'].default_value=.26
    opacity(mat,[(1,1),(18,1),(26,0),(168,0)])
    return mat


blue=paint('TG_Intro_Blue','036eb8')
gold=paint('TG_Intro_Gold','f9b341')


def sphere(name,location,radius,mat):
    bpy.ops.mesh.primitive_uv_sphere_add(segments=20,ring_count=12,radius=radius,location=location)
    obj=own(bpy.context.object,name)
    obj.data.materials.append(mat)
    for poly in obj.data.polygons:
        poly.use_smooth=True
    return obj


def stroke(name,start,end,target_start,target_end,center,mat,radius=.13,vanish=False):
    curve=bpy.data.curves.new(name,'CURVE')
    curve.dimensions='3D'
    curve.bevel_depth=radius
    curve.bevel_resolution=4
    curve.use_fill_caps=True
    spline=curve.splines.new('POLY')
    spline.points.add(1)
    obj=bpy.data.objects.new(name,curve)
    intro.objects.link(obj)
    obj.location=(center,0,.16)
    curve.materials.append(mat)
    caps=[sphere(name+'_cap'+str(i),(0,0,0),radius,mat) for i in range(2)]
    for cap in caps:
        cap.parent=obj
    for frame,t in [(1,0),(5,0),(16,1),(26,1)]:
        for i,(a,b) in enumerate([(start,target_start),(end,target_end)]):
            p=(a[0]+(b[0]-a[0])*t,a[1]+(b[1]-a[1])*t,0)
            spline.points[i].co=(*p,1)
            spline.points[i].keyframe_insert('co',frame=frame)
            caps[i].location=p
            caps[i].keyframe_insert('location',frame=frame)
        if vanish:
            scale=1 if t==0 else .0001
            obj.scale=(scale,)*3
            obj.keyframe_insert('scale',frame=frame)
    return obj


# Literal house: pitched roof, both walls, door and windows. Roof levels into ㄷ.
cx=-2.15
for name,a,b,c,d in [
    ('roof_left',(-1.1,.45),(0,1.35),(-1.1,1.1),(0,1.1)),
    ('roof_right',(0,1.35),(1.1,.45),(0,1.1),(1.1,1.1)),
    ('left_wall',(-1.1,.45),(-1.1,-1.1),(-1.1,1.1),(-1.1,-1.1)),
    ('floor',(-1.1,-1.1),(1.1,-1.1),(-1.1,-1.1),(1.1,-1.1)),
]:
    stroke('TG_Intro_House_'+name,a,b,c,d,cx,blue)
for name,a,b in [
    ('right_wall',(1.1,.45),(1.1,-1.1)),
    ('door_left',(-.25,-1.1),(-.25,-.35)),
    ('door_top',(-.25,-.35),(.25,-.35)),
    ('door_right',(.25,-.35),(.25,-1.1)),
    ('window_top',(-.8,.12),(-.48,.12)),
    ('window_left',(-.8,.12),(-.8,-.22)),
    ('window_bottom',(-.8,-.22),(-.48,-.22)),
    ('window_right',(-.48,-.22),(-.48,.12)),
]:
    stroke('TG_Intro_House_'+name,a,b,a,b,cx,blue,radius=.075 if name!='right_wall' else .13,vanish=True)

# Literal person: round head, body, lowered arms and legs. Head flattens to ㅊ's top bar.
cx=2.15
head=sphere('TG_Intro_Person_Head',(cx,1.02,.16),.28,gold)
for frame,scale in [(1,(1,1,1)),(5,(1,1,1)),(16,(1.35,.32,.7)),(26,(1.35,.32,.7))]:
    head.scale=scale
    head.keyframe_insert('scale',frame=frame)
stroke('TG_Intro_Person_Body',(0,.55),(0,-.2),(0,.4),(0,.4),cx,gold,vanish=True)
for name,a,b,c,d in [
    ('left_arm',(0,.4),(-.8,-.1),(0,.4),(-.95,.4)),
    ('right_arm',(0,.4),(.8,-.1),(0,.4),(.95,.4)),
    ('left_leg',(0,-.2),(-.55,-1.1),(0,.3),(-.85,-1.1)),
    ('right_leg',(0,-.2),(.55,-1.1),(0,.3),(.85,-1.1)),
]:
    stroke('TG_Intro_Person_'+name,a,b,c,d,cx,gold)

# Keep the invisible prefix geometry out of the unchanged video tail.
for obj in intro.objects:
    for frame,hidden in [(1,False),(26,False),(27,True),(168,True)]:
        obj.hide_render=hidden
        obj.keyframe_insert('hide_render',frame=frame)

for marker in scene.timeline_markers:
    marker.frame+=24
scene.timeline_markers.new('00 집·사람 → ㄷ·ㅊ',frame=1)
scene.timeline_markers.new('00 자음 형태 확인',frame=16)

max_error=0.
for frame in range(49,169):
    scene.frame_set(frame)
    for obj in objects:
        for channel in ['location','rotation_euler','scale']:
            expected=Vector(samples[frame-24]['objects'][obj.name][channel])
            max_error=max(max_error,(Vector(getattr(obj,channel))-expected).length)
assert max_error<.00001, max_error
scene.render.resolution_x,scene.render.resolution_y=960,540
scene.render.image_settings.file_format='PNG'
review=out/'storyboard'
review.mkdir(exist_ok=True)
for frame in [1,10,18,28,58,144]:
    scene.frame_set(frame)
    scene.render.filepath=str(review/f'frame-{frame:03d}.png')
    bpy.ops.render.render(write_still=True)
scene.frame_set(144)
scene.render.resolution_x,scene.render.resolution_y=1280,720
scene.render.filepath='//../outputs/thegachi-opening/v003/preview.png'
report={'ok':True,'frames':168,'fps':24,'seconds':7,'added_frames':24,
        'prefix':'Literal house/person morph to ㄷ/ㅊ, then dissolve into existing brand shapes.',
        'legacy_unchanged_range':{'old':[25,144],'new':[49,168]},
        'maximum_tail_transform_error':max_error,
        'review_frames':[1,10,18,28,58,144],'v002_preserved':True}
(out/'prefix-verification.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps(report,ensure_ascii=False))
