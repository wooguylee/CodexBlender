"""사용자 요청: 오른쪽에서 집 앞까지 걸어와 머리 위로 손을 흔든 뒤 ㄷ/ㅊ 추출.

5초 도입부를 만든다. 원래 v002 6초 영상은 별도 단계에서 스트림 복사로 온전히 연결한다.
v004 기준 그림은 디스크에 보존. 기존 본편의 객체/키프레임/영상은 수정하지 않는다.
"""
import json
import math
from mathutils import Vector, Matrix

scene=bpy.context.scene
assert scene.name=='Thegachi_HousePerson_v004'
assert 'HP_Walk_Root' not in bpy.data.objects
scene.name='Thegachi_Opening_v005'
scene['output_version']='v005'
scene['poster_frame']=72
scene['symbol_frame']=106
scene['review_frames']=[1,25,51,72,96,108]
scene['opening_duration_seconds']=5
scene['stage']='Walk, overhead wave, brand-symbol extraction. Append unchanged v002 six-second master.'
scene.frame_start,scene.frame_end,scene.render.fps=1,120,24
collection=bpy.data.collections['Thegachi_HousePerson_v004']
out=PROJECT_ROOT/'outputs/thegachi-opening/v005'
out.mkdir(parents=True,exist_ok=True)
origin=Vector((1.20,-2.52,1.60))


def own(obj):
    collection.objects.link(obj)
    return obj


def empty(name,world_location):
    obj=own(bpy.data.objects.new(name,None))
    obj.location=world_location
    obj.empty_display_type='PLAIN_AXES'
    bpy.context.view_layer.update()
    return obj


def parent(obj,par):
    world=obj.matrix_world.copy()
    obj.parent=par
    obj.matrix_world=world
    bpy.context.view_layer.update()


def ease(t):
    t=max(0.,min(1.,t))
    return t*t*(3-2*t)


def lerp(a,b,t):
    return Vector(a).lerp(Vector(b),t)


person=[o for o in scene.objects if o.name.startswith('HP_Person_')]
root=empty('HP_Walk_Root',origin)
for obj in person:
    parent(obj,root)

hips={}
shoulders={}
elbows={}
for side,sign in [('L',-1),('R',1)]:
    hip=empty('HP_Walk_Hip_'+side,origin+Vector((sign*.24*.66,1.24,0)))
    parent(hip,root)
    hips[side]=hip
    for suffix in ['trouser_','shoe_']:
        parent(scene.objects['HP_Person_'+suffix+side],hip)
    shoulder=empty('HP_Wave_Shoulder_'+side,origin+Vector((sign*.37,2.04,0)))
    parent(shoulder,root)
    shoulders[side]=shoulder
    elbow=empty('HP_Wave_Elbow_'+side,origin+Vector((sign*.58,1.70,.03)))
    parent(elbow,shoulder)
    elbows[side]=elbow
    parent(scene.objects['HP_Person_sleeve_upper_'+side],shoulder)
    parent(scene.objects['HP_Person_elbow_'+side],shoulder)
    parent(scene.objects['HP_Person_sleeve_lower_'+side],elbow)
    parent(scene.objects['HP_Person_hand_'+side],elbow)

# A small step at the edge lets the person walk onto the existing miniature base.
bpy.ops.mesh.primitive_cube_add(size=1,location=(4.42,-2.82,1.60))
step=bpy.context.object
step.name='HP_Walk_EntryStep'
for col in list(step.users_collection):
    col.objects.unlink(step)
collection.objects.link(step)
step.dimensions=(.68,.24,1.12)
bpy.ops.object.transform_apply(location=False,rotation=False,scale=True)
step.data.materials.append(bpy.data.materials['HP_Limestone'])
bev=step.modifiers.new('Soft_step_edges','BEVEL')
bev.width=.06
bev.segments=3

# Walking and wave use a lightweight articulated rig, preserving the approved model.
foot_clearances=[]
wave_heights=[]
for f in range(1,121):
    t=ease((f-1)/47)
    x=7.2+(1.2-7.2)*t
    distance=7.2-x
    phase=2*math.pi*distance/2.15
    stride=.52*(1-ease((f-42)/9))
    turn=ease((f-42)/12)
    support=-2.94+.42*ease((4.85-x)/1.05)
    root.location=(x,support,1.60)
    root.rotation_euler=(0,math.radians(-78)*(1-turn),0)
    root.scale=(1,1,1)
    for side,sign in [('L',-1),('R',1)]:
        hips[side].rotation_euler=(sign*math.sin(phase)*stride,0,0)
        shoulders[side].rotation_euler=(-sign*math.sin(phase)*stride*.55,0,0)
        shoulders[side].scale=(1,1,1)
        elbows[side].rotation_euler=(0,0,0)
    raise_amount=ease((f-54)/10)*(1-ease((f-82)/8))
    if f>=54:
        shoulders['R'].rotation_euler=(0,0,math.radians(148.3)*raise_amount)
        shoulders['R'].scale=(1+.18*raise_amount,)*3
        oscillation=math.sin((f-64)*2*math.pi/10)*24 if 64<=f<=84 else 0
        elbows['R'].rotation_euler=(0,0,math.radians(14.5+oscillation)*raise_amount)
    bpy.context.view_layer.update()
    shoes=[scene.objects['HP_Person_shoe_'+s] for s in ['L','R']]
    min_foot=min((shoe.matrix_world@Vector(v)).y for shoe in shoes for v in shoe.bound_box)
    root.location.y+=support-min_foot+.005
    bpy.context.view_layer.update()
    if f<=54:
        foot_clearances.append(min((shoe.matrix_world@Vector(v)).y for shoe in shoes for v in shoe.bound_box)-support)
    if 64<=f<=80:
        hand=scene.objects['HP_Person_hand_R']
        head=scene.objects['HP_Person_hair']
        hand_top=max((hand.matrix_world@Vector(v)).y for v in hand.bound_box)
        head_top=max((head.matrix_world@Vector(v)).y for v in head.bound_box)
        wave_heights.append({'frame':f,'hand_above_head':hand_top-head_top})
    for obj in [root,*hips.values(),*shoulders.values(),*elbows.values()]:
        for channel in ['location','rotation_euler','scale']:
            obj.keyframe_insert(channel,frame=f)

assert min(foot_clearances)>-.001
assert max(v['hand_above_head'] for v in wave_heights)>.12
scene.frame_set(54)
assert abs(root.location.x-1.2)<.001


def fade_material(source,name,keys):
    mat=source.copy()
    mat.name=name
    mat.animation_data_clear()
    nodes,links=mat.node_tree.nodes,mat.node_tree.links
    output=nodes.get('Material Output')
    surface=output.inputs['Surface'].links[0].from_socket
    mix=nodes.new('ShaderNodeMixShader')
    transparent=nodes.new('ShaderNodeBsdfTransparent')
    links.new(transparent.outputs[0],mix.inputs[1])
    links.new(surface,mix.inputs[2])
    links.new(mix.outputs[0],output.inputs['Surface'])
    if hasattr(mat,'surface_render_method'):
        mat.surface_render_method='DITHERED'
    for frame,value in keys:
        mix.inputs[0].default_value=value
        mix.inputs[0].keyframe_insert('default_value',frame=frame)
    return mat


house=scene.objects['HP_BlueHouse_LogoContour']
person_set=set(person)
fading=[o for o in scene.objects if o.type in ['MESH','CURVE'] and o!=house]
material_cache={}
for obj in fading:
    family='Person' if obj in person_set else 'Architecture'
    keys=[(1,1),(88,1),(100,0),(120,0)] if family=='Person' else [(1,1),(88,1),(108,0),(120,0)]
    # Copy geometry before replacing materials so other scenes and saved references stay independent.
    obj.data=obj.data.copy()
    for i,source in enumerate(list(obj.data.materials)):
        key=(source.name,family)
        if key not in material_cache:
            material_cache[key]=fade_material(source,'HP_v005_'+family+'_'+source.name,keys)
        obj.data.materials[i]=material_cache[key]
    for f,hidden in [(1,False),(108,False),(109,True),(120,True)]:
        obj.hide_render=hidden
        obj.keyframe_insert('hide_render',frame=f)

# Exact original ㅊ symbol emerges in the person's position.
glyph=own(bpy.data.objects.new('HP_Extracted_Person_ch',bpy.data.objects['TG_person_ch'].data.copy()))
glyph.data.animation_data_clear()
glyph.data.materials.clear()
glyph.data.materials.append(fade_material(bpy.data.materials['TG_Yellow_Person'],'HP_Extracted_Yellow',[(1,0),(87,0),(98,1),(120,1)]))
glyph.data.extrude=.13
house.data=house.data.copy()
house_target=Vector(bpy.data.objects['TG_house_d']['icon_location'])
person_target=Vector(bpy.data.objects['TG_person_ch']['icon_location'])
house_scale=float(bpy.data.objects['TG_house_d']['icon_scale'])
person_scale=float(bpy.data.objects['TG_person_ch']['icon_scale'])
house_initial=house.location.copy()
cam=scene.camera
cam_initial=cam.location.copy()
cam_rot_initial=cam.rotation_euler.copy()

# The navy background is the same material/placement as the six-second master.
background=own(bpy.data.objects.new('HP_Extract_Background',bpy.data.objects['TG_Backdrop'].data.copy()))
background.location=(0,0,-4)
background.data.materials.clear()
background.data.materials.append(fade_material(bpy.data.materials['TG_Backdrop'],'HP_Extract_Background_Mat',[(1,0),(88,0),(108,1),(120,1)]))
light_pairs=[('HP_Key','TG_Key'),('HP_Fill','TG_Fill'),('HP_Rim','TG_Top')]
light_start={n:(scene.objects[n].location.copy(),scene.objects[n].data.energy,scene.objects[n].data.size,tuple(scene.objects[n].data.color)) for n,_ in light_pairs}
world=scene.world.node_tree.nodes['Background']
world_start=list(world.inputs[0].default_value)
world_strength=world.inputs[1].default_value
for f in range(1,121):
    pull=ease((f-88)/20)
    finish=ease((f-110)/10)
    # Forward motion explicitly pulls the blue architectural contour out of the house.
    house.location=lerp(house_initial,house_target,pull)
    house.location.z+=math.sin(math.pi*pull)*2.0
    house.scale=(2.25+(house_scale-2.25)*pull,)*3
    house.data.extrude=.43+(.13-.43)*pull
    house.data.keyframe_insert('extrude',frame=f)
    glyph.location=lerp((1.20,-1.0,1.92),person_target,pull)
    glyph.location.z+=math.sin(math.pi*pull)*.75
    glyph.scale=(1.28+(person_scale-1.28)*pull,)*3
    if finish>0:
        for obj,position in [(house,house_target),(glyph,person_target)]:
            obj.scale=tuple(s*(1-finish)+.0001*finish for s in obj.scale)
            obj.location=lerp(obj.location,(position.x,position.y,0),finish)
    for obj in [house,glyph]:
        obj.keyframe_insert('location',frame=f)
        obj.keyframe_insert('scale',frame=f)
    cam.location=lerp(cam_initial,(0,0,22),pull)
    target=lerp((-.25,0,.15),(0,0,0),pull)
    direction=(target-cam.location).normalized()
    right=direction.cross(Vector((0,1,0))).normalized()
    up=right.cross(direction).normalized()
    cam.rotation_euler=Matrix((right,up,-direction)).transposed().to_euler()
    cam.data.ortho_scale=12.8+(11.5-12.8)*pull
    cam.keyframe_insert('location',frame=f)
    cam.keyframe_insert('rotation_euler',frame=f)
    cam.data.keyframe_insert('ortho_scale',frame=f)
    for local,legacy in light_pairs:
        lamp=scene.objects[local]
        reference=bpy.data.objects[legacy]
        start=light_start[local]
        lamp.location=lerp(start[0],reference.location,pull)
        lamp.data.energy=start[1]+(reference.data.energy-start[1])*pull
        lamp.data.size=start[2]+(reference.data.size-start[2])*pull
        lamp.data.color=lerp(start[3],reference.data.color,pull)
        look=lerp((-.3,0,0),(0,0,0),pull)
        lamp.rotation_euler=(look-lamp.location).to_track_quat('-Z','Y').to_euler()
        lamp.keyframe_insert('location',frame=f)
        lamp.keyframe_insert('rotation_euler',frame=f)
        for channel in ['energy','size','color']:
            lamp.data.keyframe_insert(channel,frame=f)
    world.inputs[0].default_value=tuple(a+(b-a)*pull for a,b in zip(world_start,(.32,.4,.55,1)))
    world.inputs[1].default_value=world_strength+(.22-world_strength)*pull
    world.inputs[0].keyframe_insert('default_value',frame=f)
    world.inputs[1].keyframe_insert('default_value',frame=f)
    scene.view_settings.exposure=.15+(-.35-.15)*pull
    scene.view_settings.keyframe_insert('exposure',frame=f)

for f,label in [(1,'01 오른쪽에서 걸어오기'),(51,'02 집 앞 도착'),(64,'03 머리 위 인사'),(88,'04 ㄷ과 ㅊ 추출'),(110,'05 심벌'),(120,'06 원본 영상 연결')]:
    scene.timeline_markers.new(label,frame=f)
scene.render.engine='BLENDER_EEVEE'
scene.render.resolution_x,scene.render.resolution_y=960,540
scene.render.image_settings.file_format='PNG'
review=out/'storyboard'
review.mkdir(exist_ok=True)
for f in [1,25,51,64,72,80,96,108,117]:
    scene.frame_set(f)
    scene.render.filepath=str(review/f'frame-{f:03d}.png')
    bpy.ops.render.render(write_still=True)
scene.frame_set(72)
scene.render.resolution_x,scene.render.resolution_y=1280,720
scene.render.filepath='//../outputs/thegachi-opening/v005/preview.png'
report={'ok':True,'intro_frames':120,'intro_seconds':5,'legacy_seconds':6,'total_seconds':11,
        'arrival_x':1.2,'minimum_walking_foot_clearance':min(foot_clearances),
        'overhead_wave':wave_heights,'maximum_hand_above_head':max(v['hand_above_head'] for v in wave_heights),
        'reference_scene_preserved_on_disk':'scenes/thegachi-house-person-v004-final.blend',
        'review_frames':[1,25,51,64,72,80,96,108,117]}
(out/'motion-verification.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps(report,ensure_ascii=False))
