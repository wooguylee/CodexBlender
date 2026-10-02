"""브리찌 제작: 통창 카페에서 맑은 오후 3시 가을 공원, 낙엽과 불규칙 차량.
20초/480장, 1번과 480번 같은 화면. 기존 Scene과 자산은 보존한다.
외부 자산 없는 절차적 제작. 고정 배경과 움직이는 요소를 분리하여 조명 안정화.
"""
import bpy, math, random, json
from mathutils import Vector, Euler
from pathlib import Path

rng = random.Random(100215)
out = PROJECT_ROOT / 'outputs/autumn-cafe/v001'
out.mkdir(parents=True, exist_ok=True)
assert 'Autumn_Cafe_v001' not in bpy.data.scenes, 'Existing scene: use a revision script.'
prior = {s.name: len(s.objects) for s in bpy.data.scenes}
scene = bpy.data.scenes.new('Autumn_Cafe_v001')
bpy.context.window.scene = scene
scene.render.engine = 'CYCLES'
prefs = bpy.context.preferences.addons['cycles'].preferences
prefs.compute_device_type = 'OPTIX'; prefs.get_devices()
for d in prefs.devices: d.use = d.type == 'OPTIX'
scene.cycles.device = 'GPU'; scene.cycles.samples = 40
scene.cycles.use_denoising = True; scene.cycles.seed = 215
scene.cycles.use_animated_seed = False
scene.cycles.max_bounces = 6; scene.cycles.transparent_max_bounces = 8
scene.render.resolution_x = 1920; scene.render.resolution_y = 1080
scene.render.resolution_percentage = 50
scene.render.fps = 24; scene.frame_start = 1; scene.frame_end = 480
scene.render.image_settings.file_format = 'PNG'; scene.render.image_settings.color_mode = 'RGB'
scene.render.use_persistent_data = True
scene.view_settings.view_transform = 'AgX'; scene.view_settings.look = 'AgX - Medium High Contrast'
scene.view_settings.exposure = .25

def collection(n):
    c = bpy.data.collections.new('AC_' + n); scene.collection.children.link(c); return c
interior = collection('Interior')
park = collection('Park')
traffic = collection('Traffic')
weather = collection('FallingLeaves')
rig = collection('LightingCamera')
col = interior

def link(o, c=None):
    for p in list(o.users_collection): p.objects.unlink(o)
    (c or col).objects.link(o); return o
def mat(name, color, rough=.55, metal=0):
    m = bpy.data.materials.new('AC_' + name); m.use_nodes=True
    p=m.node_tree.nodes.get('Principled BSDF'); p.inputs['Base Color'].default_value=(*color,1)
    p.inputs['Roughness'].default_value=rough; p.inputs['Metallic'].default_value=metal
    return m
def noise(m, scale=30, strength=.12, grain=False):
    nt=m.node_tree; ns=nt.nodes; p=ns.get('Principled BSDF')
    t=ns.new('ShaderNodeTexNoise'); t.inputs['Scale'].default_value=scale; t.inputs['Detail'].default_value=3
    if grain:
        tex=ns.new('ShaderNodeTexCoord'); v=ns.new('ShaderNodeVectorMath'); v.operation='MULTIPLY'
        v.inputs[1].default_value=(.8,25,6); nt.links.new(tex.outputs['Generated'],v.inputs[0]);nt.links.new(v.outputs[0],t.inputs[0])
        ramp=ns.new('ShaderNodeValToRGB'); base=p.inputs['Base Color'].default_value[:]
        ramp.color_ramp.elements[0].position=.18;ramp.color_ramp.elements[0].color=tuple(x*.53 for x in base[:3])+(1,)
        ramp.color_ramp.elements[1].position=.82;ramp.color_ramp.elements[1].color=tuple(min(1,x*1.35) for x in base[:3])+(1,)
        nt.links.new(t.outputs['Fac'],ramp.inputs[0]);nt.links.new(ramp.outputs[0],p.inputs['Base Color'])
    b=ns.new('ShaderNodeBump');b.inputs['Strength'].default_value=strength;b.inputs['Distance'].default_value=.012
    nt.links.new(t.outputs['Fac'],b.inputs['Height']);nt.links.new(b.outputs[0],p.inputs['Normal']);return m
def box(name, loc, dims, m, bevel=0, c=None):
    bpy.ops.mesh.primitive_cube_add(size=1,location=loc);o=link(bpy.context.object,c);o.name='AC_'+name;o.dimensions=dims
    bpy.ops.object.transform_apply(location=False,rotation=False,scale=True)
    if m:o.data.materials.append(m)
    if bevel:
        b=o.modifiers.new('Soft edges','BEVEL');b.width=bevel;b.segments=3
        o.modifiers.new('Weighted normals','WEIGHTED_NORMAL')
    return o
def cyl(name,loc,r,depth,m,vertices=32,c=None):
    bpy.ops.mesh.primitive_cylinder_add(vertices=vertices,radius=r,depth=depth,location=loc)
    o=link(bpy.context.object,c);o.name='AC_'+name;o.data.materials.append(m)
    b=o.modifiers.new('Rounded edge','BEVEL');b.width=min(.012,depth*.12);b.segments=3
    for p in o.data.polygons:p.use_smooth=True
    return o
def sphere(name,loc,scale,m,c=None):
    bpy.ops.mesh.primitive_uv_sphere_add(segments=20,ring_count=12,radius=1,location=loc)
    o=link(bpy.context.object,c);o.name='AC_'+name;o.scale=scale;o.data.materials.append(m)
    for p in o.data.polygons:p.use_smooth=True
    return o
def line(name,pts,r,m,c=None):
    cu=bpy.data.curves.new('AC_'+name,'CURVE');cu.dimensions='3D';cu.resolution_u=1;cu.bevel_depth=r;cu.bevel_resolution=2
    sp=cu.splines.new('POLY');sp.points.add(len(pts)-1)
    for p,co in zip(sp.points,pts):p.co=(*co,1)
    o=bpy.data.objects.new('AC_'+name,cu);(c or col).objects.link(o);cu.materials.append(m);return o
def rod(name,a,b,r1,r2,m,c=None):
    a,b=Vector(a),Vector(b);d=b-a
    bpy.ops.mesh.primitive_cone_add(vertices=10,radius1=r1,radius2=r2,depth=d.length,location=(a+b)/2)
    o=link(bpy.context.object,c);o.name='AC_'+name;o.rotation_euler=d.to_track_quat('Z','Y').to_euler();o.data.materials.append(m)
    for p in o.data.polygons:p.use_smooth=True
    return o
def torus(name,loc,major,minor,m,rot=(0,0,0)):
    bpy.ops.mesh.primitive_torus_add(major_radius=major,minor_radius=minor,major_segments=48,minor_segments=12,location=loc,rotation=rot)
    o=link(bpy.context.object);o.name='AC_'+name;o.data.materials.append(m)
    for p in o.data.polygons:p.use_smooth=True
    return o
def lathe(name,loc,profile,m):
    verts=[];faces=[];n=64
    for r,z in profile:
        verts.extend((loc[0]+r*math.cos(i*math.tau/n),loc[1]+r*math.sin(i*math.tau/n),loc[2]+z) for i in range(n))
    for j in range(len(profile)-1):
        for i in range(n):a=j*n+i;b=j*n+(i+1)%n;faces.append((a,b,b+n,a+n))
    me=bpy.data.meshes.new(name);me.from_pydata(verts,[],faces);me.materials.append(m)
    o=bpy.data.objects.new('AC_'+name,me);col.objects.link(o)
    for p in me.polygons:p.use_smooth=True
    return o
def area(name,loc,target,power,color,size):
    d=bpy.data.lights.new('AC_'+name,'AREA');d.energy=power;d.color=color;d.shape='DISK';d.size=size
    o=bpy.data.objects.new('AC_'+name,d);rig.objects.link(o);o.location=loc;o.rotation_euler=(Vector(target)-o.location).to_track_quat('-Z','Y').to_euler();return o
def text(name,body,loc,size,m,rot=(0,0,0)):
    cu=bpy.data.curves.new('AC_'+name,'FONT');cu.body=body;cu.size=size;cu.align_x='CENTER';cu.extrude=.0002
    o=bpy.data.objects.new('AC_'+name,cu);col.objects.link(o);o.location=loc;o.rotation_euler=rot;cu.materials.append(m);return o
def drive(o,path,index,expr):o.driver_add(path,index).driver.expression=expr

oak=noise(mat('Honey oak',(.35,.17,.065),.39),5,.10,True)
walnut=noise(mat('Walnut',(.13,.059,.025),.4),5,.12,True)
plaster=noise(mat('Warm limewash',(.72,.62,.44),.85),75,.14)
bronze=mat('Dark bronze',(.038,.045,.033),.36,.5)
brass=mat('Aged brass',(.46,.28,.08),.28,.7)
ivory=mat('Ivory porcelain',(.83,.79,.62),.22)
fabric=noise(mat('Oat linen',(.59,.48,.32),.88),180,.22)
mossfabric=noise(mat('Olive upholstery',(.16,.20,.09),.8),130,.17)
black=mat('Rubber',(.012,.014,.013),.76)

# Warm interior and full-height picture window.
box('Floor',(0,-3,-.15),(13,10,.3),oak)
for x in range(-12,13):box('Floor join',(x*.5,-3,.003),(.008,10,.005),walnut)
for x in [-5.8,5.8]:box('Side plaster',(x,-2,2.3),(.5,7,4.6),plaster,.025)
box('Ceiling',(0,-2,4.6),(12,7,.2),plaster)
box('Low wall',(0,0,.22),(11.5,.24,.44),plaster)
box('Window oak sill',(0,-.04,.48),(11.6,.49,.11),oak,.025)
for x in [-5.5,-2.95,2.95,5.5]:
    box('Window vertical',(x,0,2.48),(.072,.115,4.05),bronze,.007)
for z in [.56,4.43]:box('Window horizontal',(0,0,z),(11.1,.115,.085),bronze,.007)
# Subtle static glazing; dynamic elements remain clear through the window.
glass=mat('Clear window',(.96,.985,1),.035)
p=glass.node_tree.nodes.get('Principled BSDF');p.inputs['Transmission Weight'].default_value=1;p.inputs['IOR'].default_value=1.45
for a,b in [(-5.46,-2.99),(-2.91,2.91),(2.99,5.46)]:
    o=box('Glazing',((a+b)/2,.035,2.48),(b-a,.008,3.79),glass)
    o['exclude_fx_holdout']=True
# Soft folded linen drapes, held to the sides.
for side in [-1,1]:
    verts=[];faces=[];nx=44;nz=28
    for j in range(nz):
        z=.55+j*3.90/(nz-1)
        for i in range(nx):
            u=i/(nx-1);x=side*(4.8+u*.70+.10*math.sin(z*1.8))
            verts.append((x,-.23+.09*math.cos(u*math.tau*7),z))
    for j in range(nz-1):
        for i in range(nx-1):a=j*nx+i;faces.append((a,a+1,a+1+nx,a+nx))
    me=bpy.data.meshes.new('Linen folds');me.from_pydata(verts,[],faces);me.materials.append(fabric)
    o=bpy.data.objects.new('AC_Linen curtain',me);interior.objects.link(o)
    for p in me.polygons:p.use_smooth=True

# Foreground table and a considered little still-life.
tx,ty=-1.18,-2.65
cyl('Round oak table',(tx,ty,.78),1.15,.095,oak,96)
cyl('Table pedestal',(tx,ty,.37),.09,.74,bronze)
cyl('Table foot',(tx,ty,.025),.48,.035,bronze,64)
cx,cy=tx+.15,ty+.27
cyl('Saucer',(cx,cy,.848),.19,.023,ivory,64)
lathe('Coffee cup',(cx,cy,.86),[(.063,0),(.078,.012),(.102,.115),(.105,.142),(.096,.147),(.091,.127),(.073,.023),(.063,.023)],ivory)
torus('Cup handle',(cx+.11,cy,.947),.044,.010,ivory,(math.pi/2,0,0))
coffee=mat('Latte crema',(.35,.16,.048),.27)
cyl('Latte surface',(cx,cy,.997),.092,.003,coffee,64)
foam=mat('Milk foam',(.9,.80,.59),.42)
for i in range(8):
    y=cy-.049+i*.012;r=.048*(1-i/10)
    pts=[(cx+math.sin(a)*r,y+math.cos(a)*.01,1.000) for a in [j*math.pi/24 for j in range(-24,25)]]
    line('Latte fern',pts,.0019,foam)
line('Latte stem',[(cx,cy-.065,1.001),(cx,cy+.059,1.001)],.002,foam)
book=box('Closed cloth book',(tx-.38,ty-.20,.86),(.51,.68,.07),mossfabric,.012)
box('Book pages',(tx-.38,ty-.20,.865),(.475,.65,.045),ivory,.005)
box('Book cover',(tx-.38,ty-.20,.893),(.51,.68,.01),mossfabric,.007)
text('Book title','S L O W\nA F T E R N O O N S',(tx-.38,ty-.28,.900),.041,ivory)
cyl('Pastry plate',(tx+.56,ty-.28,.846),.215,.014,ivory,64)
pastry=noise(mat('Golden pastry',(.59,.24,.055),.48),90,.2)
for i in range(11):
    a=-1.05+i*.21;x=tx+.56+.155*math.sin(a);y=ty-.28+.07*math.cos(a)
    o=sphere('Croissant layers',(x,y,.89),(.04*(.6+math.cos(a)*.45),.08*(.45+math.cos(a)*.55),.055*(.5+math.cos(a)*.5)),pastry)
    o.rotation_euler.z=-a*.6
# Right lounge chair, soft cushion, small side table and greenery.
box('Chair seat',(3.0,-1.65,.47),(1.25,1.14,.25),mossfabric,.15)
box('Chair back',(3.0,-1.1,.98),(1.27,.22,1.08),mossfabric,.13)
for x in [2.31,3.69]:box('Chair arm',(x,-1.64,.73),(.19,1.21,.40),walnut,.08)
for x in [2.49,3.51]:
    for y in [-2.05,-1.3]:rod('Chair leg',(x,y,.02),(x,y,.49),.03,.04,walnut)
cush=box('Linen cushion',(3,-1.40,.90),(.65,.21,.64),fabric,.10);cush.rotation_euler=(.16,.02,.12)
cyl('Side table',(4.35,-1.65,.57),.42,.06,oak,64)
terracotta=noise(mat('Terracotta',(.39,.15,.063),.75),100,.1)
green=mat('Deep green leaves',(.09,.18,.05),.45)
lathe('Large plant pot',(4.5,-.60,.02),[(.23,0),(.33,.52),(.34,.56),(.31,.56),(.29,.49)],terracotta)
for i in range(20):
    a=rng.uniform(0,math.tau);z=rng.uniform(.75,2.2);r=rng.uniform(.2,.65)
    end=(4.5+r*math.cos(a),-.60+r*math.sin(a),z)
    line('Plant stem',[(4.5,-.6,.48),end],.011,green)
    o=sphere('Indoor leaf',end,(.14,.29,.026),green);o.rotation_euler=(rng.uniform(-.5,.5),rng.uniform(-.4,.4),a)
# Warm ceiling lamps in the upper corners.
lamp=mat('Soft glowing linen',(.95,.72,.41),.65)
lp=lamp.node_tree.nodes.get('Principled BSDF');lp.inputs['Emission Color'].default_value=(1,.70,.35,1);lp.inputs['Emission Strength'].default_value=.5
for x in [-3.6,3.6]:
    line('Pendant cord',[(x,-2.0,4.5),(x,-2.0,3.25)],.009,bronze)
    lathe('Pleated pendant',(x,-2,3.15),[(.45,0),(.47,.035),(.21,.43),(.19,.44)],lamp)
    cyl('Pendant diffuser',(x,-2,3.16),.435,.012,ivory,64)
    area('Warm pendant',(x,-2,3.1),(x,-2,0),70,(1,.72,.44),.65)

# A narrow neighbourhood road between cafe and park.
col=park
concrete=noise(mat('Sandstone paving',(.47,.45,.36),.85),60,.14)
asphalt=noise(mat('Dry asphalt',(.12,.137,.14),.86),150,.19)
grass=noise(mat('Autumn lawn',(.22,.255,.073),.9),8,.23)
pathmat=noise(mat('Warm park gravel',(.49,.39,.245),.87),80,.19)
box('Pavement cafe',(0,1.65,-.03),(160,3.3,.15),concrete)
box('Narrow two way road',(0,6,-.15),(170,5.2,.16),asphalt)
box('Park sidewalk',(0,9.3,-.005),(160,1.5,.18),concrete)
for y in [3.27,8.7]:
    for x in range(-35,36):box('Curb',(x,y,.02),(.987,.19,.25),concrete,.012)
mark=mat('Faded center paint',(.67,.61,.37),.85)
for x in range(-80,81,5):box('Road center dash',(x,6,-.062),(2.0,.065,.005),mark)
for x in range(-35,36,2):box('Paving joint',(x,1.5,.052),(.009,3.0,.002),walnut)
box('Park lawn',(0,34,-.16),(170,48,.2),grass)
box('Park front path',(0,11.4,-.038),(150,2.15,.035),pathmat)
box('Park long walk',(2.2,31,-.015),(2.25,40,.07),pathmat)
box('Park crossing walk',(0,24,-.02),(100,2.0,.06),pathmat)
bark=noise(mat('Textured tree bark',(.115,.072,.034),.9),13,.36)
leafm=[]
for name,color in [('Amber',(.68,.245,.022)),('Gold',(.83,.49,.045)),('Ochre',(.5,.25,.022)),('Rust',(.45,.081,.022)),('Scarlet',(.47,.045,.023)),('Lime gold',(.52,.44,.065)),('Burnished',(.69,.16,.025))]:
    m=mat('Leaf '+name,color,.69);p=m.node_tree.nodes.get('Principled BSDF');p.inputs['Subsurface Weight'].default_value=.045;leafm.append(m)
leafoutline=[(0,-.55),(-.16,-.27),(-.48,-.28),(-.34,-.05),(-.72,.02),(-.42,.21),(-.5,.47),(-.21,.34),(0,.83),(.21,.34),(.5,.47),(.42,.21),(.72,.02),(.34,-.05),(.48,-.28),(.16,-.27)]
def add_leaf(vs,fs,mi,center,size,rot,matid):
    base=len(vs);q=Euler(rot).to_matrix();c=Vector(center)
    vs.append(tuple(c+q@Vector((0,0,.05*size))))
    for x,y in leafoutline:vs.append(tuple(c+q@Vector((x*size,y*size,0))))
    for j in range(16):fs.append((base,base+1+j,base+1+(j+1)%16));mi.append(matid)
def leafmesh(name,vs,fs,mi,c):
    me=bpy.data.meshes.new(name);me.from_pydata(vs,[],fs)
    for m in leafm:me.materials.append(m)
    for p,i in zip(me.polygons,mi):p.material_index=i
    o=bpy.data.objects.new('AC_'+name,me);c.objects.link(o);return o
def tree(x,y,h,spread,palette,idx):
    lean=rng.uniform(-.35,.35);root=Vector((x,y,-.03));top=Vector((x+lean,y+.12,h*.67))
    rod('Tree trunk',root,top,h*.037,.065,bark)
    clusters=[]
    for j in range(10):
        a=j*2.399+rng.uniform(-.25,.25);r=spread*rng.uniform(.35,.9)
        z=h*rng.uniform(.57,.88);tip=Vector((x+math.cos(a)*r,y+math.sin(a)*r,z))
        base=Vector((x+lean*.4,y,h*rng.uniform(.29,.53)))
        mid=base.lerp(tip,.58);mid.z-=.15
        rod('Tree branch',base,mid,.073,.035,bark);rod('Tree twig',mid,tip,.035,.008,bark)
        clusters.append((tip,rng.uniform(.7,1.2)))
        for k in range(2):
            tt=tip+Vector((rng.uniform(-.75,.75),rng.uniform(-.75,.75),rng.uniform(-.3,.8)))
            rod('Fine branch',mid,tt,.014,.003,bark)
    clusters.append((Vector((x,y,h*.89)),1.0))
    vs=[];fs=[];mi=[]
    for center,fac in clusters:
        for k in range(260):
            a=rng.random()*math.tau;zz=rng.uniform(-1,1);r=rng.random()**(1/3);ss=math.sqrt(1-zz*zz)
            pos=center+Vector((math.cos(a)*ss*r*spread*.62*fac,math.sin(a)*ss*r*spread*.54*fac,zz*r*h*.16*fac))
            add_leaf(vs,fs,mi,pos,rng.uniform(.12,.22),[rng.uniform(-1.5,1.5),rng.uniform(-1.4,1.4),rng.random()*math.tau],rng.choice(palette))
    leafmesh('Tree canopy %02d'%idx,vs,fs,mi,park)
tree_specs=[(-10,15,8.2,3.2,[0,3,4]),(-5.6,17,9.2,3.5,[0,1,2]),(.0,17,8.3,3.4,[0,1,5]),(7,16.2,9.2,3.6,[3,4,6]),(13,18,9.4,3.6,[0,1,2]),(-18,18,10,4,[3,4,6])]
for y in [27,38,49]:
    for x in range(-33,36,8):tree_specs.append((x+rng.uniform(-2,2),y+rng.uniform(-2,2),rng.uniform(8,12),rng.uniform(3.4,4.7),rng.choice([[0,1,2],[3,4,6],[1,2,5]])))
for i,spec in enumerate(tree_specs):tree(*spec,i)
# Loose leaves on paths and pavement, individually modeled and merged.
vs=[];fs=[];mi=[]
for i in range(1600):
    x=rng.uniform(-27,27);y=rng.choice([rng.uniform(8.9,16),rng.uniform(1,3)])
    add_leaf(vs,fs,mi,(x,y,.095 if y<3 else .10),rng.uniform(.055,.13),(0,0,rng.random()*math.tau),rng.randrange(len(leafm)))
leafmesh('Fallen leaf carpet',vs,fs,mi,park)
# Benches and slender traditional park lamps.
for bx,by in [(-5,13.5),(8.6,13.5),(-8,25.5),(9,26)]:
    for k in range(5):box('Bench seat slat',(bx,by+k*.10,.48),(2.0,.084,.047),walnut,.008)
    for k in range(4):box('Bench back slat',(bx,by+.48,.69+k*.12),(2.0,.047,.084),walnut,.007)
    for xx in [bx-.74,bx+.74]:
        rod('Bench leg',(xx,by+.06,.04),(xx,by+.1,.51),.034,.034,bronze)
        rod('Bench upright',(xx,by+.48,.04),(xx,by+.48,1.14),.028,.028,bronze)
for x,y in [(-11,11.5),(11,11.5),(-10,25),(12,25)]:
    cyl('Park lamp post',(x,y,1.55),.043,3.1,bronze,16)
    cyl('Park lamp foot',(x,y,.14),.13,.28,bronze,24)
    sphere('Park opal globe',(x,y,3.21),(.19,.19,.25),ivory)
    lathe('Park lamp cap',(x,y,3.35),[(.23,0),(.14,.13),(.03,.18)],bronze)

# Six distinct simple cars, two lanes, with reproducible irregular arrival offsets.
col=traffic
car_glass=mat('Car dark glazing',(.042,.075,.093),.16,.48)
chrome=mat('Car chrome',(.39,.42,.4),.25,.8)
head=mat('Car headlamp lens',(.79,.83,.68),.19,.18)
tail=mat('Car taillamp',(.37,.012,.006),.22)
colors=[(.48,.105,.04),(.16,.26,.20),(.68,.64,.49),(.14,.21,.3),(.38,.065,.045),(.72,.49,.13)]
schedule=[]
for i,(phase,lane,direction) in enumerate([(0.05,4.65,1),(.33,4.65,1),(.69,4.65,1),(.13,7.35,-1),(.47,7.35,-1),(.84,7.35,-1)]):
    start=set(traffic.objects)
    paint=mat('Car paint %d'%i,colors[i],.26,.28)
    length=[3.9,4.35,3.7,4.1,4.0,3.65][i];h=[1.30,1.47,1.29,1.34,1.28,1.42][i]
    body=box('Car body %d'%i,(0,0,.53),(length,1.62,.65),paint,.18)
    box('Car lower sill',(0,0,.28),(length-.1,1.64,.19),black,.06)
    # Trapezoid glazed cabin with sloping windshield and rear hatch.
    x1,x2=-1.25,.87;zt=h-.14
    vs=[(x1,-.73,.79),(x2,-.73,.79),(x2,.73,.79),(x1,.73,.79),(-.83,-.63,zt),(.40,-.63,zt),(.40,.63,zt),(-.83,.63,zt)]
    fs=[(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7),(4,5,6,7)]
    me=bpy.data.meshes.new('Car cabin');me.from_pydata(vs,[],fs);me.materials.append(car_glass)
    o=bpy.data.objects.new('AC_Car glazed cabin',me);traffic.objects.link(o)
    box('Car roof',(-.21,0,zt+.045),(1.27,1.32,.105),paint,.055)
    for y in [-.736,.736]:
        rod('Car A pillar',(.87,y,.79),(.40,y*.86,zt),.027,.025,paint)
        rod('Car C pillar',(-1.25,y,.79),(-.83,y*.86,zt),.045,.036,paint)
        rod('Car B pillar',(-.24,y,.80),(-.24,y*.86,zt),.026,.027,paint)
        box('Door handle',(-.34,y*1.09,.68),(.16,.025,.024),chrome,.008)
        box('Wing mirror',(.61,y*1.15,.91),(.19,.15,.10),paint,.04)
    for x in [-length*.31,length*.31]:
        for y in [-.78,.78]:
            o=cyl('Car tyre',(x,y,.29),.29,.17,black,32);o.rotation_euler.x=math.pi/2
            o=cyl('Alloy wheel',(x,y+math.copysign(.092,y),.29),.177,.02,chrome,24);o.rotation_euler.x=math.pi/2
            o=cyl('Wheel center',(x,y+math.copysign(.105,y),.29),.060,.025,bronze,16);o.rotation_euler.x=math.pi/2
    for y in [-.55,.55]:
        box('Headlight',(length/2-.025,y,.59),(.025,.28,.15),head,.035)
        box('Taillight',(-length/2+.022,y,.59),(.025,.26,.12),tail,.025)
    box('Front grille',(length/2-.025,0,.38),(.025,.73,.17),bronze,.025)
    box('Number plate',(length/2+.001,0,.46),(.025,.33,.07),ivory,.009)
    # Soft contact shadow, with broad penumbra rings, stable across frames.
    for k in range(5):
        m=bpy.data.materials.new('AC_Contact shadow');m.use_nodes=True;ns=m.node_tree.nodes;ns.clear()
        tr=ns.new('ShaderNodeBsdfTransparent');em=ns.new('ShaderNodeEmission');em.inputs[0].default_value=(.013,.018,.02,1)
        mix=ns.new('ShaderNodeMixShader');mix.inputs[0].default_value=.09;op=ns.new('ShaderNodeOutputMaterial')
        m.node_tree.links.new(tr.outputs[0],mix.inputs[1]);m.node_tree.links.new(em.outputs[0],mix.inputs[2]);m.node_tree.links.new(mix.outputs[0],op.inputs[0])
        sh=cyl('Car contact shadow',(-.18,.10,-.049+k*.001),1,.0002,m,64);sh.scale=(length*.5+.23-k*.04,.95-k*.04,1)
        sh.visible_shadow=False
    root=bpy.data.objects.new('AC_Traffic motion %d'%i,None);traffic.objects.link(root)
    for o in set(traffic.objects)-start-{root}:o.parent=root
    root.location.y=lane;root.rotation_euler.z=0 if direction==1 else math.pi
    span=150 if direction==1 else 171
    expr=f'{direction}*{span}*((((frame-1)/479+{phase})%1)-0.5)'
    drive(root,'location',0,expr)
    schedule.append({'car':root.name,'phase':phase,'lane':lane,'direction':direction,'speed_m_s':span/(479/24)})

# Individual maple leaves tumble and drift, resetting above and below the visible area.
for i in range(56):
    vs=[];fs=[];mi=[];size=rng.uniform(.080,.16)
    add_leaf(vs,fs,mi,(0,0,0),size,(0,0,0),rng.randrange(len(leafm)))
    o=leafmesh('Airborne maple %02d'%i,vs,fs,mi,weather)
    phase=rng.random();x=rng.uniform(-20,20);y=rng.uniform(9.6,15.5);period=rng.choice([1,2])
    u=f'(((frame-1)/479*{period}+{phase})%1)'
    drive(o,'location',0,f'{x}+1.1*sin(6.28318530718*{u}+{i})+1.6*{u}')
    drive(o,'location',1,f'{y}+.32*sin(12.56637061436*{u}+{i})')
    drive(o,'location',2,f'10.7-11.3*{u}')
    drive(o,'rotation_euler',0,f'.6*sin(25.13274122872*{u}+{i})')
    drive(o,'rotation_euler',1,f'12.56637061436*{u}+{i}')
    drive(o,'rotation_euler',2,f'6.28318530718*{u}+{i}')

# Clear mid-afternoon sky and warm angled sunlight, constant throughout the shot.
world=bpy.data.worlds.new('AC_Clear afternoon sky');world.use_nodes=True;scene.world=world
nt=world.node_tree;sky=nt.nodes.new('ShaderNodeTexSky');sky.sky_type='SINGLE_SCATTERING'
sky.sun_elevation=math.radians(34);sky.sun_rotation=math.radians(225);sky.altitude=.1;sky.air_density=1.0;sky.aerosol_density=1.0
sky.sun_intensity=.8;nt.links.new(sky.outputs['Color'],nt.nodes['Background'].inputs['Color']);nt.nodes['Background'].inputs['Strength'].default_value=.35
area('Window soft bounce',(0,-.3,3.7),(0,-3,1),220,(1,.87,.68),6)
area('Interior warm fill',(0,-5,3.6),(0,0,1.3),130,(1,.81,.6),5)
d=bpy.data.cameras.new('AC_Camera');cam=bpy.data.objects.new('AC_Camera',d);rig.objects.link(cam)
cam.location=(0,-6.4,1.83);target=Vector((0,14,2.65));cam.rotation_euler=(target-cam.location).to_track_quat('-Z','Y').to_euler()
d.lens=25;d.sensor_width=36;d.clip_end=250;scene.camera=cam
scene.frame_set(1)
for screen in bpy.data.screens:
    for a in screen.areas:
        if a.type=='VIEW_3D':a.spaces.active.region_3d.view_perspective='CAMERA'
scene['request']='코지한 카페 통창, 가을 공원, 좁은 도로와 불규칙 차량, 맑은 오후 3시, 20초 첫/마지막 동일'
scene['loop_endpoint']=480;scene['loop_period_frames']=479
(out/'build-report.json').write_text(json.dumps({'ok':True,'scene':scene.name,'camera':cam.name,'objects':len(scene.objects),'preserved_scenes':prior,'trees':len(tree_specs),'falling_leaves':56,'traffic':schedule,'external_assets':False},indent=2),encoding='utf-8')
print('Autumn cafe scene built',len(scene.objects),'objects')
