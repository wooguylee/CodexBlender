"""승인된 겨울 카페: 새 AI 공원/실내 두 장 + 실제 3D 차량 6대와 눈 280개.

브리찌 run 전용. 기존 Scene/결과는 유지하고 독립 Scene을 만든다.
20초 주기는 480프레임이며 출력 1~480, 다음 주기 시작은 481이다.
"""
import bpy, math, random, json, hashlib
from mathutils import Vector
from bpy_extras.object_utils import world_to_camera_view

root=PROJECT_ROOT
out=root/'outputs/vvoori-cafe-winter/v001'
assets=root/'assets/vvoori-cafe-winter/v001'
name='Vvoori_Cafe_Winter_v001'
assert name not in bpy.data.scenes
assert not (root/'scenes/vvoori-cafe-winter-v001.blend').exists()
source=bpy.data.scenes['Vvoori_Cafe_v005']
assert source.camera.name=='VC5_Camera'
preserved={s.name:len(s.objects) for s in bpy.data.scenes}
scene=bpy.data.scenes.new(name)
bpy.context.window.scene=scene
scene.render.engine='CYCLES'
scene.cycles.samples=12
scene.cycles.use_denoising=False
scene.cycles.use_adaptive_sampling=False
scene.cycles.use_animated_seed=False
scene.cycles.seed=20261002
scene.cycles.max_bounces=1
scene.cycles.transparent_max_bounces=8
prefs=bpy.context.preferences.addons['cycles'].preferences
prefs.compute_device_type='OPTIX';prefs.get_devices()
for device in prefs.devices:device.use=device.type=='OPTIX'
scene.cycles.device='GPU'
scene.render.resolution_x=1920;scene.render.resolution_y=1080
scene.render.resolution_percentage=50
scene.render.fps=24;scene.frame_start=1;scene.frame_end=480
scene.render.image_settings.file_format='PNG'
scene.render.image_settings.color_mode='RGB'
scene.render.image_settings.color_depth='8'
scene.render.film_transparent=True
scene.render.use_persistent_data=True
scene.view_settings.view_transform='Standard';scene.view_settings.look='None'
scene.view_settings.exposure=0;scene.view_settings.gamma=1
scene.render.dither_intensity=0
scene.world=bpy.data.worlds.new('VWC1_World');scene.world.use_nodes=True
scene.world.node_tree.nodes['Background'].inputs[1].default_value=0
layer=scene.view_layers[0];layer.name='VWC1_Motion'

def collection(suffix):
    c=bpy.data.collections.new('VWC1_'+suffix);scene.collection.children.link(c);return c
traffic=collection('Traffic');snow=collection('Snow');rig=collection('Rig')
camdata=bpy.data.cameras.new('VWC1_Camera')
cam=bpy.data.objects.new('VWC1_Camera',camdata);rig.objects.link(cam)
cam.location=(-5,-4.5,1.8)
direction=Vector((math.sin(math.radians(50)),math.cos(math.radians(50)),-.079)).normalized()
cam.rotation_euler=direction.to_track_quat('-Z','Y').to_euler()
camdata.lens=28;camdata.sensor_width=36;camdata.clip_end=500
scene.camera=cam;bpy.context.view_layer.update()

def srgb(v):return v/12.92 if v<=.04045 else ((v+.055)/1.055)**2.4
def color(hex):return tuple(srgb(int(hex[i:i+2],16)/255) for i in (0,2,4))
def toon(suffix,hex):
    m=bpy.data.materials.new('VWC1_'+suffix);m.use_nodes=True
    nt=m.node_tree;nt.nodes.clear()
    normal=nt.nodes.new('ShaderNodeNewGeometry')
    dot=nt.nodes.new('ShaderNodeVectorMath');dot.operation='DOT_PRODUCT'
    dot.inputs[1].default_value=Vector((-.5,-.35,.8)).normalized()
    nt.links.new(normal.outputs['Normal'],dot.inputs[0])
    ramp=nt.nodes.new('ShaderNodeValToRGB');ramp.color_ramp.interpolation='CONSTANT'
    cr=ramp.color_ramp;cr.elements.remove(cr.elements[1])
    for e,pos,mult in [(cr.elements[0],0,.68),(cr.elements.new(.18),.18,.86),(cr.elements.new(.52),.52,1.0)]:
        e.position=pos;e.color=(*(v*mult for v in color(hex)),1)
    nt.links.new(dot.outputs['Value'],ramp.inputs[0])
    emission=nt.nodes.new('ShaderNodeEmission');nt.links.new(ramp.outputs['Color'],emission.inputs[0])
    output=nt.nodes.new('ShaderNodeOutputMaterial');nt.links.new(emission.outputs[0],output.inputs[0])
    return m
def flat(suffix,hex):
    m=bpy.data.materials.new('VWC1_'+suffix);m.use_nodes=True
    nt=m.node_tree;nt.nodes.clear();em=nt.nodes.new('ShaderNodeEmission')
    em.inputs[0].default_value=(*color(hex),1)
    op=nt.nodes.new('ShaderNodeOutputMaterial');nt.links.new(em.outputs[0],op.inputs[0]);return m
def drive(obj,path,index,expr):
    f=obj.driver_add(path,index);f.driver.type='SCRIPTED';f.driver.expression=expr

# Only the existing editable vehicle shapes are reused, with independent datablocks.
mapping={};materials={}
for old in bpy.data.collections['VC5_Traffic'].objects:
    obj=old.copy();obj.name=old.name.replace('VC5_','VWC1_',1)
    obj.animation_data_clear()
    if old.data:
        obj.data=old.data.copy();obj.data.name=obj.name
        for i,m in enumerate(obj.data.materials):
            if m:
                if m not in materials:materials[m]=m.copy();materials[m].name='VWC1_'+m.name
                obj.data.materials[i]=materials[m]
    traffic.objects.link(obj);mapping[old]=obj
for old,obj in mapping.items():
    if old.parent:obj.parent=mapping[old.parent]

view=camdata.view_frame(scene=scene)
left=min(p.x for p in view);right=max(p.x for p in view)
bottom=min(p.y for p in view);top=max(p.y for p in view);depth=view[0].z
def ray(u,v):return cam.matrix_world.to_quaternion()@Vector((left+u*(right-left),top-v*(top-bottom),depth))
def ground(u,v):
    r=ray(u,v);return cam.location+r*(-cam.location.z/r.z)
def on_y(u,v,y):
    r=ray(u,v);return cam.location+r*((y-cam.location.y)/r.y)
def road(u,t):
    far=.583-.176*u;near=.757-.329*u
    return far+(near-far)*t

palette=['758D79','B96857','738DAB','DBCEB5','C68D59','D9C682']
phases=[.06,.34,.72,.18,.51,.83]
schedule=[]
shadowmat=flat('Contact_shadow','68717A')
glassmat=toon('Bluegrey_cartoon_windows','637F8D')
rubbermat=toon('Warm_charcoal_tyres','42474B')
trim=toon('Warm_grey_trim','B7B7AA')
for i in range(6):
    obj=bpy.data.objects[f'VWC1_Traffic motion {i}']
    t=.74 if i<3 else .26
    a=ground(-.65,road(-.65,t));b=ground(.955,road(.955,t))
    sign=1 if i<3 else -1
    u=f'(({sign}*(frame-1)/480+{phases[i]})%1)'
    for axis in (0,1):drive(obj,'location',axis,f'{a[axis]}+{b[axis]-a[axis]}*{u}')
    obj.location.z=.0;obj.scale=(.78,.78,.78)
    obj.rotation_euler.z=math.atan2(b.y-a.y,b.x-a.x)+(0 if sign==1 else math.pi)
    paint=toon('Paint_'+str(i),palette[i])
    paint_names=['Car body','Car roof','pillar','Wing mirror','Car lower sill']
    for child in obj.children:
        if 'contact shadow' in child.name.lower():
            # Previous vehicle has several rings; retain only its already-enabled silhouette.
            child.location.z=.012
            child.data.materials.clear();child.data.materials.append(shadowmat)
        elif any(n in child.name for n in paint_names):
            child.data.materials.clear();child.data.materials.append(paint)
        elif 'glazed cabin' in child.name:
            child.data.materials.clear();child.data.materials.append(glassmat)
        elif 'tyre' in child.name:
            child.data.materials.clear();child.data.materials.append(rubbermat)
        elif any(n in child.name for n in ['Alloy wheel','Wheel center','Door handle','grille']):
            child.data.materials.clear();child.data.materials.append(trim)
    schedule.append({'car':obj.name,'lane':'near' if i<3 else 'far','phase':phases[i],
                     'direction':sign,'a':list(a),'b':list(b),'scale':.78,'speed_m_s':(b-a).length/20})

# Snow occupies two spatial bands outside the glass and outside the car swept volumes.
# Re-entry is beyond the image's top/bottom, never a scale fade or a visible jump.
rng=random.Random(102024)
snowmats=[flat('Snow_ivory','F3F1E7'),flat('Snow_bluegrey','DAE2E7'),flat('Snow_white','FAF8F0')]
snowrecords=[]
for i in range(280):
    near=i<170
    y=rng.uniform(.4,2.25) if near else rng.uniform(26,60)
    u=rng.uniform(-.08,.98)
    start=on_y(u,rng.uniform(-.24,-.10),y)
    end=on_y(u,rng.uniform(1.08,1.24),y)
    phase=rng.random();frequency=rng.choice([1,1,2])
    sway=rng.uniform(.017,.05) if near else rng.uniform(.06,.18)
    mid=(start+end)/2
    projected_depth=(mid-cam.location).dot(direction)
    pixel_radius=rng.uniform(.65,1.35) if near else rng.uniform(.35,.75)
    radius=pixel_radius*projected_depth*(36/28)/1920
    bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=1,radius=radius)
    flake=bpy.context.object;flake.name=f'VWC1_Snow_{i:03d}'
    for c in list(flake.users_collection):c.objects.unlink(flake)
    snow.objects.link(flake)
    flake.scale=(.8,.75,rng.uniform(.9,1.3))
    flake.data.materials.append(snowmats[rng.randrange(3)])
    unit=f'(((frame-1)/480+{phase})%1)'
    wave=f'{sway}*sin(6.283185307179586*{frequency}*(frame-1)/480+{phase*math.tau})'
    drive(flake,'location',0,f'{start.x}+({end.x-start.x})*{unit}+{wave}')
    flake.location.y=y
    drive(flake,'location',2,f'{start.z}+({end.z-start.z})*{unit}')
    flake['snow_band']='near' if near else 'far'
    flake['reset_offscreen']=True
    snowrecords.append({'name':flake.name,'y':y,'phase':phase,'start':list(start),'end':list(end),'radius':radius})

# Two original generated images only; no image-plane mesh and no static geometry cache.
ng=bpy.data.node_groups.new('VWC1_Park then 3D motion then Cafe','CompositorNodeTree')
ng.interface.new_socket(name='Image',in_out='OUTPUT',socket_type='NodeSocketColor')
images={}
for key,file in [('Park','ai-winter-park.png'),('Cafe','ai-winter-cafe.png')]:
    im=bpy.data.images.load(str(assets/file),check_existing=False)
    im.name='VWC1_'+key;im.colorspace_settings.name='sRGB';im.alpha_mode='STRAIGHT';im.pack()
    im.filepath='//../assets/vvoori-cafe-winter/v001/'+file;images[key]=im

def plate(key,x,y):
    n=ng.nodes.new('CompositorNodeImage');n.name=key;n.image=images[key];n.location=(x,y)
    socket=n.outputs['Image']
    if key=='Cafe':
        # Generated opaque interiors peak at 252/253. Remap 4..248 to 0..1,
        # retain antialiased contours while protecting fully opaque furniture.
        sub=ng.nodes.new('ShaderNodeMath');sub.operation='SUBTRACT';sub.inputs[1].default_value=4/255
        ng.links.new(n.outputs['Alpha'],sub.inputs[0])
        mul=ng.nodes.new('ShaderNodeMath');mul.operation='MULTIPLY';mul.use_clamp=True;mul.inputs[1].default_value=255/244
        ng.links.new(sub.outputs[0],mul.inputs[0])
        sa=ng.nodes.new('CompositorNodeSetAlpha');sa.inputs['Type'].default_value='Replace Alpha'
        ng.links.new(socket,sa.inputs['Image']);ng.links.new(mul.outputs[0],sa.inputs['Alpha']);socket=sa.outputs['Image']
    fit=ng.nodes.new('CompositorNodeScale');fit.name=key+'_Fit';fit.inputs['Type'].default_value='Render Size'
    fit.inputs['Extension X'].default_value='Extend';fit.inputs['Extension Y'].default_value='Extend'
    ng.links.new(socket,fit.inputs['Image']);return fit.outputs['Image']
park=plate('Park',-700,300);cafe=plate('Cafe',-700,-350)
motion=ng.nodes.new('CompositorNodeRLayers');motion.name='CarsAndSnow';motion.scene=scene;motion.layer=layer.name
def over(name,bg,fg):
    n=ng.nodes.new('CompositorNodeAlphaOver');n.name=name
    ng.links.new(bg,n.inputs['Background']);ng.links.new(fg,n.inputs['Foreground']);return n.outputs['Image']
combined=over('CarsSnow_over_Park',park,motion.outputs['Image'])
combined=over('OpaqueCafe_in_front',combined,cafe)
output=ng.nodes.new('NodeGroupOutput');ng.links.new(combined,output.inputs['Image'])
scene.compositing_node_group=ng
camdata.show_background_images=True
for key,order in [('Park','BACK'),('Cafe','FRONT')]:
    bg=camdata.background_images.new();bg.image=images[key];bg.display_depth=order;bg.alpha=1;bg.frame_method='FIT'
scene['camera_to_window_normal_degrees']=50
scene['loop_period_frames']=480;scene['loop_verification_endpoint']=481
scene['static_images_count']=2;scene['no_static_3d_geometry_or_cache']=True
scene['workflow']='AI winter park -> real 3D cars/snow -> AI opaque cafe/perimeter/furniture'
scene.frame_set(1)
scene.render.filepath='//../outputs/vvoori-cafe-winter/v001/master-frames/'
for screen in bpy.data.screens:
    for area in screen.areas:
        if area.type=='VIEW_3D':area.spaces.active.region_3d.view_perspective='CAMERA'
assert all(len(bpy.data.scenes[n].objects)==count for n,count in preserved.items())
report={'ok':True,'scene':scene.name,'objects':len(scene.objects),'cars':schedule,'snow_count':len(snowrecords),
        'snow':snowrecords,'preserved_scene_counts':preserved,'packed_images':{
            key:hashlib.sha256(im.packed_file.data).hexdigest() for key,im in images.items()},
        'static_image_count':2,'static_geometry':0,'camera_angle_degrees':50,'period_frames':480}
(out/'build-report.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
print(json.dumps({k:report[k] for k in ['ok','scene','objects','snow_count','static_image_count','period_frames']},indent=2))
