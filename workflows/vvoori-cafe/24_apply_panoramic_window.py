"""사용자 요청: 창틀은 카페 이미지에, 통창은 넓게. 3D 창틀/창턱과 캐시를 v005에서 제외."""
import bpy,json,hashlib
root=PROJECT_ROOT;out=root/'outputs/vvoori-cafe/v005';out.mkdir(parents=True,exist_ok=True)
source=bpy.data.scenes['Vvoori_Cafe_v004'];assert source.camera.name=='VC4_Camera'
assert 'Vvoori_Cafe_v005' not in bpy.data.scenes
hashes={p:hashlib.sha256((root/p).read_bytes()).hexdigest() for p in ['scenes/vvoori-cafe-v004.blend','scenes/vvoori-cafe-v003.blend','outputs/vvoori-cafe/v004/vvoori-cafe-toon-20s.mp4']}
scene=source.copy();scene.name='Vvoori_Cafe_v005';bpy.context.window.scene=scene
for c in list(scene.collection.children):scene.collection.children.unlink(c)
objects={};materials={}
for suffix in ['Traffic','Leaves','Rig']:
    dst=bpy.data.collections.new('VC5_'+suffix);scene.collection.children.link(dst)
    for old in bpy.data.collections['VC4_'+suffix].objects:
        obj=old.copy();obj.name=old.name.replace('VC4_','VC5_',1)
        if old.data:
            obj.data=old.data.copy();obj.data.name=obj.name
            if hasattr(obj.data,'materials'):
                for i,mat in enumerate(obj.data.materials):
                    if mat:
                        if mat not in materials:materials[mat]=mat.copy();materials[mat].name=mat.name.replace('VC4_','VC5_',1)
                        obj.data.materials[i]=materials[mat]
        dst.objects.link(obj);objects[old]=obj
for old,obj in objects.items():
    if old.parent:obj.parent=objects[old.parent]
scene.camera=objects[source.camera];scene.world=source.world.copy();scene.world.name='VC5_World'
motion=scene.view_layers[0];motion.name='VC5_Motion';motion.use=True
bpy.context.window.view_layer=motion
for other in list(scene.view_layers):
    if other!=motion:scene.view_layers.remove(other)
for child in motion.layer_collection.children:child.exclude=False
ng=source.compositing_node_group.copy();ng.name='VC5_Park + 3D motion + panoramic cafe image'
interior=bpy.data.images.load(str(root/'assets/vvoori-cafe/v005/ai-panoramic-interior.png'),check_existing=False)
interior.name='VC5_PanoramicInterior';interior.alpha_mode='STRAIGHT';interior.colorspace_settings.name='sRGB';interior.pack()
interior.filepath='//../assets/vvoori-cafe/v005/ai-panoramic-interior.png'
ng.nodes['Interior'].image=interior
ng.nodes['Motion3D'].scene=scene;ng.nodes['Motion3D'].layer=motion.name
ng.links.new(ng.nodes['CarsAndLeavesOverPark'].outputs['Image'],ng.nodes['GeneratedInterior'].inputs['Background'])
for name in ['Real3DWindow','Static3D','Static3D_Fit']:ng.nodes.remove(ng.nodes[name])
ng.nodes['GeneratedInterior'].location=(-100,350)
scene.compositing_node_group=ng
for bg in list(scene.camera.data.background_images):scene.camera.data.background_images.remove(bg)
for image,depth in [(ng.nodes['Park'].image,'BACK'),(interior,'FRONT')]:
    bg=scene.camera.data.background_images.new();bg.image=image;bg.display_depth=depth;bg.alpha=1;bg.frame_method='FIT'
scene['workflow']='Generated park + 3D cars/leaves + generated panoramic cafe including window perimeter and furniture'
scene['window_and_furniture_are_generated_image']=True
scene['static_3d_cache']='None: no static geometry or static 3D cache in this version'
scene.cycles.samples=8;scene.render.image_settings.color_mode='RGB'
scene.frame_set(2);scene.frame_set(1);bpy.context.view_layer.update()
scene.render.filepath=str(out/'poster-fullhd.png');bpy.ops.render.render(write_still=True)
scene.render.filepath='//../outputs/vvoori-cafe/v005/master-frames/'
assert len(scene.objects)==285
assert not set(scene.objects).intersection(source.objects)
assert not any(any(word in o.name for word in ['Window','sill','Table','Cup','Book','Chair','Coffee']) for o in scene.objects if not o.name.startswith('VC5_Car'))
assert len([n for n in ng.nodes if n.type=='IMAGE'])==2
assert all(hashlib.sha256((root/p).read_bytes()).hexdigest()==h for p,h in hashes.items())
report={'ok':True,'scene':scene.name,'camera':scene.camera.name,'objects':len(scene.objects),'no_3d_window_or_furniture':True,
    'source_hashes':hashes,'collections':{c.name:len(c.objects) for c in scene.collection.children},
    'packed_images':{n.name:{'path':n.image.filepath,'sha256':hashlib.sha256(n.image.packed_file.data).hexdigest()} for n in ng.nodes if n.type=='IMAGE'}}
(out/'project-build.json').write_text(json.dumps(report,indent=2),encoding='utf-8');print(json.dumps(report,indent=2))
