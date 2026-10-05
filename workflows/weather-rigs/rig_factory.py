"""기존 날씨 요정 디자인을 독립 복제하여 실제 뼈대, IK, 스키닝, 표정 driver를 만든다."""
import math,sys
from pathlib import Path
import bpy,bmesh
from mathutils import Vector,Matrix
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'weather-shorts'))
from production import Production,KEYS,rgb,smooth

PREFIX='WR1_'
NAMES={'Mongsil':'몽실','Haerong':'해롱','Ttorr':'또르','Songsong':'송송','Solsol':'솔솔'}
ARMS={
 'Mongsil':[[(-.87,-.22,1.62),(-.70,-.48,1.47),(-.42,-.72,1.30)],[(.90,-.19,1.66),(.71,-.46,1.47),(.43,-.71,1.31)]],
 'Haerong':[[(-.88,-.025,1.87),(-1.03,-.15,1.69),(-1.05,-.24,1.46)],[(.84,-.015,1.9),(1.23,-.05,2.07),(1.49,-.07,2.52)]],
 'Ttorr':[[(-.66,-.06,1.35),(-.63,-.46,1.21),(-.16,-.666,1.22)],[(.67,-.07,1.37),(.59,-.47,1.22),(.12,-.679,1.23)]],
 'Songsong':[[(-.55,-.02,1.72),(-.87,-.11,1.54),(-1.03,-.18,1.76)],[(.56,-.015,1.70),(.86,-.16,1.40),(1,-.22,1.50)]],
 'Solsol':[[(-.54,-.02,1.64),(-.88,-.17,1.54),(-1.04,-.23,1.78)],[(.53,-.04,1.65),(.75,-.25,1.50),(.86,-.30,1.75)]]}
LEGS={
 'Mongsil':[[(-.38,-.02,1.19),(-.38,-.16,1.015),(-.38,-.11,.84)],[(.38,-.02,1.19),(.38,-.16,1.015),(.38,-.11,.84)]],
 'Haerong':[[(-.36,0,1.13),(-.375,-.13,.89),(-.425,-.06,.66)],[(.36,0,1.13),(.375,-.13,.89),(.425,-.06,.66)]],
 'Ttorr':[[(-.26,.025,.94),(-.26,-.11,.79),(-.26,-.025,.64)],[(.26,.025,.94),(.26,-.11,.79),(.26,-.025,.64)]],
 'Songsong':[[(-.26,0,1.41),(-.28,-.13,1.05),(-.307,-.04,.69)],[(.26,0,1.41),(.28,-.13,1.05),(.307,-.04,.69)]],
 'Solsol':[[(-.22,.04,1.12),(-.31,-.12,.88),(-.34,-.05,.65)],[(.23,.04,1.09),(.47,.045,.88),(.61,-.015,1.06)]]}


class Stage(Production):
    def __init__(self,root):
        self.root=root;self.prefix=PREFIX;self.name='Weather_Rigs_v001';self.duration=16;self.title='날씨 요정 맞춤 리깅'
        assert self.name not in bpy.data.scenes
        self.scene=bpy.data.scenes.new(self.name);bpy.context.window.scene=self.scene
        self.collection=bpy.data.collections.new(PREFIX+'Stage');self.scene.collection.children.link(self.collection)
        self.materials={};self.objects={};self.dynamic=set();self.base={}
        self.material('floor','E9E3ED',emission=True);self.material('shadow','D1C8D7',emission=True)
        self.ball('Floor',(0,0,-.30),(200,200,.58),'floor')
        self.shadows={k:self.ball(k+'_GroundShadow',((i-2)*3,0,.286),(.72,.42,.004),'shadow') for i,k in enumerate(KEYS)}
        self.setup_camera();self.setup_lighting();self.scene.camera.data.ortho_scale=18.2
        self.scene['purpose']='Reusable custom armatures, IK controls, facial shape keys and weather-specific controls.'
        self.rigs={}


def drive(owner,path,index,rig,variables,expression):
    curve=owner.driver_add(path) if index is None else owner.driver_add(path,index)
    driver=curve.driver;driver.type='SCRIPTED';driver.expression=expression
    for name,(bone,prop) in variables.items():
        var=driver.variables.new();var.name=name;var.type='SINGLE_PROP'
        var.targets[0].id=rig;var.targets[0].data_path=f'pose.bones["{bone}"]["{prop}"]'
    return curve


def prop(bone,name,value,low,high,description):
    bone[name]=value
    bone.id_properties_ui(name).update(min=low,max=high,soft_min=low,soft_max=high,description=description)


def center(obj):
    vs=[v.co for v in obj.data.vertices]
    return Vector([(min(v[i] for v in vs)+max(v[i] for v in vs))*.5 for i in range(3)])


def widget(name,kind):
    mesh=bpy.data.meshes.new(PREFIX+'Widget_'+name)
    if kind=='ring':
        points=[(math.cos(i*math.tau/32),math.sin(i*math.tau/32),0) for i in range(32)]
    elif kind=='diamond':points=[(-1,0,0),(0,1,0),(1,0,0),(0,-1,0)]
    else:points=[(-1,-1,0),(-1,1,0),(1,1,0),(1,-1,0)]
    mesh.from_pydata(points,[(i,(i+1)%len(points)) for i in range(len(points))],[])
    obj=bpy.data.objects.new(PREFIX+'Widget_'+name,mesh);obj.hide_render=True
    # Referenced by pose bones, not linked as visible render geometry.
    return obj


class CharacterRig:
    def __init__(self,stage,key,index):
        self.stage=stage;self.key=key;self.prefix=PREFIX+key+'_';self.x=(index-2)*3
        self.collection=bpy.data.collections.new(PREFIX+key);stage.scene.collection.children.link(self.collection)
        self.meshes={};self.assignments={};self.material_map={};self.defaults={}
        source=bpy.data.scenes['Weather_Fairies_v002'];bpy.context.window.scene=source
        bpy.context.view_layer.update();deps=bpy.context.evaluated_depsgraph_get()
        origin=bpy.data.objects['WF2_'+key+'_Root'];inverse=origin.matrix_world.inverted()
        for old in bpy.data.collections['WF2_'+key].objects:
            if old.type not in ('MESH','CURVE'):continue
            label=old.name.removeprefix('WF2_'+key+'_')
            mesh=bpy.data.meshes.new_from_object(old.evaluated_get(deps),preserve_all_data_layers=True,depsgraph=deps)
            mesh.name=self.prefix+label;mesh.transform(inverse@old.matrix_world)
            materials=list(mesh.materials);mesh.materials.clear()
            for original in materials:
                if original not in self.material_map:
                    material=original.copy();material.name=PREFIX+original.name.removeprefix('WF2_')+'_'+key
                    self.material_map[original]=material
                mesh.materials.append(self.material_map[original])
            obj=bpy.data.objects.new(self.prefix+label,mesh);self.collection.objects.link(obj)
            self.meshes[label]=obj
        bpy.context.window.scene=stage.scene
        data=bpy.data.armatures.new(self.prefix+'Skeleton')
        self.rig=bpy.data.objects.new(self.prefix+'RIG',data);self.collection.objects.link(self.rig)
        self.rig.location=(self.x,0,0);self.rig.show_in_front=True;data.display_type='OCTAHEDRAL'
        self.rig['character_ko']=NAMES[key];self.rig['rig_version']='1.0';self.rig['instructions']='Pose Mode: move CTRL_Hand / CTRL_Foot. Select CTRL_Face or CTRL_Extras; edit custom properties in N > Item.'
        bpy.ops.object.select_all(action='DESELECT');self.rig.select_set(True);bpy.context.view_layer.objects.active=self.rig
        self.original_labels=list(self.meshes)
        self.build_bones();self.build_properties();self.skin();self.face();self.special_drivers();self.decorate()
        for pb in self.rig.pose.bones:
            self.defaults[pb.name]={k:pb[k] for k in pb.keys() if isinstance(pb[k],(int,float))}
        self.rig['neutral_properties']=__import__('json').dumps(self.defaults)
        stage.rigs[key]=self

    def bone(self,name,head,tail,parent=None,deform=False,connected=False):
        b=self.rig.data.edit_bones.new(name);b.head=head;b.tail=tail;b.use_deform=deform
        if parent:b.parent=self.rig.data.edit_bones[parent];b.use_connect=connected
        b.align_roll(Vector((0,-1,0)))
        if hasattr(b,'inherit_scale'):b.inherit_scale='FIX_SHEAR'
        return b

    def build_bones(self):
        bpy.ops.object.mode_set(mode='EDIT')
        self.bone('CTRL_Root',(0,0,.30),(0,0,.75))
        self.bone('CTRL_Body',(0,0,1.25),(0,0,2.1),'CTRL_Root')
        self.bone('DEF_Body',(0,0,1.25),(0,0,2.1),'CTRL_Body',True)
        self.bone('CTRL_Face',(-1.05,-1.0,3.7),(-1.05,-1.0,4.0),'CTRL_Root')
        self.bone('CTRL_Extras',(1.05,-1.0,3.7),(1.05,-1.0,4.0),'CTRL_Root')
        parent='CTRL_Body'
        if self.key=='Solsol':
            self.bone('DEF_Bend',(0,0,1.15),(0,0,2.45),'CTRL_Body',True)
            self.bone('DEF_Crest',(-.35,.05,2.42),(.1,.07,3.4),'DEF_Bend',True)
            parent='DEF_Bend'
        for j,side in enumerate(('L','R')):
            a,b,c=map(Vector,ARMS[self.key][j])
            self.bone('DEF_UpperArm.'+side,a,b,parent,True)
            self.bone('DEF_Forearm.'+side,b,c,'DEF_UpperArm.'+side,True,True)
            self.bone('DEF_Hand.'+side,c,c+(c-b).normalized()*.23,'DEF_Forearm.'+side,True,True)
            self.bone('MCH_HandSpace.'+side,c,c+Vector((0,0,.25)),parent)
            self.bone('CTRL_Hand.'+side,c,c+Vector((0,0,.25)),'MCH_HandSpace.'+side)
            a,b,c=map(Vector,LEGS[self.key][j])
            self.bone('DEF_Thigh.'+side,a,b,'CTRL_Body',True)
            self.bone('DEF_Shin.'+side,b,c,'DEF_Thigh.'+side,True,True)
            self.bone('DEF_Foot.'+side,c,c+Vector((0,-.3,-.13)),'DEF_Shin.'+side,True,True)
            self.bone('CTRL_Foot.'+side,c,c+Vector((0,0,.25)),'CTRL_Root')
        if self.key=='Mongsil':self.bone('CTRL_Cushion',(0,-.69,1.38),(0,-.69,1.83),'CTRL_Body',True)
        if self.key=='Haerong':
            for i in range(12):
                c=center(self.meshes[f'Ray_{i:02d}']);self.bone(f'DEF_Ray_{i:02d}',(0,0,2.12),c,'CTRL_Body',True)
        if self.key=='Songsong':
            for i in range(6):
                a=i*math.tau/6;self.bone(f'DEF_Crystal_{i:02d}',(0,.055,2.13),(math.sin(a)*1.31,.055,2.13+math.cos(a)*1.31),'CTRL_Body',True)
        if self.key=='Solsol':
            for label,points in [('Upper',[(.46,-.10,1.25),(.86,.08,1.47),(1.20,.16,1.41),(1.55,.16,1.57)]),('Lower',[(.47,-.08,1.22),(.88,.18,1.11),(1.18,.23,1.18),(1.42,.24,1.05)])]:
                for i in range(3):self.bone(f'DEF_Scarf{label}{i}',points[i],points[i+1],'DEF_Bend' if i==0 else f'DEF_Scarf{label}{i-1}',True,i>0)
        bpy.ops.object.mode_set(mode='OBJECT')
        for side in ('L','R'):
            for part,target in [('Forearm','Hand'),('Shin','Foot')]:
                pb=self.rig.pose.bones['DEF_'+part+'.'+side];c=pb.constraints.new('IK');c.name='Two joint '+target+' IK'
                c.target=self.rig;c.subtarget='CTRL_'+target+'.'+side;c.chain_count=2;c.use_stretch=False;c.iterations=64
        for pb in self.rig.pose.bones:pb.rotation_mode='XYZ'

    def build_properties(self):
        body=self.rig.pose.bones['CTRL_Body'];face=self.rig.pose.bones['CTRL_Face'];extra=self.rig.pose.bones['CTRL_Extras']
        prop(body,'squash',0.,-.25,.35,'몸 눌림/늘림. 기본 0; 손발 IK는 별도로 조작 가능')
        prop(face,'blink',0.,0.,1.,'눈 깜빡임 / 닫기')
        prop(face,'smile',0.,0.,1.,'웃음의 폭과 입꼬리')
        prop(face,'surprise',0.,0.,1.,'놀란 동그란 입과 눈썹')
        prop(face,'awake',0.,0.,1.,'몽실/솔솔의 눈 뜨기, 송송의 윙크 눈 뜨기')
        specifications={
          'Mongsil':[('breath',0.,0.,1.,'숨 들이쉬기'),('hug',1.,0.,1.,'0 팔 벌리기 / 1 쿠션 안기')],
          'Haerong':[('ray_sway',0.,0.,1.,'햇살 흔들림 크기'),('ray_phase',0.,-100.,100.,'햇살 흔들림 진행'),('ray_spread',0.,-.1,.12,'햇살 펼치기')],
          'Ttorr':[('tip_sway',0.,-1.,1.,'물방울 꼭지 좌우 휘기')],
          'Songsong':[('crystal_fold',0.,0.,1.,'눈 결정 접기')],
          'Solsol':[('body_bend',0.,-1.,1.,'몸 좌우 휘기'),('crest_curl',0.,-1.,1.,'소용돌이 기울기'),('scarf_wave',0.,0.,1.,'스카프 흔들림 크기'),('scarf_phase',0.,-100.,100.,'스카프 흔들림 진행')]
        }
        for args in specifications[self.key]:prop(extra,*args)
        variables={'s':('CTRL_Body','squash')};expr='1+s'
        if self.key=='Mongsil':variables['b']=('CTRL_Extras','breath');expr='1+s+0.035*b'
        drive(body,'scale',1,self.rig,variables,expr)
        for axis in (0,2):drive(body,'scale',axis,self.rig,variables,f'1/sqrt({expr})')

    def bind(self,obj,weights):
        obj.parent=self.rig;obj.matrix_parent_inverse=Matrix.Identity(4);obj.matrix_basis=Matrix.Identity(4)
        groups={}
        for vertex in obj.data.vertices:
            record=weights(vertex.co)
            for name,value in record.items():
                if value<1e-6:continue
                if name not in groups:groups[name]=obj.vertex_groups.new(name=name)
                groups[name].add([vertex.index],float(value),'REPLACE')
        modifier=obj.modifiers.new('Weather skeletal deformation','ARMATURE');modifier.object=self.rig;modifier.use_deform_preserve_volume=True
        self.assignments[obj.name]=list(groups)

    def torso_weights(self,co):
        if self.key!='Solsol':return {'DEF_Body':1.}
        bend=smooth(1.1,2.1,co.z);crest=smooth(2.45,3.15,co.z)
        return {'DEF_Body':1-bend,'DEF_Bend':bend*(1-crest),'DEF_Crest':bend*crest}

    def chain_weights(self,co,points,names):
        # Smoothly blend adjacent joints along the original curved limb.
        points=list(map(Vector,points));best=(1e9,0.)
        lengths=[(b-a).length for a,b in zip(points,points[1:])];total=sum(lengths);offset=0
        for i,(a,b) in enumerate(zip(points,points[1:])):
            direction=b-a;t=max(0,min(1,(co-a).dot(direction)/direction.length_squared))
            distance=(co-(a+direction*t)).length
            if distance<best[0]:best=(distance,(offset+t*lengths[i])/total)
            offset+=lengths[i]
        fraction=best[1];joint=lengths[0]/total
        blend=smooth(joint-.17,joint+.17,fraction)
        return {names[0]:1-blend,names[1]:blend}

    def skin(self):
        for label,obj in self.meshes.items():
            c=center(obj);side='L' if c.x<0 else 'R';i=0 if side=='L' else 1
            fixed=None;weights=None
            if any(token in label for token in ('Arm','LeftHug','RightHug')):
                weights=lambda co,i=i,side=side:self.chain_weights(co,ARMS[self.key][i],['DEF_UpperArm.'+side,'DEF_Forearm.'+side])
            elif any(token in label for token in ('Hand','Mitten','Thumb','Palm','Crease')):fixed='DEF_Hand.'+side
            elif 'Leg' in label:weights=lambda co,i=i,side=side:self.chain_weights(co,LEGS[self.key][i],['DEF_Thigh.'+side,'DEF_Shin.'+side])
            elif any(token in label for token in ('Shoe','Slipper','Boot')):fixed='DEF_Foot.'+side
            elif label=='HuggedStar':fixed='CTRL_Cushion'
            elif label.startswith('Ray_'):fixed='DEF_'+label
            elif label.startswith('Crystal'):fixed='DEF_Crystal_'+label.split('_')[1]
            elif 'ScarfTail' in label or label=='ScarfStitch':
                part='Lower' if label.startswith('Lower') else 'Upper'
                def scarf(co,part=part):
                    t=max(0,min(2,(co.x-.55)/.4));a=int(t);b=min(2,a+1);u=t-a
                    return {f'DEF_Scarf{part}{a}':1-u} if a==b else {f'DEF_Scarf{part}{a}':1-u,f'DEF_Scarf{part}{b}':u}
                weights=scarf
            if fixed:weights=lambda co,b=fixed:{b:1.}
            self.bind(obj,weights or self.torso_weights)

    def shape(self,obj,name,transform,variables,expression):
        if not obj.data.shape_keys:obj.shape_key_add(name='Basis')
        block=obj.shape_key_add(name=name)
        for point in block.data:point.co=transform(point.co.copy())
        drive(block,'value',None,self.rig,variables,expression)
        return block

    def ellipsoid(self,label,position,scale,material):
        mesh=bpy.data.meshes.new(self.prefix+label);bm=bmesh.new()
        bmesh.ops.create_uvsphere(bm,u_segments=24,v_segments=16,radius=1)
        matrix=Matrix.Translation(Vector(position))@Matrix.Diagonal(Vector((*scale,1)))
        bmesh.ops.transform(bm,matrix=matrix,verts=bm.verts);bm.to_mesh(mesh);bm.free()
        for polygon in mesh.polygons:polygon.use_smooth=True
        mesh.materials.append(material)
        obj=bpy.data.objects.new(self.prefix+label,mesh);self.collection.objects.link(obj);self.meshes[label]=obj
        self.bind(obj,self.torso_weights)
        return obj

    def face(self):
        blink={'v':('CTRL_Face','blink')};smile={'v':('CTRL_Face','smile')};surprise={'v':('CTRL_Face','surprise')};awake={'v':('CTRL_Face','awake')}
        originals=list(self.meshes.items());mouths=[]
        for label,obj in originals:
            c=center(obj)
            if any(token in label for token in ('BrightEye','ShyEye','OpenEye','EyeGlint')):
                self.shape(obj,'Blink',lambda co,c=c:Vector((co.x,co.y,c.z+(co.z-c.z)*.06)),blink,'v')
            if any(token in label for token in ('SleepingEye','HappyEye','WinkingEye')):
                self.shape(obj,'Wake',lambda co,c=c:c+(co-c)*.001,awake,'v')
                eye=self.ellipsoid('AwakeEye_'+label,(c.x,c.y-.016,c.z),(.060,.031,.091),obj.data.materials[0]);ec=center(eye)
                self.shape(eye,'Hide',lambda co,c=ec:c+(co-c)*.001,awake,'1-v')
                self.shape(eye,'Blink',lambda co,c=ec:Vector((co.x,co.y,c.z+(co.z-c.z)*.06)),{'v':('CTRL_Face','blink'),'a':('CTRL_Face','awake')},'v*a')
            if any(token in label for token in ('Mouth','Smile')):mouths.append((label,obj,c))
            if any(token in label for token in ('Mouth','Smile','Tongue','SoftLip')):
                width=max(.07,max(abs(v.co.x-c.x) for v in obj.data.vertices))
                self.shape(obj,'Smile',lambda co,c=c,w=width:Vector((c.x+(co.x-c.x)*1.45,co.y,co.z+.10*((co.x-c.x)/w)**2)),{'v':('CTRL_Face','smile'),'u':('CTRL_Face','surprise')},'v*(1-u)')
                self.shape(obj,'SurpriseHide',lambda co,c=c:c+(co-c)*.001,surprise,'v')
            if 'Brow' in label:self.shape(obj,'BrowRaise',lambda co:co+Vector((0,0,.12)),surprise,'v')
        if mouths:
            _,obj,c=mouths[0];round_mouth=self.ellipsoid('SurprisedMouth',(c.x,c.y-.025,c.z),(.092,.024,.125),obj.data.materials[0]);mc=center(round_mouth)
            self.shape(round_mouth,'Hide',lambda co,c=mc:c+(co-c)*.001,surprise,'1-v')
        if self.key=='Ttorr':
            for label,obj in originals:
                if label=='DropBody' or 'Highlight' in label:
                    self.shape(obj,'TipSway',lambda co:Vector((co.x+.35*smooth(2.0,2.95,co.z)**2,co.y,co.z)),{'v':('CTRL_Extras','tip_sway')},'v').slider_min=-1

    def special_drivers(self):
        if self.key=='Mongsil':
            for j,side in enumerate(('L','R')):
                pb=self.rig.pose.bones['MCH_HandSpace.'+side]
                delta=pb.bone.matrix_local.to_3x3().inverted()@Vector((-.30 if j==0 else .30,.20,.18))
                for axis in range(3):drive(pb,'location',axis,self.rig,{'h':('CTRL_Extras','hug')},f'{delta[axis]}*(1-h)')
        if self.key=='Haerong':
            for i in range(12):
                pb=self.rig.pose.bones[f'DEF_Ray_{i:02d}']
                drive(pb,'rotation_euler',2,self.rig,{'s':('CTRL_Extras','ray_sway'),'p':('CTRL_Extras','ray_phase')},f'0.11*s*sin(p+{i*.6})')
                drive(pb,'scale',1,self.rig,{'s':('CTRL_Extras','ray_spread')},'1+s')
        if self.key=='Songsong':
            for i in range(6):
                pb=self.rig.pose.bones[f'DEF_Crystal_{i:02d}']
                for axis in range(3):drive(pb,'scale',axis,self.rig,{'f':('CTRL_Extras','crystal_fold')},'1-0.58*f' if axis==1 else '1-0.35*f')
        if self.key=='Solsol':
            for name,pr,amount in [('DEF_Bend','body_bend',.22),('DEF_Crest','crest_curl',.28)]:
                drive(self.rig.pose.bones[name],'rotation_euler',2,self.rig,{'v':('CTRL_Extras',pr)},f'{amount}*v')
            for part in ('Upper','Lower'):
                for i in range(3):
                    pb=self.rig.pose.bones[f'DEF_Scarf{part}{i}'];phase=i*.8+(0 if part=='Upper' else 1)
                    drive(pb,'rotation_euler',2,self.rig,{'s':('CTRL_Extras','scarf_wave'),'p':('CTRL_Extras','scarf_phase')},f'0.16*s*sin(p-{phase})')

    def decorate(self):
        controls=self.rig.data.collections.new('Controls — 조작');deform=self.rig.data.collections.new('Deform — 변형');mechanism=self.rig.data.collections.new('Mechanism — 내부')
        shapes={kind:widget(self.key+'_'+kind,kind) for kind in ('ring','square','diamond')}
        for bone in self.rig.data.bones:
            pb=self.rig.pose.bones[bone.name]
            if bone.name.startswith('CTRL_'):
                controls.assign(bone);kind='diamond' if bone.name in ('CTRL_Face','CTRL_Extras') else 'ring'
                pb.custom_shape=shapes[kind];pb.use_custom_shape_bone_size=False
                size=.75 if bone.name=='CTRL_Body' else (1.25 if bone.name=='CTRL_Root' else .21)
                pb.custom_shape_scale_xyz=(size,)*3
                if hasattr(pb,'color'):pb.color.palette='THEME04' if bone.name.endswith('.L') else ('THEME01' if bone.name.endswith('.R') else 'THEME03')
            elif bone.name.startswith('MCH_'):mechanism.assign(bone)
            else:deform.assign(bone)
        deform.is_visible=False;mechanism.is_visible=False
        bpy.context.view_layer.update()

    def metadata(self):
        return {'name':self.key,'ko':NAMES[self.key],'armature':self.rig.name,'bones':len(self.rig.data.bones),
                'controls':[b.name for b in self.rig.data.bones if b.name.startswith('CTRL_')],
                'meshes':len(self.meshes),'shape_keys':sum(len(o.data.shape_keys.key_blocks)-1 for o in self.meshes.values() if o.data.shape_keys),
                'properties':self.defaults,'skinned_meshes':len(self.assignments),'bindings':self.assignments}
