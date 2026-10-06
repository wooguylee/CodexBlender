import bpy,json
from pathlib import Path
root=Path(__file__).resolve().parents[2]
bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.fbx(filepath=str(root/'exports/weather-fairies/v001/unity/Assets/WeatherFairies/Models/Mongsil.fbx'))
scene=bpy.context.scene;scene.frame_set(1);bpy.context.view_layer.update();deps=bpy.context.evaluated_depsgraph_get()
rig=next(o for o in scene.objects if o.type=='ARMATURE');pb=rig.pose.bones['CTRL_Root']
points=[o.matrix_world@v.co for o in scene.objects if o.type=='MESH' for v in o.evaluated_get(deps).data.vertices]
report={'frame_range':[scene.frame_start,scene.frame_end],'root_location':list(rig.location),'root_scale':list(rig.scale),'root_rotation':list(rig.rotation_euler),'bone_rest':list(pb.bone.head_local),'bone_pose':list(pb.head),'minimum':[min(v[i] for v in points) for i in range(3)]}
(root/'outputs/weather-unity/v001/fbx-roundtrip-probe.json').write_text(json.dumps(report,indent=2),encoding='utf-8');print(json.dumps(report))
