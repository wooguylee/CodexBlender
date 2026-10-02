"""카페/공원은 단 한 번 렌더. 차량/낙엽만 합성하여 정적 영역 깜빡임 방지."""
import bpy, json, time
scene=bpy.context.scene
assert scene.name=='Autumn_Cafe_v001'
out=PROJECT_ROOT/'outputs/autumn-cafe/v001'
assets=PROJECT_ROOT/'assets/autumn-cafe/v001';assets.mkdir(parents=True,exist_ok=True)
plate=assets/'afternoon-background.exr'
assert not plate.exists(), 'Existing bake must be versioned.'
glass=bpy.data.collections.new('AC_StaticGlass');scene.collection.children.link(glass)
for o in list(bpy.data.collections['AC_Interior'].objects):
    if o.get('exclude_fx_holdout'):
        bpy.data.collections['AC_Interior'].objects.unlink(o);glass.objects.link(o)
def lc(layer,name):return layer.layer_collection.children[name]
beauty=scene.view_layers[0];beauty.name='StaticAfternoon'
lc(beauty,'AC_Traffic').exclude=True;lc(beauty,'AC_FallingLeaves').exclude=True
scene.render.resolution_percentage=100;scene.cycles.samples=160
scene.cycles.use_adaptive_sampling=False;scene.cycles.use_denoising=True
scene.render.image_settings.file_format='OPEN_EXR';scene.render.image_settings.color_mode='RGBA';scene.render.image_settings.color_depth='16'
scene.render.film_transparent=False;scene.render.filepath=str(plate)
t=time.monotonic();scene.frame_set(1);bpy.ops.render.render(write_still=True)
plate_time=time.monotonic()-t
im=bpy.data.images.load(str(plate));im.pack();im.filepath='//../assets/autumn-cafe/v001/afternoon-background.exr'
fx=scene.view_layers.new('MovingLeavesAndTraffic')
lc(fx,'AC_Park').exclude=True;lc(fx,'AC_StaticGlass').exclude=True
lc(fx,'AC_Interior').holdout=True
beauty.use=False;fx.use=True
scene.render.film_transparent=True
ng=bpy.data.node_groups.new('AC_Stable afternoon composite','CompositorNodeTree')
ng.interface.new_socket(name='Image',in_out='OUTPUT',socket_type='NodeSocketColor')
rl=ng.nodes.new('CompositorNodeRLayers');rl.scene=scene;rl.layer=fx.name
bg=ng.nodes.new('CompositorNodeImage');bg.image=im
over=ng.nodes.new('CompositorNodeAlphaOver')
ng.links.new(bg.outputs['Image'],over.inputs['Background']);ng.links.new(rl.outputs['Image'],over.inputs['Foreground'])
output=ng.nodes.new('NodeGroupOutput');ng.links.new(over.outputs['Image'],output.inputs['Image'])
scene.compositing_node_group=ng
scene.cycles.samples=32;scene.cycles.use_denoising=True
scene.cycles.use_animated_seed=False;scene.cycles.seed=215
scene.render.image_settings.file_format='PNG';scene.render.image_settings.color_mode='RGB';scene.render.image_settings.color_depth='8'
scene.render.filepath='//../outputs/autumn-cafe/v001/frames/'
scene['background_locked']=True;scene['background_plate']='assets/autumn-cafe/v001/afternoon-background.exr'
bpy.context.window.view_layer=fx
(out/'background-report.json').write_text(json.dumps({'ok':True,'plate_seconds':plate_time,'plate_samples':160,'animated_samples':32,'packed':bool(im.packed_file),'method':'fixed linear HDR plate plus Blender traffic and falling leaf layer'},indent=2),encoding='utf-8')
print('Background locked and packed',plate_time)
