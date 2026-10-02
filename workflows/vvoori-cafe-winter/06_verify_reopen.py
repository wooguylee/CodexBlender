"""다시 분리한 Blender 프로세스에서 완성 .blend의 packed 자산과 실제 렌더를 검사."""
from pathlib import Path
import bpy, json, math
root=Path(__file__).resolve().parents[2];out=root/'outputs/vvoori-cafe-winter/v001'
scene=bpy.context.scene
assert scene.name=='Vvoori_Cafe_Winter_v001' and len(bpy.data.scenes)==1
assert bpy.context.view_layer.name=='VWC1_Motion' and len(scene.objects)==527
images=[n.image for n in scene.compositing_node_group.nodes if n.type=='IMAGE']
assert len(images)==2 and all(im.packed_file for im in images)
for im in images:im.filepath='//__packed_only_verification__/'+im.name+'.png'
prefs=bpy.context.preferences.addons['cycles'].preferences;prefs.compute_device_type='OPTIX';prefs.get_devices()
for device in prefs.devices:device.use=device.type=='OPTIX'
scene.cycles.device='GPU'
animated=[o for o in scene.objects if o.animation_data and o.animation_data.drivers]
def state(frame):
    scene.frame_set(frame);bpy.context.view_layer.update();deps=bpy.context.evaluated_depsgraph_get();deps.update()
    return {o.name:[float(v) for row in o.evaluated_get(deps).matrix_world for v in row] for o in animated}
a,b=state(1),state(481)
error=max(abs(x-y) for n in a for x,y in zip(a[n],b[n]));assert error<1e-4
state(1)
scene.render.filepath=str(out/'native-reopen-preview.png');bpy.ops.render.render(write_still=True)
report={'ok':True,'default_scene':scene.name,'packed_images':2,'external_paths_deliberately_unavailable':True,
 'rendered_after_independent_reopen':True,'width':scene.render.resolution_x,'height':scene.render.resolution_y,
 'animated_objects':len(animated),'frame_1_481_matrix_error':error,'original_file_not_modified':True}
(out/'native-reopen-verification.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
print(json.dumps(report,indent=2))
