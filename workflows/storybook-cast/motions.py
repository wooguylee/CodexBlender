"""Eight usable in-place actions, native IK controls, and a continuous export take."""
import bpy,math,json
import numpy as np
from mathutils import Vector
from rigging import world_delta
from catalog import CLIPS,SWIMMERS,clip_ranges

def mesh_bounds(mesh):
    evaluated=mesh.evaluated_get(bpy.context.evaluated_depsgraph_get());data=evaluated.data
    xyz=np.empty(len(data.vertices)*3,dtype=np.float32);data.vertices.foreach_get('co',xyz);xyz=xyz.reshape((-1,3))
    assert np.isfinite(xyz).all();return xyz.min(axis=0),xyz.max(axis=0)

def curves(action):
    return action.layers[0].strips[0].channelbag(action.slots[0]).fcurves

def set_pose(rig,key,kind,u):
    controls=[p for p in rig.pose.bones if p.name.startswith('CTRL_') or p.name in json.loads(rig['extra_names'])]
    for p in controls:p.location=(0,0,0);p.rotation_euler=(0,0,0);p.scale=(1,1,1)
    body=rig.pose.bones['CTRL_Body'];head=rig.pose.bones['CTRL_Head'];face=rig.pose.bones['CTRL_Face']
    t=u*2.;phase=math.tau*t;seat=0.;body_delta=Vector((0,0,0));swim=key in SWIMMERS
    if kind in ('SitDown','StandUp'):seat=(u*u*(3-2*u));seat=seat if kind=='SitDown' else 1-seat
    if kind=='SitIdle':seat=1.
    body_delta.y=.10*seat;body_delta.z=-(.26 if swim else .36)*seat
    # A tailless leg IK target cannot lower a seahorse whose curled tail already
    # touches the ground. Compress its long torso into a readable resting pose.
    if key=='HaniSeahorse':body.scale.y=1-.16*seat
    if kind in ('Idle','SitIdle'):body_delta.z+=.009*math.sin(phase);head.rotation_euler[2]=.025*math.sin(phase)
    if kind in ('Walk','Run'):
        fast=kind=='Run';phase=math.tau*t*(1.5 if fast else 1)
        body_delta.z=(.035 if fast else .017)*(1-math.cos(phase*2))
        body.rotation_euler[0]=(.12 if fast else .04)*(1 if not swim else -1)
        body.rotation_euler[2]=(.035 if fast else .025)*math.sin(phase)
        head.rotation_euler[0]=-.025 if fast else 0
    if kind=='Celebrate':
        body_delta.z=.17*math.sin(math.pi*u)**2*abs(math.sin(phase));body.rotation_euler[2]=.12*math.sin(phase)*math.sin(math.pi*u)
        if key in ('PuruPudding','MomoMochi','BobaPuffer'):head.scale=(1+.065*math.sin(phase)**2,1-.055*math.sin(phase)**2,1+.065*math.sin(phase)**2)
    world_delta(body,body_delta)
    for i,side in enumerate(('L','R')):
        sign=-1 if side=='L' else 1;leg_phase=phase+i*math.pi;foot=Vector((0,-.34*seat,0));hand=Vector((-sign*.18*seat,-.28*seat,-.29*seat))
        if kind in ('Walk','Run'):
            fast=kind=='Run';foot.y=(.245 if fast else .17)*math.cos(leg_phase)
            foot.z=(.17 if fast else .095)*max(0,math.sin(leg_phase)+(.20 if fast else 0))
            hand.y=-(.21 if fast else .15)*math.cos(leg_phase);hand.z=(.14 if fast else .035)+.035*math.sin(leg_phase)
            if swim:
                foot=(0,0,0);hand=Vector((sign*.07*math.sin(leg_phase),.13*math.cos(leg_phase),.19+.10*math.sin(leg_phase)))
        if kind=='Wave' and side=='R':
            e=math.sin(math.pi*u);hand=Vector((-.08*e+.12*math.sin(phase*2)*e,-.12*e,.83*e))
        if kind=='Celebrate':
            e=math.sin(math.pi*u);hand=Vector((sign*.12*e,-.08*e,.75*e))
        world_delta(rig.pose.bones['CTRL_Foot.'+side],foot)
        world_delta(rig.pose.bones['CTRL_Hand.'+side],hand)
    extras=json.loads(rig['extra_names'])
    for i,name in enumerate(extras):
        p=rig.pose.bones[name];strength=.055 if kind in ('Idle','SitIdle') else .11
        if 'Tentacle' in name or 'SideLeg' in name:strength=.065
        p.rotation_euler[0]=strength*math.sin(phase+i*.8)*math.sin(math.pi*u)
        if 'Ear' in name or 'Antenna' in name:p.rotation_euler[2]=strength*.8*math.sin(phase)*math.sin(math.pi*u)
        if seat and ('Tail' in name or 'Tentacle' in name):p.rotation_euler[0]+=.12*seat
    # A short centered blink. All loop endpoints have identical face values.
    face['blink']=max(0,1-abs(u-.48)/.055)
    face['smile']=.6*math.sin(math.pi*u)**2 if kind in ('Wave','Celebrate') else .1*math.sin(math.pi*u)**2
    face['surprise']=.9*math.sin(math.pi*u)**4 if kind=='Celebrate' else 0.
    return controls

def create_actions(scene,rig,mesh,key):
    rig.animation_data_create();action=bpy.data.actions.new(key+'_AllMotions');rig.animation_data.action=action
    rig['extra_names']=json.dumps([e['name'] for e in json.loads(rig['extra_bones'])])
    extrema=[];ground_max=0.;ranges=clip_ranges();last=ranges[-1]['last']
    scene.frame_start=1;scene.frame_end=last
    for clip in ranges:
        count=clip['last']-clip['first']
        for frame in range(clip['first'],clip['last']+1):
            scene.frame_set(frame);u=(frame-clip['first'])/count;controls=set_pose(rig,key,clip['name'],u)
            bpy.context.view_layer.update();low,high=mesh_bounds(mesh)
            # Extra tentacles/tails fold while sitting. Prevent floor penetration across all frames.
            correction=max(0.,-float(low[2]));world_delta(rig.pose.bones['CTRL_Root'],(0,0,correction))
            for p in controls:
                for channel in ('location','rotation_euler','scale'):p.keyframe_insert(channel,frame=frame,group=p.name)
            for prop in ('blink','smile','surprise'):rig.pose.bones['CTRL_Face'].keyframe_insert('["'+prop+'"]',frame=frame,group='Face')
            if frame in (clip['first'],clip['last']) or (frame-clip['first'])%12==0:
                bpy.context.view_layer.update();lo,hi=mesh_bounds(mesh);ground_max=max(ground_max,max(0,-float(lo[2])))
                extrema.append({'clip':clip['name'],'frame':frame,'min':lo.tolist(),'max':hi.tolist(),'ground_correction':correction})
    for f in curves(action):
        for p in f.keyframe_points:p.interpolation='LINEAR'
    action.use_fake_user=True;actions={}
    for clip in ranges:
        cut=action.copy();cut.name=key+'_'+clip['name'];cut.use_fake_user=True
        for f in curves(cut):
            rows=[(p.co.x-clip['first']+1,p.co.y) for p in f.keyframe_points if clip['first']<=p.co.x<=clip['last']]
            f.keyframe_points.clear();f.keyframe_points.add(len(rows))
            for p,co in zip(f.keyframe_points,rows):p.co=co;p.interpolation='LINEAR'
            f.update()
        actions[clip['name']]=cut
    rig.animation_data.action=action;rig.animation_data.action_slot=action.slots[0];scene.frame_set(1);bpy.context.view_layer.update()
    assert ground_max<.0001,(key,ground_max)
    return action,actions,{'frames':last,'fps':24,'clips':ranges,'samples':extrema,'max_ground_penetration':ground_max}
