"""사용자 요청: 테이블·의자도 실내 생성 이미지에 포함. v003은 보존하고 v004를 분리한다."""
import bpy, json, hashlib
root=PROJECT_ROOT;out=root/'outputs/vvoori-cafe/v004';out.mkdir(parents=True,exist_ok=True)
source=bpy.data.scenes['Vvoori_Cafe_v003'];assert source.camera.name=='VC3_Camera'
assert 'Vvoori_Cafe_v004' not in bpy.data.scenes
hashes={p:hashlib.sha256((root/p).read_bytes()).hexdigest() for p in ['scenes/vvoori-cafe-v003.blend','scenes/vvoori-cafe-v002.blend','outputs/vvoori-cafe/v003/vvoori-cafe-toon-20s.mp4']}
scene=source.copy();scene.name='Vvoori_Cafe_v004';bpy.context.window.scene=scene
for c in list(scene.collection.children):scene.collection.children.unlink(c)
objects={};materials={}
for suffix in ['Traffic','Leaves','WindowSet','Rig']:
    dst=bpy.data.collections.new('VC4_'+suffix);scene.collection.children.link(dst)
    for old in bpy.data.collections['VC3_'+suffix].objects:
        obj=old.copy();obj.name=old.name.replace('VC3_','VC4_',1)
        if old.data:
            obj.data=old.data.copy();obj.data.name=obj.name
            if hasattr(obj.data,'materials'):
                for i,mat in enumerate(obj.data.materials):
                    if mat:
                        if mat not in materials:materials[mat]=mat.copy();materials[mat].name=mat.name.replace('VC3_','VC4_',1)
                        obj.data.materials[i]=materials[mat]
        dst.objects.link(obj);objects[old]=obj
for old,obj in objects.items():
    if old.parent:obj.parent=objects[old.parent]
scene.camera=objects[source.camera];scene.world=source.world.copy();scene.world.name='VC4_World'
motion=scene.view_layers[0];motion.name='VC4_Motion';motion.use=True
edit=scene.view_layers[1];edit.name='VC4_EditAll3D';edit.use=False
bpy.context.window.view_layer=motion
ng=source.compositing_node_group.copy();ng.name='VC4_Illustrated furniture + 3D window and motion'
scene.compositing_node_group=None
for child in motion.layer_collection.children:child.exclude=child.name not in {'VC4_WindowSet','VC4_Rig'}
for child in edit.layer_collection.children:child.exclude=False
scene.render.image_settings.color_mode='RGBA';scene.cycles.samples=16
scene.render.filepath=str(out/'static-window-3d.png');bpy.ops.render.render(write_still=True)
window_image=bpy.data.images.load(scene.render.filepath,check_existing=False);window_image.name='VC4_StaticWindow'
window_image.alpha_mode='STRAIGHT';window_image.pack();window_image.filepath='//../outputs/vvoori-cafe/v004/static-window-3d.png'
interior=bpy.data.images.load(str(root/'assets/vvoori-cafe/v004/ai-furnished-interior.png'),check_existing=False)
interior.name='VC4_FurnishedInterior';interior.alpha_mode='STRAIGHT';interior.colorspace_settings.name='sRGB';interior.pack()
interior.filepath='//../assets/vvoori-cafe/v004/ai-furnished-interior.png'
ng.nodes['Interior'].image=interior;ng.nodes['Static3D'].image=window_image
ng.nodes['Motion3D'].scene=scene;ng.nodes['Motion3D'].layer=motion.name
# Furniture must occlude the physical mullions, so the interior image is LAST.
win_over=ng.nodes['Real3DWindowTableCup'];win_over.name='Real3DWindow';win_over.label='Window frame only'
inside_over=ng.nodes['GeneratedInterior']
ng.links.new(ng.nodes['CarsAndLeavesOverPark'].outputs['Image'],win_over.inputs['Background'])
ng.links.new(win_over.outputs['Image'],inside_over.inputs['Background'])
output=next(n for n in ng.nodes if n.type=='GROUP_OUTPUT');ng.links.new(inside_over.outputs['Image'],output.inputs['Image'])
win_over.location=(-100,350);inside_over.location=(200,350)
for child in motion.layer_collection.children:child.exclude=child.name not in {'VC4_Traffic','VC4_Leaves','VC4_Rig'}
scene.compositing_node_group=ng;scene.cycles.samples=8;scene.render.image_settings.color_mode='RGB'
for bg in list(scene.camera.data.background_images):scene.camera.data.background_images.remove(bg)
for image,depth in [(ng.nodes['Park'].image,'BACK'),(interior,'FRONT')]:
    bg=scene.camera.data.background_images.new();bg.image=image;bg.display_depth=depth;bg.alpha=1;bg.frame_method='FIT'
scene['workflow']='Generated park + 3D cars/leaves/window + generated furnished interior'
scene['furniture_is_generated_image']=True
scene['static_3d_cache']='WindowSet only. Furniture/cups/books are part of the generated interior PNG.'
scene.frame_set(2);scene.frame_set(1);bpy.context.view_layer.update()
scene.render.filepath=str(out/'poster-fullhd.png');bpy.ops.render.render(write_still=True)
scene.render.filepath='//../outputs/vvoori-cafe/v004/master-frames/'
bpy.context.window.view_layer=edit
assert not set(scene.objects).intersection(source.objects)
assert not any(any(word in o.name for word in ['Table','Cup','Saucer','Book','Chair','Coffee']) for o in scene.objects)
assert all(hashlib.sha256((root/p).read_bytes()).hexdigest()==h for p,h in hashes.items())
report={'ok':True,'scene':scene.name,'camera':scene.camera.name,'objects':len(scene.objects),'furniture_is_generated_image':True,
    'source_hashes':hashes,'collections':{c.name:len(c.objects) for c in scene.collection.children},
    'packed_images':{n.name:{'path':n.image.filepath,'sha256':hashlib.sha256(n.image.packed_file.data).hexdigest()} for n in ng.nodes if n.type=='IMAGE'}}
(out/'project-build.json').write_text(json.dumps(report,indent=2),encoding='utf-8');print(json.dumps(report,indent=2))
