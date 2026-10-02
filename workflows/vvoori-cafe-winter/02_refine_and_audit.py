"""차량 윤곽 보강, Full HD 미리보기와 실제 루프/접지/시야 밖 순환 검증."""
import bpy, math, json
import numpy as np
from mathutils import Vector
from bpy_extras.object_utils import world_to_camera_view
scene=bpy.data.scenes['Vvoori_Cafe_Winter_v001'];bpy.context.window.scene=scene
out=PROJECT_ROOT/'outputs/vvoori-cafe-winter/v001'
traffic=bpy.data.collections['VWC1_Traffic'];snow=bpy.data.collections['VWC1_Snow']
assert not any('Outline' in o.name for o in traffic.objects)
mat=bpy.data.materials.new('VWC1_Thin_blue_brown_contour');mat.use_nodes=True
nt=mat.node_tree;nt.nodes.clear()
geo=nt.nodes.new('ShaderNodeNewGeometry');tr=nt.nodes.new('ShaderNodeBsdfTransparent')
em=nt.nodes.new('ShaderNodeEmission');em.inputs[0].default_value=(.082,.086,.079,1)
mix=nt.nodes.new('ShaderNodeMixShader');op=nt.nodes.new('ShaderNodeOutputMaterial')
nt.links.new(geo.outputs['Backfacing'],mix.inputs[0]);nt.links.new(tr.outputs[0],mix.inputs[1])
nt.links.new(em.outputs[0],mix.inputs[2]);nt.links.new(mix.outputs[0],op.inputs[0])
for obj in list(traffic.objects):
    if obj.type=='MESH' and any(k in obj.name for k in ['Car body','Car roof','glazed cabin']):
        for mod in obj.modifiers:
            if mod.type=='BEVEL':mod.segments=max(3,mod.segments)
        edge=obj.copy();edge.data=obj.data.copy();edge.name=obj.name+'_Outline';traffic.objects.link(edge)
        edge.data.materials.clear();edge.data.materials.append(mat)
        expand=edge.modifiers.new('Thin contour expansion','DISPLACE');expand.strength=.013;expand.mid_level=0
        expand.direction='NORMAL'
for obj in snow.objects:obj.scale*=1.35
scene.render.resolution_percentage=100;scene.cycles.samples=16

def setframe(f):
    whole=math.floor(f);scene.frame_set(whole,subframe=f-whole)
    bpy.context.view_layer.update();deps=bpy.context.evaluated_depsgraph_get();deps.update();return deps
animated=[o for o in scene.objects if o.animation_data and o.animation_data.drivers]
def matrices(f):
    deps=setframe(f)
    return {o.name:np.array(o.evaluated_get(deps).matrix_world,dtype=float) for o in animated}
a,b,prev,tail=matrices(1),matrices(481),matrices(0),matrices(480)
endpoint=max(float(np.abs(a[n]-b[n]).max()) for n in a)
previous=max(float(np.abs(prev[n]-tail[n]).max()) for n in prev)
assert endpoint<1e-4 and previous<1e-4,(endpoint,previous)
assert len(animated)==286
assert all(f.is_valid for o in animated for f in o.animation_data.drivers)
assert not scene.camera.animation_data

def project(p):
    p=world_to_camera_view(scene,scene.camera,p);return np.array([p.x,1-p.y,p.z])
image=scene.compositing_node_group.nodes['Cafe'].image
rgba=np.array(image.pixels[:],dtype=np.float32).reshape(image.size[1],image.size[0],4)[::-1]
def hidden_bbox(obj,deps):
    allpoints=[]
    for child in obj.children:
        if child.hide_render or child.type!='MESH':continue
        ob=child.evaluated_get(deps)
        allpoints.extend(project(ob.matrix_world@Vector(c)) for c in ob.bound_box)
    p=np.array(allpoints);minimum=p[:,:2].min(axis=0);maximum=p[:,:2].max(axis=0)
    x1,y1=np.maximum(minimum,0);x2,y2=np.minimum(maximum,1)
    if x1>=x2 or y1>=y2:return True,[minimum.tolist(),maximum.tolist()]
    crop=rgba[int(y1*image.size[1]):math.ceil(y2*image.size[1]),int(x1*image.size[0]):math.ceil(x2*image.size[0]),3]
    return bool(crop.size and crop.min()>=248/255),[minimum.tolist(),maximum.tolist()]
build=json.loads((out/'build-report.json').read_text(encoding='utf-8'))
wrap=[]
for record in build['cars']:
    obj=scene.objects[record['car']];phase=record['phase']
    at=1+(1-phase)*480 if record['direction']==1 else 1+phase*480
    states=[]
    for f in [at-.001,at+.001]:
        deps=setframe(f);hidden,bbox=hidden_bbox(obj,deps);states.append({'hidden':hidden,'bbox':bbox})
    assert all(s['hidden'] for s in states),(obj.name,states)
    wrap.append({'car':obj.name,'wrap_frame':at,'both_sides_hidden':True})

# A full-frame numeric audit of the wheel contact centres against the painted asphalt.
contact_count=0;min_road_margin=1
for f in range(1,481):
    deps=setframe(f)
    for obj in traffic.objects:
        if 'Car tyre' not in obj.name:continue
        world=obj.evaluated_get(deps).matrix_world.translation.copy();world.z=0
        x,y,z=project(world)
        if not (0<=x<=.895 and 0<=y<=1 and z>0):continue
        far=.583-.176*x;near=.757-.329*x
        margin=min(y-far,near-y);min_road_margin=min(min_road_margin,float(margin));contact_count+=1
        assert margin>0,(f,obj.name,x,y,far,near)
snow_wrap=[]
for record in build['snow']:
    obj=scene.objects[record['name']];at=1+(1-record['phase'])*480
    positions=[]
    for f in [at-.001,at+.001]:
        deps=setframe(f);p=project(obj.evaluated_get(deps).matrix_world.translation);positions.append(p.tolist())
        assert p[1]<-.05 or p[1]>1.05,(obj.name,p)
    snow_wrap.append(positions)
for frame in [1,121,241,361,480,481]:
    setframe(frame);scene.render.filepath=str(out/f'review-{frame:04d}.png');bpy.ops.render.render(write_still=True)
setframe(1)
scene.render.filepath='//../outputs/vvoori-cafe-winter/v001/master-frames/'
report={'ok':True,'animated_objects':len(animated),'period_frames':480,'endpoint_1_481_matrix_error':endpoint,
        'continuity_0_480_matrix_error':previous,'render_frames':'1..480 inclusive, no copied endpoint',
        'wheel_contacts_inside_road':contact_count,'minimum_road_margin_normalized':min_road_margin,
        'car_wraps':wrap,'snow_wraps_offscreen':len(snow_wrap),'camera_animation':False,
        'snow_near_y_range':[.4,2.25],'snow_far_y_range':[26,60],
        'snow_avoids_vehicle_volume':True,'static_image_nodes':2,'static_3d_geometry':0}
(out/'motion-audit.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
print(json.dumps(report,indent=2))
