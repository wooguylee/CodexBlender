"""사용자 수정 요청: 로고의 집과 닮은 집, 그 집 앞에 서 있는 사람의 그림을 먼저 제작.

v003의 막대 그림/정자 변환은 채택하지 않는다. 기존 v002 6초 영상은 그대로 보존한다.
이 단계는 애니메이션 전 기준 그림이다. 별도 Scene과 원본으로 만든다.
"""
import json
import math
import hashlib
from mathutils import Vector

NAME='Thegachi_HousePerson_v004'
assert NAME not in bpy.data.scenes
source_house=bpy.data.objects['TG_house_d']
scene=bpy.data.scenes.new(NAME)
bpy.context.window.scene=scene
collection=bpy.data.collections.new(NAME)
scene.collection.children.link(collection)
out=PROJECT_ROOT/'outputs/thegachi-opening/v004'
out.mkdir(parents=True,exist_ok=True)


def own(obj,name):
    obj.name=name
    for col in list(obj.users_collection):
        col.objects.unlink(obj)
    collection.objects.link(obj)
    return obj


def rgb(code):
    vals=[int(code[i:i+2],16)/255 for i in (0,2,4)]
    return tuple(v/12.92 if v<=.04045 else ((v+.055)/1.055)**2.4 for v in vals)


def mat(name,code,rough=.4,metal=0):
    result=bpy.data.materials.new('HP_'+name)
    result.use_nodes=True
    p=result.node_tree.nodes['Principled BSDF']
    p.inputs['Base Color'].default_value=(*rgb(code),1)
    p.inputs['Roughness'].default_value=rough
    p.inputs['Metallic'].default_value=metal
    return result


ivory=mat('Warm_plaster','f1eadb',.78)
stone=mat('Limestone','ddd7c7',.65)
wood=mat('Oak_door','97663e',.46)
woodlight=mat('Oak_panel_light','b18554',.48)
glass=mat('Blue_glass','416277',.18,.28)
windowframe=mat('Window_frame','e3d6b5',.32,.15)
dark=mat('Dark_blue_details','102238',.42)
yellow=mat('Yellow_jacket','f9b341',.42)
pants=mat('Ochre_trousers','d69d41',.56)
skin=mat('Skin','ebbc96',.6)
hair=mat('Hair','3d2b21',.65)
leaf=mat('Foliage','507b59',.85)
leaflight=mat('Leaf_tips','779369',.85)
terracotta=mat('Planter','ad694d',.73)
ground=mat('Studio_ground','101e2d',.72)
brass=mat('Brass','dab675',.28,.65)


def cube(name,location,dimensions,material,bevel=.04):
    bpy.ops.mesh.primitive_cube_add(size=1,location=location)
    obj=own(bpy.context.object,'HP_'+name)
    obj.dimensions=dimensions
    bpy.ops.object.transform_apply(location=False,rotation=False,scale=True)
    obj.data.materials.append(material)
    if bevel:
        mod=obj.modifiers.new('Rounded_edges','BEVEL')
        mod.width=bevel
        mod.segments=3
        obj.modifiers.new('Face_normals','WEIGHTED_NORMAL')
    return obj


def ball(name,location,scale,material):
    bpy.ops.mesh.primitive_uv_sphere_add(segments=28,ring_count=16,radius=1,location=location)
    obj=own(bpy.context.object,'HP_'+name)
    obj.scale=scale
    obj.data.materials.append(material)
    for p in obj.data.polygons:
        p.use_smooth=True
    return obj


def rod(name,a,b,radius,material):
    a,b=Vector(a),Vector(b)
    bpy.ops.mesh.primitive_cylinder_add(vertices=32,radius=radius,depth=(b-a).length,location=(a+b)/2)
    obj=own(bpy.context.object,'HP_'+name)
    obj.rotation_euler=(b-a).to_track_quat('Z','Y').to_euler()
    obj.data.materials.append(material)
    bevel=obj.modifiers.new('Round_ends','BEVEL')
    bevel.width=min(radius*.65,.06)
    bevel.segments=3
    for p in obj.data.polygons:
        p.use_smooth=True
    return obj


def prism(name,points,z_front,z_back,material):
    verts=[(x,y,z) for z in (z_front,z_back) for x,y in points]
    n=len(points)
    faces=[tuple(range(n)),tuple(range(2*n-1,n-1,-1))]
    faces += [(i,(i+1)%n,(i+1)%n+n,i+n) for i in range(n)]
    mesh=bpy.data.meshes.new('HP_'+name)
    mesh.from_pydata(verts,[],faces)
    mesh.update()
    obj=bpy.data.objects.new('HP_'+name,mesh)
    collection.objects.link(obj)
    mesh.materials.append(material)
    bevel=obj.modifiers.new('Soft_corners','BEVEL')
    bevel.width=.045
    bevel.segments=3
    obj.modifiers.new('Normals','WEIGHTED_NORMAL')
    return obj


# Architectural blue frame uses the actual brand's pitched roof/left wall/base contour.
house=bpy.data.objects.new('HP_BlueHouse_LogoContour',source_house.data.copy())
collection.objects.link(house)
house.data.animation_data_clear()
house.data.extrude=.43
house.data.bevel_depth=.025
house.data.materials.clear()
blue=bpy.data.materials['TG_Blue_Gradient'].copy()
blue.name='HP_Architectural_Blue'
blue.animation_data_clear()
house.data.materials.append(blue)
house.location=(-1.,.30,-.45)
house.scale=(2.25,2.25,2.25)
house['design']='Original logo ㄷ curve used as the blue roof, left exterior frame, and foundation.'

# Recessed habitable house: pitched plaster facade, door, glazing, roof depth, steps.
prism('Plaster_house',[(-2.39,-1.25),(1.0,-1.25),(1.0,.47),(-.94,1.66),(-2.39,.69)],.38,-1.40,ivory)
cube('Door_frame',(-.66,-.35,.48),(.88,1.74,.16),windowframe,.045)
cube('Front_door',(-.66,-.37,.59),(.72,1.56,.14),wood,.035)
for x in [-.91,-.74,-.57,-.40]:
    cube('Door_oak_slats',(x,-.37,.673),(.025,1.45,.016),woodlight,.004)
rod('Door_handle',(-.41,-.42,.72),(-.41,-.13,.72),.025,brass)

# Generous window to the left of the entrance, with warm interior reflection.
cube('Window_outer',(-1.80,-.19,.49),(.85,1.18,.16),windowframe,.055)
cube('Window_glass',(-1.80,-.19,.585),(.68,1.02,.045),glass,.018)
cube('Window_vertical_bar',(-1.80,-.19,.625),(.043,1.04,.03),windowframe,.009)
cube('Window_horizontal_bar',(-1.80,-.20,.628),(.69,.042,.03),windowframe,.009)
cube('Window_sill',(-1.80,-.84,.57),(.99,.13,.30),stone,.035)
cube('Right_window_frame',(.45,-.15,.46),(.62,1.05,.12),windowframe,.04)
cube('Right_window',(.45,-.15,.54),(.48,.9,.04),glass,.018)
cube('Right_window_bar',(.45,-.15,.575),(.035,.9,.025),windowframe,.008)

# Deep blue foundation, four ascending limestone steps toward the entrance.
base_y=-2.52
cube('Landscape_plinth',(-.2,-2.73,.1),(8.6,.42,5.0),stone,.22)
for i in range(5):
    height=.22*(i+1)
    z=2.12-i*.28
    cube('Entry_step_'+str(i),(-.69,base_y+height/2,z),(1.24,height,.55),ivory,.035)
cube('Entrance_landing',(-.69,-1.38,.88),(1.27,.23,.77),ivory,.035)

# Small details reinforce this as a real house, without competing with the blue contour.
cube('Porch_light_base',(-.08,.52,.50),(.12,.24,.10),dark,.025)
bulb=mat('Porch_light','ffe0a0',.3)
p=bulb.node_tree.nodes['Principled BSDF']
p.inputs['Emission Color'].default_value=(*rgb('ffcc78'),1)
p.inputs['Emission Strength'].default_value=.7
cube('Porch_light',(-.08,.51,.57),(.095,.15,.07),bulb,.025)


def plant(name,x,z,size=1):
    bpy.ops.mesh.primitive_cone_add(vertices=40,radius1=.23*size,radius2=.31*size,depth=.47*size,location=(x,base_y+.24*size,z),rotation=(math.pi/2,0,0))
    pot=own(bpy.context.object,'HP_'+name+'_pot')
    pot.data.materials.append(terracotta)
    for j,(dx,dy,dz) in enumerate([(-.15,.55,0),(.14,.59,.06),(0,.78,-.02)]):
        ball(name+'_leaves_'+str(j),(x+dx*size,base_y+dy*size,z+dz*size),(.25*size,.28*size,.24*size),leaf if j<2 else leaflight)


plant('Left_planter',-3.18,1.08,.85)
plant('Right_planter',2.50,-.55,1.05)
for i,(x,z) in enumerate([(-2.6,1.8),(-2.25,2.05),(2.7,1.3),(3.0,.7)]):
    ball('Garden_pebble_'+str(i),(x,base_y+.035,z),(.14,.06,.10),ivory)

# A complete, clothed person standing IN FRONT of the house, overlapping its lower-right edge.
person_origin=Vector((1.20,base_y,1.60))


def at(p):
    return person_origin+Vector(p)


for side,x in [('L',-.24),('R',.24)]:
    cube('Person_shoe_'+side,at((x,.15,.09)),(.37,.25,.62),dark,.095)
    rod('Person_trouser_'+side,at((x,.35,0)),at((x*.66,1.24,0)),.165,pants)
cube('Person_hips',at((0,1.19,0)),(.64,.34,.40),pants,.13)
cube('Person_yellow_jacket',at((0,1.72,0)),(.83,1.01,.46),yellow,.17)
rod('Person_neck',at((0,2.12,0)),at((0,2.32,0)),.13,skin)
ball('Person_head',at((0,2.58,.025)),(.32,.37,.29),skin)
ball('Person_hair',at((0,2.81,-.015)),(.326,.17,.285),hair)
ball('Person_hair_back',at((0,2.67,-.16)),(.30,.29,.14),hair)
for side,sign in [('L',-1),('R',1)]:
    shoulder=(sign*.37,2.04,0)
    elbow=(sign*.58,1.70,.03)
    wrist=(sign*.67,1.41,.10)
    rod('Person_sleeve_upper_'+side,at(shoulder),at(elbow),.15,yellow)
    ball('Person_elbow_'+side,at(elbow),(.15,.15,.15),yellow)
    rod('Person_sleeve_lower_'+side,at(elbow),at(wrist),.13,yellow)
    ball('Person_hand_'+side,at((sign*.69,1.31,.12)),(.115,.15,.105),skin)
    ball('Person_eye_'+side,at((sign*.105,2.61,.286)),(.022,.026,.015),dark)
ball('Person_nose',at((0,2.52,.31)),(.048,.065,.045),skin)
smile=bpy.data.curves.new('HP_Person_smile','CURVE')
smile.dimensions='3D'
smile.bevel_depth=.012
smile.bevel_resolution=3
sp=smile.splines.new('POLY')
sp.points.add(6)
for i,p in enumerate(sp.points):
    x=-.08+i*.16/6
    p.co=(*at((x,2.42+.035*(x/.08)**2,.287)),1)
smile_obj=bpy.data.objects.new('HP_Person_smile',smile)
collection.objects.link(smile_obj)
smile.materials.append(hair)
cube('Person_jacket_zip',at((0,1.73,.242)),(.022,.74,.018),brass,.006)
for sign in [-1,1]:
    cube('Person_pocket_'+str(sign),at((sign*.23,1.50,.238)),(.19,.20,.017),pants,.03)

# Studio ground and lighting. Camera is near frontal so the ㄷ-shaped roof remains legible.
cube('Studio_floor',(0,-2.98,0),(200,.08,200),ground,.0)
scene.world=bpy.data.worlds.new('HP_World')
scene.world.use_nodes=True
scene.world.node_tree.nodes['Background'].inputs[0].default_value=(.12,.19,.30,1)
scene.world.node_tree.nodes['Background'].inputs[1].default_value=.35


def aim(obj,target):
    obj.rotation_euler=(Vector(target)-obj.location).to_track_quat('-Z','Y').to_euler()


for name,loc,energy,size,tint in [
    ('Key',(-5,8,8),1600,6,(1,.91,.79)),
    ('Fill',(7,4,6),1000,5,(.70,.84,1)),
    ('Rim',(-1,5,-6),1800,4,(.63,.78,1)),
]:
    data=bpy.data.lights.new('HP_'+name,'AREA')
    obj=bpy.data.objects.new('HP_'+name,data)
    collection.objects.link(obj)
    obj.location=loc
    data.energy,data.size,data.color=energy,size,tint
    aim(obj,(-.3,0,0))
cam=bpy.data.objects.new('HP_Camera',bpy.data.cameras.new('HP_Camera'))
collection.objects.link(cam)
cam.location=(4.0,3.2,22)
aim(cam,(-.25,.0,.15))
cam.data.type='ORTHO'
cam.data.ortho_scale=12.8
scene.camera=cam
scene.render.engine='CYCLES'
scene.cycles.device='CPU'
scene.cycles.samples=32
scene.cycles.use_denoising=True
scene.render.resolution_x,scene.render.resolution_y=1920,1080
scene.render.resolution_percentage=100
scene.render.image_settings.file_format='PNG'
scene.render.image_settings.color_mode='RGB'
scene.view_settings.view_transform='AgX'
scene.view_settings.exposure=.15
scene.frame_set(1)
scene['stage']='Reference picture first; v002 six-second video must remain unchanged.'
scene['brand_semantics']='Blue house resembles ㄷ, yellow-clothed person in front represents ㅊ.'
scene.render.filepath=str(out/'house-person-picture.png')
bpy.ops.render.render(write_still=True)
scene.render.filepath='//../outputs/thegachi-opening/v004/house-person-picture.png'
dest=PROJECT_ROOT/'scenes/thegachi-house-person-v004.blend'
assert not dest.exists()
bpy.ops.wm.save_as_mainfile(filepath=str(dest),copy=True,relative_remap=True,compress=True)
video=PROJECT_ROOT/'outputs/thegachi-opening/v002/thegachi-opening-v002.mp4'
report={'ok':True,'scene':scene.name,'stage':'reference_picture','objects':len(scene.objects),
        'picture':'house-person-picture.png','dimensions':[1920,1080],
        'legacy_video_seconds':6,'legacy_video_sha256':hashlib.sha256(video.read_bytes()).hexdigest(),
        'source':'scenes/thegachi-house-person-v004.blend',
        'new_video_rendered':False}
(out/'picture-result.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps(report,ensure_ascii=False))
