"""새 생성 이미지와 실제 3D를 결합한다. 고정 실내 3D만 1회 캐시하여 깜빡임 방지."""
import bpy
import json
import hashlib

scene=bpy.data.scenes['Vvoori_Cafe_v003']
bpy.context.window.scene=scene
root=PROJECT_ROOT;out=root/'outputs/vvoori-cafe/v003';assets=root/'assets/vvoori-cafe/v003'
assert scene.compositing_node_group is None
old_paths=['scenes/vvoori-cafe-v002.blend','scenes/vvoori-cafe-v001.blend','scenes/autumn-cafe-v001.blend']
hashes={p:hashlib.sha256((root/p).read_bytes()).hexdigest() for p in old_paths}
scene.render.resolution_percentage=100
scene.cycles.samples=16
scene.render.image_settings.color_mode='RGBA'
layer=scene.view_layers[0];layer.name='VC3_Motion'
bpy.context.window.view_layer=layer
for child in layer.layer_collection.children:
    child.exclude=child.name not in {'VC3_WindowSet','VC3_Foreground','VC3_Rig'}
scene.render.filepath=str(out/'static-3d.png')
bpy.ops.render.render(write_still=True)
for child in layer.layer_collection.children:
    child.exclude=child.name not in {'VC3_Traffic','VC3_Leaves','VC3_Rig'}
# Editable complete geometry in a second, non-rendered view layer.
edit=scene.view_layers.new('VC3_EditAll3D');edit.use=False
edit.layer_collection.children['VC3_Guides'].exclude=True
bpy.context.window.view_layer=layer
images={}
for key,path in [('Park',assets/'ai-oblique-park.png'),('Interior',assets/'ai-oblique-interior.png'),('Static3D',out/'static-3d.png')]:
    im=bpy.data.images.load(str(path),check_existing=False);im.name='VC3_'+key
    im.colorspace_settings.name='sRGB';im.alpha_mode='STRAIGHT';im.pack()
    im.filepath='//../'+path.relative_to(root).as_posix();images[key]=im
ng=bpy.data.node_groups.new('VC3_Generated art + toon 3D','CompositorNodeTree')
ng.interface.new_socket(name='Image',in_out='OUTPUT',socket_type='NodeSocketColor')

def plate(key,x,y):
    n=ng.nodes.new('CompositorNodeImage');n.name=key;n.image=images[key];n.location=(x,y)
    fit=ng.nodes.new('CompositorNodeScale');fit.name=key+'_Fit';fit.inputs['Type'].default_value='Render Size';fit.location=(x+180,y)
    socket=n.outputs['Image']
    if key=='Interior':
        alpha=ng.nodes.new('ShaderNodeMath');alpha.operation='MULTIPLY';alpha.use_clamp=True;alpha.inputs[1].default_value=255/250
        ng.links.new(n.outputs['Alpha'],alpha.inputs[0]);alpha.location=(x,y-130)
        sa=ng.nodes.new('CompositorNodeSetAlpha');sa.inputs['Type'].default_value='Replace Alpha';sa.location=(x+180,y-130)
        ng.links.new(socket,sa.inputs['Image']);ng.links.new(alpha.outputs[0],sa.inputs['Alpha']);socket=sa.outputs['Image']
    ng.links.new(socket,fit.inputs['Image']);return fit.outputs['Image']

park=plate('Park',-900,350);inside=plate('Interior',-500,-100);static=plate('Static3D',-100,-300)
motion=ng.nodes.new('CompositorNodeRLayers');motion.scene=scene;motion.layer=layer.name;motion.name='Motion3D';motion.location=(-700,50)
def over(name,background,foreground,x):
    n=ng.nodes.new('CompositorNodeAlphaOver');n.name=name;n.location=(x,350)
    ng.links.new(background,n.inputs['Background']);ng.links.new(foreground,n.inputs['Foreground']);return n.outputs['Image']
combined=over('CarsAndLeavesOverPark',park,motion.outputs['Image'],-450)
combined=over('GeneratedInterior',combined,inside,-100)
combined=over('Real3DWindowTableCup',combined,static,200)
output=ng.nodes.new('NodeGroupOutput');output.location=(450,350);ng.links.new(combined,output.inputs['Image'])
scene.compositing_node_group=ng
scene.render.image_settings.color_mode='RGB';scene.cycles.samples=8
scene['static_images_are_ai_generated']=True
scene['static_3d_cache']='Rebake WindowSet + Foreground after editing geometry/camera; editable geometry retained'
scene.frame_set(1)
scene.render.filepath=str(out/'poster-first.png');bpy.ops.render.render(write_still=True)
scene.render.filepath='//../outputs/vvoori-cafe/v003/master-frames/'
scene.camera.data.show_background_images=True
for key,depth in [('Park','BACK'),('Interior','FRONT')]:
    bg=scene.camera.data.background_images.new();bg.image=images[key];bg.display_depth=depth;bg.alpha=1;bg.frame_method='FIT'
report={'ok':True,'scene':scene.name,'camera':scene.camera.name,'angle_degrees':scene['camera_to_window_normal_degrees'],
        'objects':len(scene.objects),'generated_static_images':True,'source_hashes':hashes,
        'packed_images':{key:{'path':im.filepath,'size':list(im.size),'sha256':hashlib.sha256(im.packed_file.data).hexdigest()} for key,im in images.items()}}
(out/'project-build.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
print(json.dumps(report,indent=2))
