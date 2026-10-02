"""일반 .blend 기본 Scene을 다시 열어 pack 데이터만으로 실제 Full HD 렌더."""
from pathlib import Path
import bpy, json
root=Path(__file__).resolve().parents[2];out=root/'outputs/vvoori-cafe/v005'
scene=bpy.context.scene
assert scene.name=='Vvoori_Cafe_v005' and len(bpy.data.scenes)==1 and len(scene.objects)==285
assert scene.camera.name=='VC5_Camera' and bpy.context.view_layer.name=='VC5_Motion'
images=[n.image for n in scene.compositing_node_group.nodes if n.type=='IMAGE'];assert len(images)==2 and all(im.packed_file for im in images)
assert scene.render.resolution_percentage==100 and scene.render.fps==24
prefs=bpy.context.preferences.addons['cycles'].preferences;prefs.compute_device_type='OPTIX';prefs.get_devices()
for d in prefs.devices:d.use=d.type=='OPTIX'
scene.cycles.device='GPU';scene.frame_set(2);scene.frame_set(1)
scene.render.filepath=str(out/'native-reopen-preview.png');bpy.ops.render.render(write_still=True)
report={'ok':True,'native_default_scene':scene.name,'packed_images':2,'rendered_after_reopen':True,'source_file_modified':False}
(out/'native-reopen-verification.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
print(json.dumps(report,indent=2))
