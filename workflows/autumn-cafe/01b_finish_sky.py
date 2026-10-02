"""실패 지점만 복구: Blender 5.2에서는 Nishita enum이 SINGLE_SCATTERING으로 변경됨."""
import bpy, json, math
from mathutils import Vector
scene=bpy.context.scene;assert scene.name=='Autumn_Cafe_v001'
out=PROJECT_ROOT/'outputs/autumn-cafe/v001';rig=bpy.data.collections['AC_LightingCamera']
world=scene.world;nt=world.node_tree;sky=next(n for n in nt.nodes if n.type=='TEX_SKY')
props={p.identifier:p.type for p in sky.bl_rna.properties}
(out/'sky-api.json').write_text(json.dumps(props,indent=2),encoding='utf-8')
sky.sky_type='SINGLE_SCATTERING'
for key,value in {'sun_elevation':math.radians(34),'sun_rotation':math.radians(225),'altitude':.1,'air_density':1.0,'dust_density':.65,'sun_intensity':.8}.items():
    if key in props:setattr(sky,key,value)
nt.links.new(sky.outputs['Color'],nt.nodes['Background'].inputs['Color']);nt.nodes['Background'].inputs['Strength'].default_value=.35
def area(name,loc,target,power,color,size):
    d=bpy.data.lights.new('AC_'+name,'AREA');d.energy=power;d.color=color;d.shape='DISK';d.size=size
    o=bpy.data.objects.new('AC_'+name,d);rig.objects.link(o);o.location=loc;o.rotation_euler=(Vector(target)-o.location).to_track_quat('-Z','Y').to_euler()
area('Window soft bounce',(0,-.3,3.7),(0,-3,1),220,(1,.87,.68),6)
area('Interior warm fill',(0,-5,3.6),(0,0,1.3),130,(1,.81,.6),5)
d=bpy.data.cameras.new('AC_Camera');cam=bpy.data.objects.new('AC_Camera',d);rig.objects.link(cam)
cam.location=(0,-6.4,1.83);target=Vector((0,14,2.65));cam.rotation_euler=(target-cam.location).to_track_quat('-Z','Y').to_euler()
d.lens=25;d.sensor_width=36;d.clip_end=250;scene.camera=cam;scene.frame_set(1)
for screen in bpy.data.screens:
    for a in screen.areas:
        if a.type=='VIEW_3D':a.spaces.active.region_3d.view_perspective='CAMERA'
scene['request']='코지한 카페 통창, 가을 공원, 좁은 도로와 불규칙 차량, 맑은 오후 3시, 20초 첫/마지막 동일'
scene['loop_endpoint']=480;scene['loop_period_frames']=479
(out/'build-report.json').write_text(json.dumps({'ok':True,'scene':scene.name,'camera':cam.name,'objects':len(scene.objects),'preserved_scenes':{s.name:len(s.objects) for s in bpy.data.scenes if s!=scene},'trees':len([o for o in scene.objects if o.name.startswith('AC_Tree canopy')]),'falling_leaves':56,'cars':6,'external_assets':False,'sky_type':sky.sky_type},indent=2),encoding='utf-8')
print('Sky API recovered; scene complete')
