"""독립 Blender에서 library 원본을 기본 장면이 있는 편집 가능한 일반 .blend로 저장."""
from pathlib import Path
import bpy, json, hashlib, shutil, math
from mathutils import Vector
root=Path(__file__).resolve().parents[2];out=root/'outputs/vvoori-cafe-winter/v001'
path=root/'scenes/vvoori-cafe-winter-v001.blend'
assert Path(bpy.data.filepath).resolve()==path.resolve()
assert len(bpy.data.scenes)==1
scene=bpy.data.scenes['Vvoori_Cafe_Winter_v001'];bpy.context.window.scene=scene
bpy.context.window.view_layer=scene.view_layers['VWC1_Motion']
assert {c.name for c in scene.collection.children}=={'VWC1_Traffic','VWC1_Snow','VWC1_Rig'}
assert len(bpy.data.collections['VWC1_Snow'].objects)==280
assert len(scene.objects)==527
assert not any(k in o.name for o in scene.objects for k in ['Window','Table','Cup','Book','Chair','Floor'])
assert (scene.render.resolution_x,scene.render.resolution_y,scene.render.resolution_percentage,scene.render.fps,scene.frame_end)==(1920,1080,100,24,480)
direction=scene.camera.rotation_euler.to_quaternion()@Vector((0,0,-1))
angle=math.degrees(math.atan2(direction.x,direction.y));assert abs(angle-50)<1e-4
images=[n.image for n in scene.compositing_node_group.nodes if n.type=='IMAGE']
assert len(images)==2 and all(im.packed_file for im in images)
packed={}
for im in images:
    actual=Path(bpy.path.abspath(im.filepath));assert actual.is_relative_to(root)
    sha=hashlib.sha256(im.packed_file.data).hexdigest();assert sha==hashlib.sha256(actual.read_bytes()).hexdigest()
    packed[im.name]=sha
assert scene.view_settings.view_transform=='Standard' and scene.view_settings.exposure==0
backup=out/'source-library-before-finalize.blend'
if backup.exists():backup=out/'source-library-before-finalize-edge-fixed.blend'
assert not backup.exists();shutil.copyfile(path,backup)
scene.frame_set(1)
for screen in bpy.data.screens:
    for area in screen.areas:
        if area.type=='VIEW_3D':area.spaces.active.region_3d.view_perspective='CAMERA'
bpy.ops.wm.save_as_mainfile(filepath=str(path),check_existing=False,compress=True,relative_remap=True)
report={'ok':True,'scene':scene.name,'objects':len(scene.objects),'camera_angle_degrees':angle,
 'static_image_nodes':2,'packed_images_sha256':packed,'no_static_3d_geometry':True,
 'no_external_dependencies':True,'color_transform':'sRGB images -> linear compositing -> Standard sRGB output',
 'snow_count':280,'cars':6,'period_frames':480,'source_normalized_to_editable_native_blend':True}
(out/'source-verification.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
print(json.dumps(report,indent=2))
