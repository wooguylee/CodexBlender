"""v003: 창면 정면에서 50도 사선 카메라, 실제 3D 창틀/탁자/잔, 만화풍 움직임.

이미지 생성에 사용할 구도 가이드만 먼저 출력한다. 가이드를 최종 배경으로 사용하지 않는다.
"""
import bpy
import math
import json
from mathutils import Vector
from bpy_extras.object_utils import world_to_camera_view

root = PROJECT_ROOT
out = root/'outputs/vvoori-cafe/v003'
out.mkdir(parents=True, exist_ok=True)
assert 'Vvoori_Cafe_v003' not in bpy.data.scenes
source = bpy.data.scenes['Vvoori_Cafe_v002']
scene = bpy.data.scenes.new('Vvoori_Cafe_v003')
bpy.context.window.scene = scene
scene.render.engine = 'CYCLES'
scene.cycles.samples = 8
scene.cycles.use_denoising = False
scene.cycles.use_adaptive_sampling = False
scene.cycles.use_animated_seed = False
scene.cycles.seed = 50
scene.cycles.max_bounces = 2
scene.cycles.transparent_max_bounces = 16
scene.cycles.device = 'GPU'
prefs = bpy.context.preferences.addons['cycles'].preferences
prefs.compute_device_type = 'OPTIX'; prefs.get_devices()
for device in prefs.devices:
    device.use = device.type == 'OPTIX'
scene.render.resolution_x = 1920; scene.render.resolution_y = 1080
scene.render.resolution_percentage = 50
scene.render.fps = 24; scene.frame_start = 1; scene.frame_end = 480
scene.render.image_settings.file_format = 'PNG'
scene.render.image_settings.color_mode = 'RGBA'
scene.render.image_settings.color_depth = '8'
scene.render.film_transparent = True
scene.render.use_persistent_data = True
scene.view_settings.view_transform = 'Standard'
scene.view_settings.look = 'None'
scene.world = bpy.data.worlds.new('VC3_World')
scene.world.use_nodes = True
scene.world.node_tree.nodes['Background'].inputs[0].default_value = (.48,.66,.72,1)
scene.world.node_tree.nodes['Background'].inputs[1].default_value = .6

def collection(name):
    c=bpy.data.collections.new('VC3_'+name);scene.collection.children.link(c);return c
traffic=collection('Traffic'); leaves=collection('Leaves'); window=collection('WindowSet')
foreground=collection('Foreground'); rig=collection('Rig'); guides=collection('Guides')

def flat(name, color):
    m=bpy.data.materials.new('VC3_'+name);m.use_nodes=True
    nt=m.node_tree;nt.nodes.clear()
    em=nt.nodes.new('ShaderNodeEmission');em.inputs[0].default_value=(*color,1)
    op=nt.nodes.new('ShaderNodeOutputMaterial');nt.links.new(em.outputs[0],op.inputs[0]);return m

def toon(name, color):
    m=bpy.data.materials.new('VC3_'+name);m.use_nodes=True
    nt=m.node_tree;nt.nodes.clear()
    geo=nt.nodes.new('ShaderNodeNewGeometry')
    dot=nt.nodes.new('ShaderNodeVectorMath');dot.operation='DOT_PRODUCT'
    dot.inputs[1].default_value=Vector((-.55,-.35,.76)).normalized()
    nt.links.new(geo.outputs['Normal'],dot.inputs[0])
    step=nt.nodes.new('ShaderNodeMath');step.operation='GREATER_THAN';step.inputs[1].default_value=.35
    nt.links.new(dot.outputs['Value'],step.inputs[0])
    tone=nt.nodes.new('ShaderNodeMath');tone.operation='MULTIPLY_ADD'
    tone.inputs[1].default_value=.26;tone.inputs[2].default_value=.74
    nt.links.new(step.outputs[0],tone.inputs[0])
    multiply=nt.nodes.new('ShaderNodeMixRGB');multiply.blend_type='MULTIPLY';multiply.inputs[0].default_value=1
    multiply.inputs[1].default_value=(*color,1);nt.links.new(tone.outputs[0],multiply.inputs[2])
    em=nt.nodes.new('ShaderNodeEmission');nt.links.new(multiply.outputs[0],em.inputs[0])
    op=nt.nodes.new('ShaderNodeOutputMaterial');nt.links.new(em.outputs[0],op.inputs[0]);return m

def link(obj, c):
    for parent in list(obj.users_collection):parent.objects.unlink(obj)
    c.objects.link(obj);return obj

def box(name,loc,dims,mat,c,bevel=0):
    bpy.ops.mesh.primitive_cube_add(size=1,location=loc)
    o=link(bpy.context.object,c);o.name='VC3_'+name;o.dimensions=dims
    bpy.ops.object.transform_apply(location=False,rotation=False,scale=True)
    o.data.materials.append(mat)
    if bevel:
        mod=o.modifiers.new('Rounded cartoon edges','BEVEL');mod.width=bevel;mod.segments=2
        o.modifiers.new('Normals','WEIGHTED_NORMAL')
    return o

def cylinder(name,loc,r,depth,mat,c,vertices=48):
    bpy.ops.mesh.primitive_cylinder_add(vertices=vertices,radius=r,depth=depth,location=loc)
    o=link(bpy.context.object,c);o.name='VC3_'+name;o.data.materials.append(mat)
    return o

def lathe(name,loc,profile,mat):
    vs=[];fs=[];n=64
    for r,z in profile:vs.extend((loc[0]+r*math.cos(i*math.tau/n),loc[1]+r*math.sin(i*math.tau/n),loc[2]+z) for i in range(n))
    for j in range(len(profile)-1):
        for i in range(n):a=j*n+i;b=j*n+(i+1)%n;fs.append((a,b,b+n,a+n))
    me=bpy.data.meshes.new(name);me.from_pydata(vs,[],fs);me.materials.append(mat)
    o=bpy.data.objects.new('VC3_'+name,me);foreground.objects.link(o)
    for p in me.polygons:p.use_smooth=True
    return o

# Independent copies of the approved 3D motion, with cel-shaded materials.
mapping={}; mats={}
for cname, dst in [('VC2_Traffic',traffic),('VC2_FallingLeaves',leaves)]:
    for old in bpy.data.collections[cname].objects:
        obj=old.copy();obj.name=old.name.replace('VC2_','VC3_',1)
        if old.data:
            obj.data=old.data.copy()
            if hasattr(obj.data,'materials'):
                for i,mat in enumerate(obj.data.materials):
                    if mat not in mats:
                        if mat and 'Contact shadow' not in mat.name:
                            p=mat.node_tree.nodes.get('Principled BSDF') if mat.use_nodes else None
                            color=tuple(p.inputs['Base Color'].default_value[:3]) if p else (.65,.3,.065)
                            mats[mat]=toon(mat.name.replace('VC2_',''),color)
                        else:mats[mat]=mat.copy() if mat else None
                    obj.data.materials[i]=mats[mat]
        dst.objects.link(obj);mapping[old]=obj
for old,obj in mapping.items():
    if old.parent:obj.parent=mapping[old.parent]

wood=toon('Honey oak',(.44,.225,.09));dark=toon('Dark wood',(.09,.055,.035))
cream=toon('Ivory porcelain',(.88,.76,.52));coffee=toon('Coffee',(.09,.035,.015))
olive=toon('Sage book',(.30,.40,.24));paper=toon('Paper',(.83,.76,.60))
for x in [-3.7,-.5,2.7,5.9,9.1,12.3,15.5,18.7,21.9]:
    box('Window upright',(x,0,2.35),(.09,.16,3.8),dark,window,.01)
for z in [.45,4.25]:box('Window horizontal',(9.1,0,z),(25.7,.18,.10),dark,window,.015)
box('Deep oak sill',(9.1,-.08,.42),(25.8,.45,.10),wood,window,.025)

# Physical foreground table and cup, both foreshortened by the oblique camera.
tx,ty=-1.65,-.62
cylinder('Round cafe tabletop',(tx,ty,.79),1.04,.095,wood,foreground,96)
cylinder('Table foot',(tx,ty,.39),.10,.72,dark,foreground,32)
cx,cy=tx+.20,ty+.18
lathe('Saucer',(cx,cy,.849),[(0,0),(.19,0),(.235,.025),(.225,.035),(.16,.022),(0,.022)],cream)
lathe('Cup',(cx,cy,.873),[(.082,0),(.105,.025),(.137,.18),(.137,.205),(.126,.208),(.124,.185),(.082,.015)],cream)
cylinder('Coffee surface',(cx,cy,1.066),.122,.003,coffee,foreground,64)
bpy.ops.mesh.primitive_torus_add(major_radius=.071,minor_radius=.018,major_segments=32,minor_segments=10,
                               location=(cx+.16,cy,.99),rotation=(math.pi/2,0,0))
handle=link(bpy.context.object,foreground);handle.name='VC3_Cup handle';handle.data.materials.append(cream)
box('Closed book',(tx-.37,ty-.14,.888),(.46,.32,.065),olive,foreground,.015)
box('Book pages',(tx-.37,ty-.14,.887),(.44,.315,.044),paper,foreground,.008)

# Measured 50-degree horizontal angle from the window normal (world +Y).
camdata=bpy.data.cameras.new('VC3_Camera');cam=bpy.data.objects.new('VC3_Camera',camdata);rig.objects.link(cam)
cam.location=(-5,-4.5,1.80)
direction=Vector((math.sin(math.radians(50)),math.cos(math.radians(50)),-.045)).normalized()
cam.rotation_euler=direction.to_track_quat('-Z','Y').to_euler();camdata.lens=28;camdata.sensor_width=36
camdata.clip_end=300;scene.camera=cam
angle=math.degrees(math.atan2(direction.x,direction.y));assert abs(angle-50)<1e-4

# Temporary layout geometry. It is excluded from production after image generation.
guide_sky=flat('Guide sky',(.48,.70,.84));guide_park=flat('Guide park',(.32,.53,.29))
guide_road=flat('Guide asphalt',(.23,.25,.29));guide_walk=flat('Guide sidewalk',(.69,.63,.49))
guide_line=flat('Guide road stripe',(.88,.66,.24));guide_inside=flat('Guide interior',(.65,.41,.22))
guide_wall=flat('Guide cream wall',(.81,.72,.54));guide_open=flat('Guide opening',(.18,.7,.85))
park=box('Guide park',(20,58,-.1),(260,100,.1),guide_park,guides)
road=box('Guide road',(20,6,-.045),(260,6,.05),guide_road,guides)
farwalk=box('Guide far walk',(20,10.5,-.025),(260,3,.05),guide_walk,guides)
nearwalk=box('Guide near walk',(20,1.5,-.02),(260,3,.04),guide_walk,guides)
stripe=box('Guide center line',(20,6,.005),(260,.045,.005),guide_line,guides)
floor=box('Guide indoor floor',(9,-5,-.1),(30,10,.15),guide_inside,guides)
ceiling=box('Guide ceiling',(9,-5,4.4),(30,10,.2),guide_wall,guides)
endwall=box('Guide end wall',(22,-5,2.2),(.2,10,4.4),guide_wall,guides)
lowwall=box('Guide low wall',(9,0,.18),(26,.18,.4),guide_wall,guides)
opening=box('Guide window opening',(9.1,.1,2.35),(25.7,.025,3.7),guide_open,guides)
scene.frame_set(1);bpy.context.view_layer.update()

def visibility(objs, value):
    for obj in objs:obj.hide_render=not value
visibility(list(traffic.objects)+list(leaves.objects)+list(window.objects)+list(foreground.objects),False)
visibility([floor,ceiling,endwall,lowwall,opening],False)
scene.render.film_transparent=False
scene.render.filepath=str(out/'park-layout.png');bpy.ops.render.render(write_still=True)
visibility([park,road,farwalk,nearwalk,stripe],False)
visibility([floor,ceiling,endwall,lowwall,opening],True)
visibility(list(window.objects),True)
scene.render.filepath=str(out/'cafe-layout.png');bpy.ops.render.render(write_still=True)
visibility(list(guides.objects),False)
visibility(list(traffic.objects)+list(leaves.objects)+list(window.objects)+list(foreground.objects),True)
scene.render.film_transparent=True
scene.render.filepath=str(out/'geometry-layout.png');bpy.ops.render.render(write_still=True)
scene['camera_to_window_normal_degrees']=angle
scene['workflow']='AI-generated oblique cartoon park/interior + real 3D window/table/cup and traffic'
scene['guide_images_are_not_final_assets']=True
points={}
for name,p in {'near_road_left':(-4,3,0),'far_road_left':(-4,9,0),'far_road_right':(45,9,0),
               'near_road_right':(45,3,0),'near_sill':(-3.7,0,.45),'far_sill':(21.9,0,.45),
               'near_header':(-3.7,0,4.25),'far_header':(21.9,0,4.25)}.items():
    q=world_to_camera_view(scene,cam,Vector(p));points[name]=[float(q.x),float(1-q.y)]
(out/'layout.json').write_text(json.dumps({'ok':True,'scene':scene.name,'camera':cam.name,
    'angle_degrees':angle,'objects':len(scene.objects),'projected_guide_points':points},indent=2),encoding='utf-8')
for screen in bpy.data.screens:
    for area in screen.areas:
        if area.type=='VIEW_3D':area.spaces.active.region_3d.view_perspective='CAMERA'
print('Oblique cartoon layout',angle,len(scene.objects))
