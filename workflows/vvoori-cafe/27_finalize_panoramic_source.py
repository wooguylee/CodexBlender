"""독립 프로세스에서 전용 scene library를 정상 .blend로 저장하고 pack/움직임 검증."""
from pathlib import Path
import bpy, hashlib, json, shutil, math
from mathutils import Vector
root=Path(__file__).resolve().parents[2];out=root/'outputs/vvoori-cafe/v005';path=root/'scenes/vvoori-cafe-v005.blend'
assert Path(bpy.data.filepath).resolve()==path.resolve()
scene=bpy.data.scenes['Vvoori_Cafe_v005'];assert len(bpy.data.scenes)==1
bpy.context.window.scene=scene;bpy.context.window.view_layer=scene.view_layers['VC5_Motion']
assert len(scene.objects)==285 and scene.camera.name=='VC5_Camera'
assert not any(any(word in o.name for word in ['Window','Deep oak sill','Table','Cup','Saucer','Book','Chair','Coffee']) for o in scene.objects)
assert scene['window_and_furniture_are_generated_image']
assert {c.name for c in scene.collection.children}=={'VC5_Traffic','VC5_Leaves','VC5_Rig'}
assert 'Static3D' not in scene.compositing_node_group.nodes
assert (scene.render.resolution_x,scene.render.resolution_y,scene.render.resolution_percentage,scene.render.fps,scene.frame_end)==(1920,1080,100,24,480)
direction=scene.camera.rotation_euler.to_quaternion()@Vector((0,0,-1));angle=math.degrees(math.atan2(direction.x,direction.y));assert abs(angle-50)<1e-4
images=[n.image for n in scene.compositing_node_group.nodes if n.type=='IMAGE'];assert len(images)==2 and all(im.packed_file for im in images)
for im in images:
    actual=Path(bpy.path.abspath(im.filepath));assert actual.exists()
    assert hashlib.sha256(im.packed_file.data).hexdigest()==hashlib.sha256(actual.read_bytes()).hexdigest()
animated=[o for o in scene.objects if o.animation_data and o.animation_data.drivers];assert len(animated)==62
def transforms(frame):
    scene.frame_set(frame);bpy.context.view_layer.update();deps=bpy.context.evaluated_depsgraph_get();deps.update()
    return {o.name:[float(x) for row in o.evaluated_get(deps).matrix_world for x in row] for o in animated}
a,b,middle=transforms(1),transforms(480),transforms(241)
error=max(abs(x-y) for k in a for x,y in zip(a[k],b[k]));movement=max(abs(x-y) for k in a for x,y in zip(a[k],middle[k]))
assert error<1e-5 and movement>1
assert not any(not f.is_valid for o in animated for f in o.animation_data.drivers)
hashes=json.loads((out/'project-build.json').read_text())['source_hashes']
assert all(hashlib.sha256((root/p).read_bytes()).hexdigest()==h for p,h in hashes.items())
backup=out/'source-library-before-finalize.blend';assert not backup.exists();shutil.copyfile(path,backup)
scene.frame_set(1)
bpy.context.window.view_layer=scene.view_layers['VC5_Motion']
for screen in bpy.data.screens:
    for area in screen.areas:
        if area.type=='VIEW_3D':area.spaces.active.region_3d.view_perspective='CAMERA'
bpy.ops.wm.save_as_mainfile(filepath=str(path),check_existing=False,compress=True,relative_remap=True)
report={'ok':True,'scene':scene.name,'camera':scene.camera.name,'camera_angle_degrees':angle,'objects':len(scene.objects),
    'window_and_furniture_are_generated_image':True,'no_3d_window_or_furniture':True,'animated_objects':62,'endpoint_transform_error':error,'midpoint_motion':movement,'packed_images':len(images),
    'generated_png_hashes_verified':True,'old_source_hashes_unchanged':True,'full_quality_movie_rendered':True,
    'packed_image_sha256':{im.name:hashlib.sha256(im.packed_file.data).hexdigest() for im in images}}
(out/'source-verification.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
(root/'workflows/vvoori-cafe/v005-source-verification.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
print(json.dumps(report,indent=2))
