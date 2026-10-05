"""출력 확인 후 브리찌 화면을 조작 가능한 중립 리깅 Scene으로 정리한다."""
import json
out=PROJECT_ROOT/'outputs/weather-rigs/v001'
verification=json.loads((out/'output-verification.json').read_text(encoding='utf-8'));assert verification['ok']
if bpy.context.object and bpy.context.object.mode!='OBJECT':bpy.ops.object.mode_set(mode='OBJECT')
scene=bpy.data.scenes['Weather_Rigs_v001'];bpy.context.window.scene=scene
rigs=[o for o in scene.objects if o.type=='ARMATURE'];assert len(rigs)==5
for rig in rigs:
    assert not rig.animation_data or not rig.animation_data.action
    defaults=json.loads(rig['neutral_properties'])
    for bone in rig.pose.bones:
        if bone.name.startswith('CTRL_'):bone.location=(0,0,0);bone.rotation_euler=(0,0,0)
        for name,value in defaults[bone.name].items():bone[name]=value
        bone.select=False
    rig.update_tag()
bpy.data.objects['WR1_Haerong_RIG'].pose.bones['CTRL_Extras'].id_properties_ui('ray_spread').update(min=-.1,max=.12,soft_min=-.1,soft_max=.12)
scene.frame_set(1);bpy.context.view_layer.update()
bpy.ops.object.select_all(action='DESELECT')
for rig in rigs:rig.select_set(True)
active=bpy.data.objects['WR1_Mongsil_RIG'];bpy.context.view_layer.objects.active=active
active.data.bones.active=active.data.bones['CTRL_Body'];active.pose.bones['CTRL_Body'].select=True
bpy.ops.object.mode_set(mode='POSE')
for area in bpy.context.screen.areas:
    if area.type=='VIEW_3D':
        area.spaces.active.region_3d.view_perspective='CAMERA'
        area.spaces.active.overlay.show_overlays=True
        area.spaces.active.shading.type='SOLID';area.spaces.active.shading.color_type='MATERIAL'
report={'ok':True,'scene':scene.name,'frame':1,'mode':'POSE','selected_rigs':5,'active_control':'WR1_Mongsil_RIG / CTRL_Body',
 'visual_review':['Neutral and combined expression/special renders directly inspected.','Delivered MP4 contact frames directly inspected for hands, face, body and special controls.'],
 'preservation':verification['unchanged_file_count'],'movie':'outputs/weather-rigs/v001/weather-rig-demo-16s.mp4',
 'source':'scenes/weather-rigs-v001.blend','demo_source':'scenes/weather-rig-demo-v001.blend'}
(out/'final-delivery.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
print(json.dumps(report))
