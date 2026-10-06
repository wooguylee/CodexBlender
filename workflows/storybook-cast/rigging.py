"""Custom IK rig and portable facial controls for the twenty new characters."""
import bpy,math,json
from mathutils import Vector,Matrix

def bone(data,name,head,tail,parent=None,deform=False):
    b=data.edit_bones.new(name);b.head=head;b.tail=tail;b.use_deform=deform
    if parent:b.parent=data.edit_bones[parent]
    direction=Vector(tail)-Vector(head)
    b.align_roll(Vector((0,0,1)) if abs(direction.z)<.01 else Vector((0,-1,0)))
    b.inherit_scale='FIX_SHEAR';return b

def build_rig(builder,collection,mesh):
    data=bpy.data.armatures.new(builder.key+'_Skeleton');rig=bpy.data.objects.new(builder.key+'_Rig',data);collection.objects.link(rig)
    bpy.ops.object.select_all(action='DESELECT');rig.select_set(True);bpy.context.view_layer.objects.active=rig
    bpy.ops.object.mode_set(mode='EDIT')
    bone(data,'CTRL_Root',(0,0,0),(0,0,.35))
    bone(data,'CTRL_Body',(0,0,.68),(0,0,1.25),'CTRL_Root')
    bone(data,'DEF_Body',(0,0,.68),(0,0,1.25),'CTRL_Body',True)
    bone(data,'CTRL_Head',(0,0,1.35),(0,0,1.85),'CTRL_Body')
    bone(data,'DEF_Head',(0,0,1.35),(0,0,1.85),'CTRL_Head',True)
    bone(data,'CTRL_Face',(-1.2,0,2.7),(-1.2,0,3.0),'CTRL_Root')
    for side in ('L','R'):
        a,c,d=builder.arms[side];bone(data,'DEF_UpperArm.'+side,a,c,'DEF_Body',True)
        bone(data,'DEF_Forearm.'+side,c,d,'DEF_UpperArm.'+side,True)
        bone(data,'DEF_Hand.'+side,d,d+(d-c).normalized()*.15,'DEF_Forearm.'+side,True)
        bone(data,'CTRL_Hand.'+side,d,d+Vector((0,0,.2)),'CTRL_Root')
        a,c,d=builder.legs[side];bone(data,'DEF_Thigh.'+side,a,c,'DEF_Body',True)
        bone(data,'DEF_Shin.'+side,c,d,'DEF_Thigh.'+side,True)
        bone(data,'DEF_Foot.'+side,d,d+Vector((0,-.28,0)),'DEF_Shin.'+side,True)
        bone(data,'CTRL_Foot.'+side,d,d+Vector((0,-.28,0)),'CTRL_Root')
    for extra in builder.extras:bone(data,extra['name'],extra['head'],extra['tail'],extra['parent'],True)
    bpy.ops.object.mode_set(mode='OBJECT')
    for side in ('L','R'):
        for part,target in [('Forearm','Hand'),('Shin','Foot')]:
            pb=rig.pose.bones['DEF_'+part+'.'+side];c=pb.constraints.new('IK');c.name='Two bone '+target+' IK'
            c.target=rig;c.subtarget='CTRL_'+target+'.'+side;c.chain_count=2;c.use_stretch=False;c.iterations=64
        c=rig.pose.bones['DEF_Foot.'+side].constraints.new('COPY_ROTATION');c.target=rig;c.subtarget='CTRL_Foot.'+side;c.target_space='POSE';c.owner_space='POSE'
    for pb in rig.pose.bones:pb.rotation_mode='XYZ'
    mesh.parent=rig;mesh.matrix_parent_inverse=Matrix.Identity(4);mesh.matrix_basis=Matrix.Identity(4)
    mod=mesh.modifiers.new('Storybook skin','ARMATURE');mod.object=rig;mod.use_deform_preserve_volume=False
    face=rig.pose.bones['CTRL_Face']
    for name in ('blink','smile','surprise'):
        face[name]=0.;face.id_properties_ui(name).update(min=0.,max=1.,description='Face '+name+' (0 to 1)')
        key=mesh.data.shape_keys.key_blocks[name.title()];curve=key.driver_add('value');d=curve.driver;d.type='SCRIPTED'
        v=d.variables.new();v.name='v';v.type='SINGLE_PROP';v.targets[0].id=rig;v.targets[0].data_path='pose.bones["CTRL_Face"]["'+name+'"]';d.expression='v'
        if name=='smile':
            v=d.variables.new();v.name='s';v.type='SINGLE_PROP';v.targets[0].id=rig;v.targets[0].data_path='pose.bones["CTRL_Face"]["surprise"]';d.expression='v*(1-s)'
    controls=data.collections.new('Controls - pose these');deforms=data.collections.new('Deform bones');extras=data.collections.new('Extras - ears tails fins')
    for b in data.bones:
        (controls if b.name.startswith('CTRL_') else extras if any(e['name']==b.name for e in builder.extras) else deforms).assign(b)
        b.color.palette='THEME04' if b.name.startswith('CTRL_') else 'THEME03'
    deforms.is_visible=False;rig.show_in_front=True;rig['character']=builder.key
    rig['usage']='Pose Mode: CTRL_Hand/Foot IK, CTRL_Body/Head motion, CTRL_Face custom properties. Separate actions are included.'
    rig['extra_bones']=json.dumps(builder.extras);rig['rest_arms']=json.dumps({s:[list(v) for v in ps] for s,ps in builder.arms.items()})
    rig['rest_legs']=json.dumps({s:[list(v) for v in ps] for s,ps in builder.legs.items()})
    rig.data.update_tag();rig.update_tag(refresh={'OBJECT','DATA','TIME'});bpy.context.view_layer.update()
    return rig

def world_delta(pb,delta):
    # Parent controls are unscaled; pose translation channels use rest-local axes.
    pb.location=pb.bone.matrix_local.to_3x3().inverted()@Vector(delta)
