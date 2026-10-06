"""Compact skinned character geometry. All coordinates are baked; no external assets."""
import math
import bpy,bmesh
from mathutils import Vector,Matrix,Euler

def rgb(value):
    values=[int(value[i:i+2],16)/255 for i in (0,2,4)]
    return tuple(v/12.92 if v<=.04045 else ((v+.055)/1.055)**2.4 for v in values)+(1.,)

def smooth(a,b,x):
    t=max(0.,min(1.,(x-a)/(b-a)));return t*t*(3-2*t)

class Part:
    def __init__(self,name,verts,faces,material,bone):
        self.name=name;self.verts=[Vector(v) for v in verts];self.faces=faces;self.material=material;self.bone=bone;self.shapes={};self.weights=None

class Builder:
    def __init__(self,key,scene):
        self.key=key;self.scene=scene;self.parts=[];self.materials={};self.extras=[]
        self.arms={s:[Vector(p) for p in [(sign*.57,0,1.25),(sign*.77,-.06,1.03),(sign*.87,-.13,.84)]] for s,sign in [('L',-1),('R',1)]}
        self.legs={s:[Vector(p) for p in [(sign*.25,0,.68),(sign*.25,-.08,.44),(sign*.25,0,.18)]] for s,sign in [('L',-1),('R',1)]}

    def mat(self,name,hex_color,roughness=.48,metallic=0):
        if name in self.materials:return name
        fullname='SC_'+self.key+'_'+name;m=bpy.data.materials.get(fullname) or bpy.data.materials.new(fullname);m.use_nodes=True
        color=rgb(hex_color);m.diffuse_color=color;p=m.node_tree.nodes.get('Principled BSDF')
        p.inputs['Base Color'].default_value=color;p.inputs['Roughness'].default_value=roughness;p.inputs['Metallic'].default_value=metallic
        self.materials[name]=m;return name

    def mesh(self,name,vertices,faces,material,bone='DEF_Head'):
        assert material in self.materials,(self.key,material)
        p=Part(name,vertices,[tuple(f) for f in faces],material,bone);self.parts.append(p);return p

    def from_bmesh(self,name,bm,center,scale,material,bone,rotation):
        rot=Euler(rotation).to_matrix();offset=Vector(center)
        bm.verts.ensure_lookup_table();bm.verts.index_update()
        verts=[rot@Vector(tuple(v.co[i]*scale[i] for i in range(3)))+offset for v in bm.verts]
        faces=[tuple(v.index for v in f.verts) for f in bm.faces];bm.free()
        return self.mesh(name,verts,faces,material,bone)

    def ell(self,name,center,scale,material,bone='DEF_Head',rotation=(0,0,0),segments=20,rings=12):
        bm=bmesh.new();bmesh.ops.create_uvsphere(bm,u_segments=segments,v_segments=rings,radius=1.)
        return self.from_bmesh(name,bm,center,scale,material,bone,rotation)

    def box(self,name,center,size,material,bone='DEF_Head',bevel=.08,rotation=(0,0,0)):
        bm=bmesh.new();bmesh.ops.create_cube(bm,size=1.)
        for v in bm.verts:v.co=Vector(tuple(v.co[i]*size[i] for i in range(3)))
        bm.normal_update()
        if bevel:bmesh.ops.bevel(bm,geom=list(bm.edges),offset=min(bevel,min(size)*.45),segments=3,profile=.5,affect='EDGES')
        return self.from_bmesh(name,bm,center,(1,1,1),material,bone,rotation)

    def tube(self,name,points,radius,material,bone='DEF_Head',chain=None,sides=10):
        points=list(map(Vector,points));radii=[radius]*len(points) if isinstance(radius,(int,float)) else list(radius)
        assert len(points)==len(radii) and len(points)>=2
        samples=[];sizes=[]
        for i in range(len(points)-1):
            p0=points[max(i-1,0)];p1=points[i];p2=points[i+1];p3=points[min(i+2,len(points)-1)]
            for j in range(5):
                t=j/5;point=.5*((2*p1)+(-p0+p2)*t+(2*p0-5*p1+4*p2-p3)*t*t+(-p0+3*p1-3*p2+p3)*t*t*t)
                samples.append(point);sizes.append(radii[i]*(1-t)+radii[i+1]*t)
        samples.append(points[-1]);sizes.append(radii[-1]);verts=[];faces=[]
        previous_tangent=None;normal=None
        for i,(p,r) in enumerate(zip(samples,sizes)):
            tangent=samples[min(i+1,len(samples)-1)]-samples[max(i-1,0)]
            if tangent.length<1e-8:tangent=Vector((0,0,1))
            tangent.normalize()
            if normal is None:
                seed=min((Vector((1,0,0)),Vector((0,1,0)),Vector((0,0,1))),key=lambda axis:abs(axis.dot(tangent)))
                normal=(seed-tangent*seed.dot(tangent)).normalized()
            else:normal=previous_tangent.rotation_difference(tangent)@normal
            normal=(normal-tangent*normal.dot(tangent)).normalized();cross=tangent.cross(normal);previous_tangent=tangent.copy()
            verts.extend(p+r*(normal*math.cos(j*math.tau/sides)+cross*math.sin(j*math.tau/sides)) for j in range(sides))
        for i in range(len(samples)-1):
            for j in range(sides):faces.append((i*sides+j,(i+1)*sides+j,(i+1)*sides+(j+1)%sides,i*sides+(j+1)%sides))
        verts.extend([samples[0],samples[-1]])
        for j in range(sides):
            faces.append((len(verts)-2,(j+1)%sides,j));start=(len(samples)-1)*sides;faces.append((len(verts)-1,start+j,start+(j+1)%sides))
        part=self.mesh(name,verts,faces,material,bone)
        if chain:
            chain=list(chain)
            def weights(co):
                best=(float('inf'),0.)
                for i,(a,c) in enumerate(zip(points,points[1:])):
                    d=c-a;t=max(0.,min(1.,(co-a).dot(d)/max(d.length_squared,1e-12)));dist=(co-(a+d*t)).length_squared
                    if dist<best[0]:best=(dist,(i+t)/(len(points)-1))
                position=best[1]*len(chain)-.5;lo=math.floor(position);mix=position-lo
                if lo<0:return {chain[0]:1.}
                if lo>=len(chain)-1:return {chain[-1]:1.}
                return {chain[lo]:1-mix,chain[lo+1]:mix}
            part.weights=weights
        return part

    def cone(self,name,start,end,radius,material,bone='DEF_Head',radius_end=.01,sides=16):
        return self.tube(name,[start,end],[radius,radius_end],material,bone,sides=sides)

    def ring(self,name,center,major,minor,material,bone='DEF_Head',rotation=(0,0,0)):
        rot=Euler(rotation).to_matrix();c=Vector(center);verts=[];faces=[];n=32;m=8
        for i in range(n):
            a=math.tau*i/n
            for j in range(m):
                b=math.tau*j/m;verts.append(c+rot@Vector(((major+minor*math.cos(b))*math.sin(a),minor*math.sin(b),(major+minor*math.cos(b))*math.cos(a))))
        for i in range(n):
            for j in range(m):faces.append((i*m+j,((i+1)%n)*m+j,((i+1)%n)*m+(j+1)%m,i*m+(j+1)%m))
        return self.mesh(name,verts,faces,material,bone)

    def star(self,name,center,radius,depth,material,bone='DEF_Head',points=5,rotation=(0,0,0)):
        verts=[];faces=[];n=points*2
        for y in (-depth*.5,depth*.5):
            for i in range(n):
                r=radius*(1 if i%2==0 else .5);a=math.tau*i/n;verts.append((r*math.sin(a),y,r*math.cos(a)))
        faces.extend([tuple(range(n)),tuple(reversed(range(n,n*2)))])
        faces.extend((i,(i+1)%n,(i+1)%n+n,i+n) for i in range(n))
        bm=bmesh.new();vs=[bm.verts.new(v) for v in verts]
        for f in faces:bm.faces.new([vs[i] for i in f])
        bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.normal_update()
        bmesh.ops.bevel(bm,geom=list(bm.edges),offset=min(depth*.18,radius*.07),segments=2,profile=.5,affect='EDGES')
        bmesh.ops.triangulate(bm,faces=[f for f in bm.faces if len(f.verts)>4])
        return self.from_bmesh(name,bm,center,(1,1,1),material,bone,rotation)

    def extra(self,name,head,tail,parent='DEF_Head'):
        label='DEF_'+name;assert not any(e['name']==label for e in self.extras)
        self.extras.append({'name':label,'head':list(head),'tail':list(tail),'parent':parent});return label

    def chain(self,name,points,parent='DEF_Body'):
        names=[]
        for i,(a,c) in enumerate(zip(points,points[1:])):
            label=self.extra(name+str(i),a,c,parent);names.append(label);parent=label
        return names

    def limbs(self,skin,shoe=None,hand=None,style='standard',radius=.105,omit_legs=False,omit_arms=False):
        shoe=shoe or skin;hand=hand or skin
        for side in ('L','R'):
            a=self.arms[side];p=self.legs[side]
            if not omit_arms:
                self.tube('Arm'+side,a,radius,skin,chain=['DEF_UpperArm.'+side,'DEF_Forearm.'+side])
                size=(.16,.105,.22) if style=='fins' else (.155,.135,.155)
                self.ell('Hand'+side,a[-1],size,hand,'DEF_Hand.'+side,segments=16,rings=10)
            if not omit_legs:
                self.tube('Leg'+side,p,radius,skin,chain=['DEF_Thigh.'+side,'DEF_Shin.'+side])
                self.ell('Foot'+side,(p[-1].x,-.08,.13),(.18,.25,.13),shoe,'DEF_Foot.'+side,segments=16,rings=10)

    def face(self,center=(0,-.55,1.75),spread=.22,scale=1.,eye_color=None,blush=True):
        dark=eye_color or self.mat('FaceInk','343042',.5);white=self.mat('FaceLight','FFF7E9',.5);pink=self.mat('FaceBlush','EFADB4',.65)
        c=Vector(center)
        for sign in (-1,1):
            eye=c+Vector((sign*spread,0,0));p=self.ell('Eye'+str(sign),eye,(.055*scale,.035*scale,.09*scale),dark,segments=16,rings=10)
            p.shapes['Blink']=[Vector((v.x,v.y,eye.z+(v.z-eye.z)*.09)) for v in p.verts]
            highlight=eye+Vector((-.013*scale,-.031*scale,.033*scale));p=self.ell('Glint'+str(sign),highlight,(.017*scale,.011*scale,.023*scale),white,segments=12,rings=8)
            p.shapes['Blink']=[eye+(v-eye)*.001 for v in p.verts]
            if blush:self.ell('Blush'+str(sign),c+Vector((sign*(spread+.14*scale),.015,-.105*scale)),(.10*scale,.027*scale,.046*scale),pink,segments=16,rings=8)
        mouth=c+Vector((0,-.015,-.19*scale))
        p=self.tube('Smile',[mouth+Vector((-.11*scale,0,.025*scale)),mouth+Vector((0,-.008,-.03*scale)),mouth+Vector((.11*scale,0,.025*scale))],.015*scale,dark,sides=8)
        p.shapes['Smile']=[mouth+Vector(((v.x-mouth.x)*1.35,v.y-mouth.y,(v.z-mouth.z)*1.6)) for v in p.verts]
        p.shapes['Surprise']=[mouth+(v-mouth)*.001 for v in p.verts]
        p=self.ell('SurprisedMouth',mouth,(.058*scale,.024*scale,.076*scale),dark,segments=16,rings=10)
        full=[v.copy() for v in p.verts];p.verts=[mouth+(v-mouth)*.001 for v in p.verts];p.shapes['Surprise']=full

    def combine(self,collection):
        verts=[];faces=[];materials=[];weights=[];shape_names=sorted({n for p in self.parts for n in p.shapes});shapes={n:[] for n in shape_names}
        mats=list(self.materials)
        for part in self.parts:
            offset=len(verts);verts.extend(part.verts);faces.extend(tuple(i+offset for i in f) for f in part.faces);materials.extend([mats.index(part.material)]*len(part.faces))
            weights.extend([part.weights(v) if part.weights else {part.bone:1.} for v in part.verts])
            for name in shape_names:shapes[name].extend(part.shapes.get(name,part.verts))
        data=bpy.data.meshes.new(self.key+'_Mesh');data.from_pydata(verts,[],faces);data.update()
        for name in mats:data.materials.append(self.materials[name])
        for poly,index in zip(data.polygons,materials):poly.material_index=index;poly.use_smooth=True
        obj=bpy.data.objects.new(self.key+'_Skin',data);collection.objects.link(obj)
        groups={name:obj.vertex_groups.new(name=name) for name in sorted({n for w in weights for n in w})}
        for i,weight in enumerate(weights):
            total=sum(weight.values());assert abs(total-1)<1e-5
            for name,value in weight.items():
                if value>1e-7:groups[name].add([i],value,'REPLACE')
        obj.shape_key_add(name='Basis')
        for name,coords in shapes.items():
            key=obj.shape_key_add(name=name)
            for v,co in zip(key.data,coords):v.co=co
        return obj
