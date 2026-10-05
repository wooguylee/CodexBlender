"""브리찌에서 독립 리깅 원본을 복제하여 실제 컨트롤 키프레임 시연을 만든다."""
import hashlib,json,math
from mathutils import Vector

out=PROJECT_ROOT/'outputs/weather-rigs/v001'
source=PROJECT_ROOT/'scenes/weather-rigs-v001.blend'
target=PROJECT_ROOT/'scenes/weather-rig-demo-v001.blend'
assert not target.exists() and 'Weather_Rig_Demo_v001' not in bpy.data.scenes
source_hash=hashlib.sha256(source.read_bytes()).hexdigest()
if bpy.context.object and bpy.context.object.mode!='OBJECT':bpy.ops.object.mode_set(mode='OBJECT')
with bpy.data.libraries.load(str(source),link=False) as (available,loaded):
    assert available.scenes==['Weather_Rigs_v001'];loaded.scenes=available.scenes
scene=loaded.scenes[0];scene.name='Weather_Rig_Demo_v001';bpy.context.window.scene=scene
names={'몽실':'Mongsil','해롱':'Haerong','또르':'Ttorr','송송':'Songsong','솔솔':'Solsol'}
rigs={names[o['character_ko']]:o for o in scene.objects if o.type=='ARMATURE'}
assert len(rigs)==5
for obj in scene.objects:
    if obj.type=='MESH' and obj.data.shape_keys and obj.data.shape_keys.animation_data:
        for curve in obj.data.shape_keys.animation_data.drivers:
            for var in curve.driver.variables:
                assert var.targets[0].id in rigs.values(),(obj.name,'driver remap')
scene.frame_start=1;scene.frame_end=384;scene.render.fps=24
scene['purpose']='16-second demonstration of the actual native armature controls. Silent.'
scene['neutral_source']='//weather-rigs-v001.blend'
defaults={key:json.loads(rig['neutral_properties']) for key,rig in rigs.items()}
def smooth(a,b,t):
    v=max(0,min(1,(t-a)/(b-a)));return v*v*(3-2*v)
def window(a,b,t,ramp=.4):return smooth(a,a+ramp,t)*(1-smooth(b-ramp,b,t))
def offset(rig,name,delta):
    control=rig.pose.bones[name];control.location=control.bone.matrix_local.to_3x3().inverted()@Vector(delta)
for frame in list(range(1,385,2))+[384]:
    scene.frame_set(frame);t=(frame-1)/24
    for index,(key,rig) in enumerate(rigs.items()):
        for bone,properties in defaults[key].items():
            pb=rig.pose.bones[bone]
            if bone.startswith('CTRL_'):
                pb.location=(0,0,0);pb.rotation_euler=(0,0,0)
            for name,value in properties.items():pb[name]=value
        body=rig.pose.bones['CTRL_Body'];face=rig.pose.bones['CTRL_Face'];extra=rig.pose.bones['CTRL_Extras']
        # Move real IK targets toward the limb root so the short limbs retain reach.
        limb=window(2,5,t)
        for side in ('L','R'):
            sign=1 if side=='L' else -1
            hand=rig.pose.bones['CTRL_Hand.'+side]
            delta=(rig.data.bones['DEF_UpperArm.'+side].head_local-hand.bone.head_local)*(.12*limb)
            delta.x+=.035*limb*math.sin(t*7+index+sign)
            offset(rig,hand.name,delta)
            delta=(rig.data.bones['DEF_Thigh.'+side].head_local-rig.data.bones['CTRL_Foot.'+side].head_local)*(.10*limb*(.5+.5*math.sin(t*5+sign*1.2)))
            offset(rig,'CTRL_Foot.'+side,delta)
        awake=window(5,15.7,t);face['awake']=awake
        face['smile']=window(5.3,6.5,t,.25)
        face['blink']=math.exp(-((t-6.25)/.13)**2)+math.exp(-((t-7.05)/.13)**2)
        face['surprise']=window(6.65,8,t,.25)
        body['squash']=.15*window(8,11.8,t)*math.sin((t-8)*math.tau*.65)
        weather=window(8,15.7,t)
        if key=='Mongsil':
            extra['breath']=window(8,12,t)*(.5+.5*math.sin(t*3))
            extra['hug']=1-.85*window(12,14.8,t)
            rig.pose.bones['CTRL_Cushion'].rotation_euler.z=.12*window(12,15,t)*math.sin(t*3)
        elif key=='Haerong':
            extra['ray_sway']=weather;extra['ray_phase']=t*3.5
            extra['ray_spread']=.10*weather*math.sin((t-8)*3)
        elif key=='Ttorr':extra['tip_sway']=.85*weather*math.sin(t*3.3)
        elif key=='Songsong':extra['crystal_fold']=weather*(.45+.4*math.sin(t*2.5))
        elif key=='Solsol':
            extra['body_bend']=.65*window(12,15.7,t)*math.sin(t*2.1)
            extra['crest_curl']=.7*window(12,15.7,t)*math.sin(t*2.1+.5)
            extra['scarf_wave']=weather;extra['scarf_phase']=t*4
        for bone,properties in defaults[key].items():
            pb=rig.pose.bones[bone]
            if bone.startswith('CTRL_'):
                pb.keyframe_insert('location',frame=frame,group=bone)
                pb.keyframe_insert('rotation_euler',frame=frame,group=bone)
            for name in properties:
                pb.keyframe_insert('['+json.dumps(name)+']',frame=frame,group=bone)
    if frame%49==0:print(json.dumps({'baked_frame':frame}))
curve_count=0
for rig in rigs.values():
    action=rig.animation_data.action
    for layer in action.layers:
        for strip in layer.strips:
            for bag in strip.channelbags:
                for curve in bag.fcurves:
                    curve_count+=1
                    for point in curve.keyframe_points:point.interpolation='LINEAR'
scene.frame_set(1);bpy.context.view_layer.update()
scene.render.filepath='//../outputs/weather-rigs/v001/frames/frame_'
bpy.ops.object.select_all(action='DESELECT');active=rigs['Mongsil'];active.select_set(True);bpy.context.view_layer.objects.active=active
bpy.data.libraries.write(str(target),{scene},path_remap='RELATIVE',fake_user=True,compress=True)
assert hashlib.sha256(source.read_bytes()).hexdigest()==source_hash
report={'ok':True,'source':target.relative_to(PROJECT_ROOT).as_posix(),'scene':scene.name,'neutral_source_sha256':source_hash,
        'frames':384,'fps':24,'duration':16,'audio':'none','animation_curves':curve_count,
        'rigs':{key:rig.name for key,rig in rigs.items()},
        'chapters':[[0,2,'기본 자세'],[2,5,'손발 IK'],[5,8,'눈·입 표정'],[8,12,'몸과 날씨 특징'],[12,16,'쿠션·스카프·바람']]}
(out/'demo-manifest.json').write_text(json.dumps(report,indent=2,ensure_ascii=False),encoding='utf-8')
print(json.dumps(report,ensure_ascii=False))
