"""새 Blender 프로세스에서 납품용 원본을 열고 pack/카메라/루프를 읽기 전용 검증."""
import bpy,json
from pathlib import Path
root=Path(__file__).resolve().parents[2]
scene=bpy.context.scene;assert scene.name=='Autumn_Cafe_v001'
if bpy.context.window:bpy.context.window.view_layer=scene.view_layers['MovingLeavesAndTraffic']
assert scene.camera and scene.camera.name=='AC_Camera'
assert scene.frame_start==1 and scene.frame_end==480 and scene.render.fps==24
assert scene.render.resolution_x==1920 and scene.render.resolution_y==1080
animated=[o for o in scene.objects if o.animation_data and o.animation_data.drivers]
def values(frame):
    scene.frame_set(frame);bpy.context.view_layer.update();deps=bpy.context.evaluated_depsgraph_get();deps.update()
    return {o.name:[float(v) for r in o.evaluated_get(deps).matrix_world for v in r] for o in animated}
a,b=values(1),values(480);err=max(abs(x-y) for k in a for x,y in zip(a[k],b[k]));assert err<1e-5
middle=values(241);motion=max(abs(x-y) for k in a for x,y in zip(a[k],middle[k]));assert motion>1
invalid=[o.name for o in animated if any(not f.is_valid for f in o.animation_data.drivers)];assert not invalid,invalid
images=[n.image for n in scene.compositing_node_group.nodes if n.type=='IMAGE'];assert images and all(im.packed_file for im in images)
assert not scene.camera.animation_data
assert not any(o.animation_data or o.data.animation_data for o in scene.objects if o.type=='LIGHT')
report={'ok':True,'scene':scene.name,'scene_count':len(bpy.data.scenes),'object_count':len(scene.objects),'camera':scene.camera.name,'animated_objects':len(animated),'driver_errors':invalid,'endpoint_transform_error':err,'midpoint_motion_confirmed':motion,'packed_backgrounds':[im.name for im in images],'camera_and_lights_static':True}
(root/'outputs/autumn-cafe/v001/saved-source-verification.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
print(json.dumps(report,indent=2))
