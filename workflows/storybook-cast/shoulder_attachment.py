"""Anatomical shoulder anchors and independent attachment measurements."""
from mathutils import Vector
from mathutils.bvhtree import BVHTree
import json
from catalog import THEMES

BODY_PARTS={key:'Rounded_uniform' for key,_,_ in THEMES['Forest']['characters']}
BODY_PARTS.update({key:'SuitTorso' for key,_,_ in THEMES['Space']['characters']})
BODY_PARTS.update(PuruPudding='Custard',MomoMochi='StrawberryMochi',PanBread='GoldenCrust',RoniMacaron='MacaronLower',ShushuPuff='PuffHeart',OctoOctopus='OctopusBody',TutuTurtle='TurtleBody',BobaPuffer='PufferRoundBody',KikiHermit='HermitBody',HaniSeahorse='SeahorseChest')

def body_part(builder,key):
    return next(p for p in builder.parts if p.name==BODY_PARTS[key])

def tree(part):return BVHTree.FromPolygons(part.verts,part.faces,all_triangles=False)
def signed_distance(bvh,point):
    hit,normal,index,distance=bvh.find_nearest(Vector(point))
    assert hit is not None
    return distance if (Vector(point)-hit).dot(normal)>0 else -distance

def original_measurement(builder,key):
    body=body_part(builder,key);bvh=tree(body);rows=[]
    for side in ('L','R'):
        part=next((p for p in builder.parts if p.name=='Arm'+side),None)
        if part is None:part=next(p for p in builder.parts if p.name==('Wing_upper_'+side if key=='BibiOwl' else 'CrabUpperArm'+side))
        distances=[signed_distance(bvh,v) for v in part.verts[:10]]
        rows.append({'side':side,'body':body.name,'body_bone':body.bone,'sample_kind':'wing_surface' if key=='BibiOwl' else 'tube_root_ring','joint_signed_distance':signed_distance(bvh,builder.arms[side][0]),'root_samples_min':min(distances),'root_samples_max':max(distances),'root_fully_inside':max(distances)<-.025})
    return {'key':key,'shoulders':rows}

def fit_shoulders(builder,key):
    """Extend the continuous arm into its own torso and blend proximal weights.

    Keep hand targets and unrelated body/face/prop geometry unchanged. The
    root cap is entirely weighted to the torso, so it cannot pull away when
    the arm rotates, nor when a dessert/puffer's body follows DEF_Head.
    """
    body=body_part(builder,key);bvh=tree(body);center=sum(body.verts,Vector())/len(body.verts)
    builder.shoulder_specs=[]
    for side,sign in (('L',-1),('R',1)):
        original=[v.copy() for v in builder.arms[side]]
        existing=next((p for p in builder.parts if p.name=='Arm'+side),None)
        if existing:
            start=sum(existing.verts[:10],Vector())/10
            radius=sum((v-start).length for v in existing.verts[:10])/10
            material=existing.material;builder.parts.remove(existing)
        elif key=='BibiOwl':
            wing=next(p for p in builder.parts if p.name=='Wing_upper_'+side);material=wing.material;radius=.105
        elif key=='KikiHermit':
            upper=next(p for p in builder.parts if p.name=='CrabUpperArm'+side);material=upper.material;radius=.087
            builder.parts=[p for p in builder.parts if p.name not in ('CrabUpperArm'+side,'CrabForearm'+side)]
        else:raise AssertionError((key,side,'missing arm geometry'))
        hit,normal,index,distance=bvh.ray_cast(Vector((sign*3,center.y,original[0].z)),Vector((-sign,0,0)))
        assert hit is not None,(key,'torso ray missed')
        anchor=Vector((hit.x*.40,center.y,original[0].z));sides=16
        for attempt in range(12):
            builder.arms[side][0]=anchor.copy()
            arm=builder.tube('Arm'+side,builder.arms[side],radius,material,chain=['DEF_UpperArm.'+side,'DEF_Forearm.'+side],sides=sides)
            root_indices=list(range(sides))+[len(arm.verts)-2]
            margin=-max(signed_distance(bvh,arm.verts[i]) for i in root_indices)
            if margin>=.035:break
            builder.parts.remove(arm);anchor.x*=.8;anchor.z=anchor.z*.85+center.z*.15
        assert margin>=.035,(key,side,'cannot embed shoulder cap',margin)
        raw_weights=arm.weights;direction=builder.arms[side][1]-anchor;bodybone=body.bone
        def anchored_weights(co,base=raw_weights,a=anchor.copy(),d=direction.copy(),torso=bodybone):
            t=max(0.,min(1.,(co-a).dot(d)/d.length_squared))
            blend=max(0.,min(1.,(t-.12)/.38));blend=blend*blend*(3-2*blend)
            weights={bone:weight*blend for bone,weight in base(co).items()}
            weights[torso]=weights.get(torso,0.)+1-blend
            return {bone:weight for bone,weight in weights.items() if weight>1e-8}
        arm.weights=anchored_weights
        assert all(arm.weights(arm.verts[i])=={bodybone:1.} for i in root_indices),(key,'cap must follow torso exactly')
        builder.shoulder_specs.append({'side':side,'body_part':body.name,'arm_part':arm.name,'body_bone':bodybone,'root_local_indices':root_indices,'old_joint':list(original[0]),'joint':list(anchor),'rest_inset_min':margin})

def store_attachment_metadata(builder,mesh):
    offsets={};offset=0
    for part in builder.parts:offsets[part.name]=(offset,len(part.verts));offset+=len(part.verts)
    specs=[]
    for spec in builder.shoulder_specs:
        body_start,body_count=offsets[spec['body_part']];arm_start,arm_count=offsets[spec['arm_part']]
        specs.append({**spec,'body_start':body_start,'body_count':body_count,'arm_start':arm_start,'arm_count':arm_count,'root_vertices':[arm_start+i for i in spec['root_local_indices']]})
    mesh['shoulder_attachment']=json.dumps(specs)
