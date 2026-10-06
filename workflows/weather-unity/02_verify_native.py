"""각 개별 파일을 독립 재개방해 정규화/검증하고 캐릭터 미리보기를 렌더한다."""
import bpy,hashlib,json
from pathlib import Path
from mathutils import Vector
root=Path(__file__).resolve().parents[2];out=root/'outputs/weather-unity/v001'
manifest=json.loads((out/'export-manifest.json').read_text(encoding='utf-8'));reports=[]
for record in manifest['characters']:
    path=root/record['blender'];bpy.ops.wm.open_mainfile(filepath=str(path),use_scripts=False)
    scene=bpy.context.scene;rigs=[o for o in scene.objects if o.type=='ARMATURE'];assert len(rigs)==1 and len(bpy.data.scenes)==1
    rig=rigs[0];meshes=[o for o in scene.objects if o.type=='MESH'];assert len(meshes)==record['meshes']
    assert all(o.parent==rig for o in meshes) and not bpy.data.libraries
    assert not any(i.source=='FILE' and not i.packed_file for i in bpy.data.images)
    scene.frame_set(1);bpy.context.view_layer.update();drivers=[]
    for data in [rig]+[o.data.shape_keys for o in meshes if o.data.shape_keys]:
        if data.animation_data:drivers.extend(data.animation_data.drivers)
    assert drivers and all(c.driver.is_valid and c.driver.is_simple_expression for c in drivers)
    assert len(rig.data.bones)==record['bones']
    if bpy.context.object and bpy.context.object.mode!='OBJECT':bpy.ops.object.mode_set(mode='OBJECT')
    bpy.ops.object.select_all(action='DESELECT');rig.select_set(True);bpy.context.view_layer.objects.active=rig
    for pb in rig.pose.bones:pb.select=False
    rig.pose.bones['CTRL_Body'].select=True;rig.data.bones.active=rig.data.bones['CTRL_Body'];bpy.ops.object.mode_set(mode='POSE')
    for screen in bpy.data.screens:
        for area in screen.areas:
            if area.type=='VIEW_3D':
                region=area.spaces.active.region_3d;region.view_location=Vector((0,0,1.6));region.view_distance=7
                region.view_rotation=Vector((0,1,-.15)).to_track_quat('-Z','Y');region.view_perspective='ORTHO'
    scene.render.filepath='//'+record['name']+'-preview.png'
    bpy.ops.wm.save_as_mainfile(filepath=str(path),compress=True,check_existing=False)
    record['blender_sha256']=hashlib.sha256(path.read_bytes()).hexdigest()
    bpy.ops.object.mode_set(mode='OBJECT')
    world=bpy.data.worlds.new('PreviewWorld');world.use_nodes=True;world.node_tree.nodes['Background'].inputs['Color'].default_value=(.6,.6,.6,1)
    world.node_tree.nodes['Background'].inputs['Strength'].default_value=.6;scene.world=world
    for name,loc,energy,size in [('Key',(-3,-5,6),700,5),('Fill',(4,-2,4),500,4),('Rim',(0,4,5),650,4)]:
        data=bpy.data.lights.new(name,'AREA');data.energy=energy;data.shape='DISK';data.size=size
        obj=bpy.data.objects.new(name,data);scene.collection.objects.link(obj);obj.location=loc;obj.rotation_euler=(Vector((0,0,1.5))-obj.location).to_track_quat('-Z','Y').to_euler()
    data=bpy.data.cameras.new('PreviewCamera');camera=bpy.data.objects.new('PreviewCamera',data);scene.collection.objects.link(camera)
    camera.location=(0,-10,4);camera.rotation_euler=(Vector((0,0,1.7))-camera.location).to_track_quat('-Z','Y').to_euler();data.type='ORTHO';data.ortho_scale=4.6;scene.camera=camera
    scene.render.engine='BLENDER_EEVEE';scene.eevee.taa_render_samples=16;scene.render.resolution_x=768;scene.render.resolution_y=768;scene.render.resolution_percentage=100
    scene.render.film_transparent=True;scene.render.image_settings.file_format='PNG';scene.render.image_settings.color_mode='RGBA'
    scene.render.filepath=str(out/(record['name']+'-native.png'));bpy.ops.render.render(write_still=True)
    reports.append({'name':record['name'],'ok':True,'scene_objects':record['objects'],'armatures':1,'meshes':len(meshes),'bones':len(rig.data.bones),'valid_simple_drivers':len(drivers),'external_dependencies':[]})
(out/'export-manifest.json').write_text(json.dumps(manifest,indent=2,ensure_ascii=False),encoding='utf-8')
(out/'native-verification.json').write_text(json.dumps({'ok':True,'characters':reports},indent=2),encoding='utf-8')
print(json.dumps({'ok':True,'characters':5}))
