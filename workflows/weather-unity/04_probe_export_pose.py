"""FBX 내보내기 시 변경된 rest pose와 평가된 pose의 차이를 조사한다."""
import json
before=bpy.context.scene;records=[]
for key in ['Mongsil','Haerong','Ttorr','Songsong','Solsol']:
    scene=bpy.data.scenes['WFUnity_'+key];bpy.context.window.scene=scene;rig=next(o for o in scene.objects if o.type=='ARMATURE')
    scene.frame_set(1);rig.update_tag();bpy.context.view_layer.update()
    pb=rig.pose.bones['CTRL_Root'];records.append({'name':key,'rest_head':list(pb.bone.head_local),'pose_head':list(pb.head),'location':list(pb.location),'matrix_translation':list(pb.matrix.translation)})
bpy.context.window.scene=before
(PROJECT_ROOT/'outputs/weather-unity/v001/rest-pose-probe.json').write_text(json.dumps(records,indent=2),encoding='utf-8')
print(json.dumps(records))
