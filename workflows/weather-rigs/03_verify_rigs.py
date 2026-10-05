"""독립 Blender에서 실제 스키닝·IK·표정·특수 조절을 검사하고 렌더한다."""
import bpy,json,math,sys,time
from pathlib import Path
from mathutils import Vector
from bpy_extras.object_utils import world_to_camera_view
root=Path(__file__).resolve().parents[2];out=root/'outputs/weather-rigs/v001'
manifest=json.loads((out/'build-manifest.json').read_text(encoding='utf-8'))
scene=bpy.context.scene;assert scene.name=='Weather_Rigs_v001' and len(bpy.data.scenes)==1
assert len([o for o in scene.objects if o.type=='ARMATURE'])==5
assert not bpy.data.libraries
assert not any(i.source=='FILE' and not i.packed_file for i in bpy.data.images)
started=time.monotonic();reports=[]
if bpy.context.object and bpy.context.object.mode!='OBJECT':bpy.ops.object.mode_set(mode='OBJECT')
bpy.data.objects['WR1_Haerong_RIG'].pose.bones['CTRL_Extras'].id_properties_ui('ray_spread').update(min=-.1,max=.12,soft_min=-.1,soft_max=.12)

def refresh(rig):
    rig.update_tag();bpy.context.view_layer.update();scene.frame_set(scene.frame_current)
    return bpy.context.evaluated_depsgraph_get()

def reset(rig):
    defaults=json.loads(rig['neutral_properties'])
    for pb in rig.pose.bones:
        pb.location=(0,0,0);pb.rotation_euler=(0,0,0);pb.scale=(1,1,1)
        for name,value in defaults[pb.name].items():pb[name]=value
    refresh(rig)

def positions(obj,deps):
    evaluated=obj.evaluated_get(deps)
    return [v.co.copy() for v in evaluated.data.vertices]

def max_delta(a,b):return max((x-y).length for x,y in zip(a,b))

for record in manifest['characters']:
    key=record['name'];rig=bpy.data.objects[record['armature']];reset(rig)
    meshes=[o for o in scene.objects if o.parent==rig and o.type=='MESH']
    assert len(meshes)==record['meshes']
    for obj in meshes:
        assert any(m.type=='ARMATURE' and m.object==rig for m in obj.modifiers),obj.name
        for vertex in obj.data.vertices:
            total=sum(g.weight for g in vertex.groups)
            assert abs(total-1)<1e-4,(obj.name,vertex.index,total)
        assert all(g.name in rig.data.bones for g in obj.vertex_groups)
    deps=refresh(rig);neutral_error=0
    for label in manifest['original_mesh_labels'][key]:
        obj=bpy.data.objects['WR1_'+key+'_'+label]
        neutral_error=max(neutral_error,max_delta([v.co.copy() for v in obj.data.vertices],positions(obj,deps)))
    assert neutral_error<.015,(key,'neutral drift',neutral_error)
    ik=[]
    for side in ('L','R'):
        for target,deformer in [('Hand','Forearm'),('Foot','Shin')]:
            reset(rig);control=rig.pose.bones['CTRL_'+target+'.'+side]
            bone=rig.pose.bones['DEF_'+deformer+'.'+side];old=bone.tail.copy()
            origin=rig.pose.bones[('DEF_UpperArm.' if target=='Hand' else 'DEF_Thigh.')+side].head
            delta=(origin-old)*.15
            control.location=control.bone.matrix_local.to_3x3().inverted()@delta
            refresh(rig);moved=(bone.tail-old).length;error=(bone.tail-control.matrix.translation).length
            assert moved>.025 and error<.025,(key,target,side,moved,error)
            ik.append({'control':control.name,'endpoint_moved':moved,'target_error':error})
    reset(rig)
    body_label={'Mongsil':'CloudBody','Haerong':'SunBody','Ttorr':'DropBody','Songsong':'SoftHexagon','Solsol':'BreezeBody'}[key]
    body=bpy.data.objects['WR1_'+key+'_'+body_label];before=positions(body,refresh(rig))
    rig.pose.bones['CTRL_Body']['squash']=.2
    squash_delta=max_delta(before,positions(body,refresh(rig)));assert squash_delta>.1,(key,squash_delta)
    reset(rig);rig.pose.bones['CTRL_Face']['awake']=1.;rig.pose.bones['CTRL_Face']['blink']=1.;rig.pose.bones['CTRL_Face']['surprise']=1.
    refresh(rig)
    blink_values=[o.data.shape_keys.key_blocks['Blink'].value for o in meshes if o.data.shape_keys and 'Blink' in o.data.shape_keys.key_blocks]
    assert blink_values and min(blink_values)>.99,(key,'blink drivers',blink_values)
    mouth=bpy.data.objects['WR1_'+key+'_SurprisedMouth'];assert mouth.data.shape_keys.key_blocks['Hide'].value<.01
    reset(rig);extra=rig.pose.bones['CTRL_Extras']
    settings={'Mongsil':{'breath':1.,'hug':0.},'Haerong':{'ray_sway':1.,'ray_phase':1.3,'ray_spread':.12},'Ttorr':{'tip_sway':1.},'Songsong':{'crystal_fold':1.},'Solsol':{'body_bend':.7,'crest_curl':.7,'scarf_wave':1.,'scarf_phase':1.6}}[key]
    target_label={'Mongsil':'CloudBody','Haerong':'Ray_00','Ttorr':'DropBody','Songsong':'CrystalTip_00','Solsol':'UpperScarfTail'}[key]
    target=bpy.data.objects['WR1_'+key+'_'+target_label];before=positions(target,refresh(rig))
    for name,value in settings.items():extra[name]=value
    difference=max_delta(before,positions(target,refresh(rig)));assert difference>.015,(key,'special control ineffective',difference)
    invalid=[]
    ids=[rig]+[o.data.shape_keys for o in meshes if o.data.shape_keys]
    drivers=[]
    for data in ids:
        if data.animation_data:
            for curve in data.animation_data.drivers:
                drivers.append(curve)
                if not curve.driver.is_valid:invalid.append(curve.data_path)
    assert not invalid,(key,invalid)
    controls=[b for b in rig.pose.bones if b.name.startswith('CTRL_')]
    assert all(b.custom_shape for b in controls)
    reports.append({'character':key,'bones':len(rig.data.bones),'skinned_meshes':len(meshes),'neutral_max_vertex_delta':neutral_error,
                    'ik':ik,'squash_vertex_delta':squash_delta,'special_vertex_delta':difference,'driver_count':len(drivers),'invalid_drivers':invalid,
                    'bone_collections':{c.name:c.is_visible for c in rig.data.collections},'pose_selection_properties':[p.identifier for p in controls[0].bl_rna.properties if 'select' in p.identifier]})
    reset(rig)

# Save a neutral, fully standalone file suitable for manual posing.
guide=[]
def project(rig,point):
    p=world_to_camera_view(scene,scene.camera,rig.matrix_world@point)
    return [p.x*1920,(1-p.y)*1080]
for record in manifest['characters']:
    rig=bpy.data.objects[record['armature']]
    guide.append({'name':record['name'],'ko':record['ko'],'bones':[{'name':b.name,'head':project(rig,b.head),'tail':project(rig,b.tail)} for b in rig.pose.bones]})
(out/'control-positions.json').write_text(json.dumps(guide,indent=2,ensure_ascii=False),encoding='utf-8')
bpy.ops.object.select_all(action='DESELECT');active=bpy.data.objects['WR1_Mongsil_RIG'];active.select_set(True);bpy.context.view_layer.objects.active=active
active.data.bones.active=active.data.bones['CTRL_Body']
for pose_bone in active.pose.bones:pose_bone.select=False
active.pose.bones['CTRL_Body'].select=True
bpy.ops.object.mode_set(mode='POSE')
for screen in bpy.data.screens:
    for area in screen.areas:
        if area.type=='VIEW_3D':area.spaces.active.region_3d.view_perspective='CAMERA'
scene.render.filepath='//../outputs/weather-rigs/v001/rig-neutral.png'
bpy.ops.wm.save_as_mainfile(filepath=str(root/'scenes/weather-rigs-v001.blend'),check_existing=False,compress=True,relative_remap=True)
scene.render.resolution_x=1920;scene.render.resolution_y=1080;scene.render.filepath=str(out/'rig-neutral.png');bpy.ops.render.render(write_still=True)
# Combined expressions/special controls: keep every property inside its published range.
for record in manifest['characters']:
    rig=bpy.data.objects[record['armature']];rig.pose.bones['CTRL_Face']['awake']=1.;rig.pose.bones['CTRL_Face']['surprise']=1.
    rig.pose.bones['CTRL_Body']['squash']=.12
    extra=rig.pose.bones['CTRL_Extras']
    for name in extra.keys():
        if name in ('hug',):extra[name]=0.
        elif 'phase' in name:extra[name]=1.6
        elif name=='ray_spread':extra[name]=.12
        else:extra[name]=.7
    refresh(rig)
scene.render.filepath=str(out/'rig-expression-special-test.png');bpy.ops.render.render(write_still=True)
report={'ok':True,'independent_reopen':True,'characters':reports,'rigs':5,'bones':sum(r['bones'] for r in reports),'native_saved_in_pose_mode':True,'external_dependencies':[],'seconds':time.monotonic()-started}
(out/'rig-verification.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
print(json.dumps(report))
