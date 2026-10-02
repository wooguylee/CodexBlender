"""생성 그림의 차선에 실제 3D 경로를 투영 정합하고 접지 그림자를 셀 스타일로 단순화."""
import bpy, math, json
from mathutils import Vector
from bpy_extras.object_utils import world_to_camera_view
scene=bpy.data.scenes['Vvoori_Cafe_v003'];bpy.context.window.scene=scene
cam=scene.camera;out=PROJECT_ROOT/'outputs/vvoori-cafe/v003'
view=cam.data.view_frame(scene=scene)
left=min(v.x for v in view);right=max(v.x for v in view)
bottom=min(v.y for v in view);top=max(v.y for v in view);z=view[0].z
def ground(x,y):
    ray=cam.matrix_world.to_quaternion() @ Vector((left+x*(right-left),top-y*(top-bottom),z))
    return cam.location+ray*(-cam.location.z/ray.z)
# Measured pixel lines from the actual generated park, normalized image coordinates.
# Keep 3D wheels on painted asphalt; use independent straight world-space lane paths.
def road(x,t):
    far=.584-.176*x;near=.758-.328*x
    return far+(near-far)*t
records=[]
for lane,t in [('near',.72),('far',.27)]:
    a=ground(.08,road(.08,t));b=ground(.84,road(.84,t))
    slope=(b.y-a.y)/(b.x-a.x);intercept=a.y-slope*a.x
    for i in range(3) if lane=='near' else range(3,6):
        obj=bpy.data.objects[f'VC3_Traffic motion {i}']
        xexpr=next(f.driver.expression for f in obj.animation_data.drivers if f.data_path=='location' and f.array_index==0)
        f=obj.driver_add('location',1);f.driver.type='SCRIPTED';f.driver.expression=f'{slope}*({xexpr})+{intercept}'
        obj.rotation_euler.z=math.atan2(slope,1)+(0 if i<3 else math.pi)
        records.append({'car':obj.name,'lane':lane,'world_y_slope':slope,'world_y_intercept':intercept})

shadow=bpy.data.materials.new('VC3_Flat cartoon contact shadow');shadow.use_nodes=True
nt=shadow.node_tree;nt.nodes.clear();em=nt.nodes.new('ShaderNodeEmission');em.inputs[0].default_value=(.14,.16,.19,1)
op=nt.nodes.new('ShaderNodeOutputMaterial');nt.links.new(em.outputs[0],op.inputs[0])
for i in range(6):
    obj=bpy.data.objects[f'VC3_Traffic motion {i}']
    shadows=sorted([o for o in obj.children if 'contact shadow' in o.name.lower()],key=lambda o:o.name)
    for j,o in enumerate(shadows):
        o.hide_render=j!=0
        if j==0:o.data.materials.clear();o.data.materials.append(shadow)
# Pedestal base grounds the physical table in the illustrated floor.
bpy.context.window.view_layer=scene.view_layers['VC3_EditAll3D']
bpy.ops.mesh.primitive_cylinder_add(vertices=64,radius=.36,depth=.055,location=(-1.65,-.62,.028))
base=bpy.context.object;base.name='VC3_Table pedestal base'
for c in list(base.users_collection):c.objects.unlink(base)
bpy.data.collections['VC3_Foreground'].objects.link(base)
base.data.materials.append(bpy.data.materials['VC3_Dark wood'])
layer=scene.view_layers['VC3_Motion'];bpy.context.window.view_layer=layer
ng=scene.compositing_node_group;scene.compositing_node_group=None
for child in layer.layer_collection.children:child.exclude=child.name not in {'VC3_WindowSet','VC3_Foreground','VC3_Rig'}
scene.render.image_settings.color_mode='RGBA';scene.cycles.samples=16
scene.render.filepath=str(out/'static-3d-refined.png');bpy.ops.render.render(write_still=True)
im=bpy.data.images.load(scene.render.filepath,check_existing=False);im.name='VC3_Static3D_refined';im.alpha_mode='STRAIGHT';im.pack()
im.filepath='//../outputs/vvoori-cafe/v003/static-3d-refined.png';ng.nodes['Static3D'].image=im
for child in layer.layer_collection.children:child.exclude=child.name not in {'VC3_Traffic','VC3_Leaves','VC3_Rig'}
scene.compositing_node_group=ng;scene.render.image_settings.color_mode='RGB';scene.cycles.samples=8
scene.frame_set(2);scene.frame_set(1);bpy.context.view_layer.update()
scene.render.filepath=str(out/'poster-fullhd.png');bpy.ops.render.render(write_still=True)
scene.render.filepath='//../outputs/vvoori-cafe/v003/master-frames/'
(out/'road-fit.json').write_text(json.dumps(records,indent=2),encoding='utf-8')
print('Fitted road',records)
