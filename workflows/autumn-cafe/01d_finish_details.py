"""카페 펜던트와 작은 화병, 공원 뒤 관목층을 추가하여 공간의 깊이를 마무리."""
import bpy,math,random
scene=bpy.context.scene;assert scene.name=='Autumn_Cafe_v001';rng=random.Random(603)
park=bpy.data.collections['AC_Park'];interior=bpy.data.collections['AC_Interior']
def sphere(n,loc,scale,mat,col):
    bpy.ops.mesh.primitive_uv_sphere_add(segments=16,ring_count=8,radius=1,location=loc)
    o=bpy.context.object
    for c in list(o.users_collection):c.objects.unlink(o)
    col.objects.link(o);o.name='AC_'+n;o.scale=scale;o.data.materials.append(mat)
    for p in o.data.polygons:p.use_smooth=True
    return o
def line(n,pts,r,mat):
    c=bpy.data.curves.new(n,'CURVE');c.dimensions='3D';c.bevel_depth=r;c.bevel_resolution=2
    sp=c.splines.new('POLY');sp.points.add(len(pts)-1)
    for p,co in zip(sp.points,pts):p.co=(*co,1)
    o=bpy.data.objects.new('AC_'+n,c);interior.objects.link(o);c.materials.append(mat)
for o in list(interior.objects):
    if any(s in o.name for s in ['Pleated pendant','Pendant diffuser','Pendant cord']):
        # Curves and lathed meshes were created with world-space vertices.
        if o.type=='CURVE':
            for sp in o.data.splines:
                for p in sp.points:
                    p.co.x-=math.copysign(.65,p.co.x);p.co.z-=.24
        elif 'Pleated' in o.name:
            for v in o.data.vertices:v.co.x-=math.copysign(.65,v.co.x);v.co.z-=.24
        else:o.location.x-=math.copysign(.65,o.location.x);o.location.z-=.24
# Park depth: broad low shrubs among the last row of trees.
for j in range(40):
    x=-66+j*3.4;y=53+rng.uniform(-2,2)
    sphere('Far woodland understory',(x,y,1.65),(rng.uniform(2,3),2.6,rng.uniform(1.6,2.8)),bpy.data.materials[rng.choice(['AC_Leaf Ochre','AC_Leaf Lime gold','AC_Deep green leaves'])],park)
# Dried foliage in a tiny stoneware vase, kept to the side of the cup.
vase=bpy.data.materials['AC_Terracotta'];stem=bpy.data.materials['AC_Walnut'];leaf=bpy.data.materials['AC_Leaf Gold']
vx,vy=-1.87,-2.33
sphere('Small stoneware vase',(vx,vy,.925),(.082,.078,.12),vase,interior)
for i in range(5):
    a=i*2.4;end=(vx+.13*math.cos(a),vy+.12*math.sin(a),1.27+rng.uniform(-.05,.1))
    line('Dried flower stem',[(vx,vy,.99),end],.003,stem)
    for k in range(4):
        z=end[2]-.07+k*.025
        sphere('Dried seed head',(end[0]+.013*math.cos(k*2),end[1]+.013*math.sin(k*2),z),(.021,.015,.025),leaf,interior)
scene.frame_set(120)
print('Foreground details and distant woodland added')
