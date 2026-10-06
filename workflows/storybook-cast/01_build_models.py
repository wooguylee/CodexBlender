"""브리찌: 기존 날씨 Scene을 보존하고 네 주제의 신규 모델/리그 20개 생성."""
import sys,importlib,json,hashlib,time
from mathutils import Vector
sys.path.insert(0,str(PROJECT_ROOT/'workflows/storybook-cast'))
from geometry import Builder,rgb
from rigging import build_rig
from catalog import THEMES

root=PROJECT_ROOT;out=root/'outputs/storybook-cast/v001';out.mkdir(parents=True,exist_ok=True)
assert not (out/'model-manifest.json').exists(),'Version already exists; choose a new version.'
preserved={p.relative_to(root).as_posix():hashlib.sha256(p.read_bytes()).hexdigest() for p in list((root/'scenes').glob('weather*.blend'))+list((root/'exports/weather-fairies/v001').rglob('*.fbx'))+list((root/'exports/weather-fairies/v001/blender').glob('*.blend'))}
if bpy.context.object and bpy.context.object.mode!='OBJECT':bpy.ops.object.mode_set(mode='OBJECT')
records=[];start=time.monotonic()
for theme,spec in THEMES.items():
    stage=bpy.data.scenes.new('SC_'+theme+'_v001');stage.render.engine='BLENDER_EEVEE';stage.render.resolution_x=1920;stage.render.resolution_y=1080;stage.render.resolution_percentage=100
    stage.render.fps=24;stage.render.image_settings.file_format='PNG';stage.eevee.taa_render_samples=32
    stage.view_settings.view_transform='AgX';stage.world=bpy.data.worlds.new('SC_'+theme+'_World');stage.world.use_nodes=True
    stage.world.node_tree.nodes['Background'].inputs['Color'].default_value=(.65,.65,.65,1);stage.world.node_tree.nodes['Background'].inputs['Strength'].default_value=.5
    for index,(key,ko,role) in enumerate(spec['characters']):
        scene=bpy.data.scenes.new('SC_'+key+'_v001');scene.render.fps=24;scene.unit_settings.system='METRIC';scene.unit_settings.scale_length=1
        bpy.context.window.scene=scene;collection=bpy.data.collections.new('SC_'+key);scene.collection.children.link(collection)
        b=Builder(key,scene);importlib.import_module(spec['module']).build(b,key);mesh=b.combine(collection);rig=build_rig(b,collection,mesh)
        rig['character_ko']=ko;rig['role_ko']=role;rig['theme']=theme;scene['character']=key;scene['theme']=theme
        empty=bpy.data.objects.new('SC_Display_'+key,None);empty.instance_type='COLLECTION';empty.instance_collection=collection;stage.collection.objects.link(empty);empty.location=((index-2)*3.15,0,0)
        bpy.context.view_layer.update();bbox=[v.co for v in mesh.data.vertices];mi=[min(v[i] for v in bbox) for i in range(3)];ma=[max(v[i] for v in bbox) for i in range(3)]
        mats=[]
        for m in mesh.data.materials:
            p=m.node_tree.nodes.get('Principled BSDF');mats.append({'name':m.name,'linear_rgba':list(p.inputs['Base Color'].default_value),'roughness':p.inputs['Roughness'].default_value,'metallic':p.inputs['Metallic'].default_value})
        records.append({'key':key,'ko':ko,'role':role,'theme':theme,'scene':scene.name,'rig':rig.name,'mesh':mesh.name,'vertices':len(mesh.data.vertices),'polygons':len(mesh.data.polygons),'bones':len(rig.data.bones),'extras':b.extras,'materials':mats,'rest_bounds':{'min':mi,'max':ma}})
        print(json.dumps({'built':key,'vertices':len(mesh.data.vertices),'seconds':time.monotonic()-start}))
    bpy.context.window.scene=stage
    # Camera/lights are only in theme review scenes, never individual models.
    camdata=bpy.data.cameras.new('SC_'+theme+'_Camera');cam=bpy.data.objects.new(camdata.name,camdata);stage.collection.objects.link(cam)
    cam.location=(0,-18,6);cam.rotation_euler=(Vector((0,0,1.35))-cam.location).to_track_quat('-Z','Y').to_euler();camdata.type='ORTHO';camdata.ortho_scale=16.6;stage.camera=cam
    for label,location,energy,size in [('Key',(-6,-6,8),1600,8),('Fill',(6,-3,5),1100,7),('Rim',(0,4,7),1400,6)]:
        ld=bpy.data.lights.new('SC_'+theme+'_'+label,'AREA');ld.energy=energy;ld.shape='DISK';ld.size=size;ob=bpy.data.objects.new(ld.name,ld);stage.collection.objects.link(ob);ob.location=location;ob.rotation_euler=(Vector((0,0,1.2))-ob.location).to_track_quat('-Z','Y').to_euler()
    floorBuilder=Builder('Stage'+theme,stage);floorBuilder.mat('Floor',spec['color'],.8)
    floorBuilder.box('Floor',(0,0,-.09),(200,200,.15),'Floor',bone='DEF_Body',bevel=0)
    floor=floorBuilder.combine(stage.collection);floor.name='SC_'+theme+'_Floor'
    stage.render.filepath=str(out/(theme+'-models.png'));bpy.ops.render.render(write_still=True)
report={'ok':True,'characters':records,'preserved_sources':preserved,'seconds':time.monotonic()-start}
(out/'model-manifest.json').write_text(json.dumps(report,indent=2,ensure_ascii=False),encoding='utf-8')
bpy.context.window.scene=bpy.data.scenes['SC_Forest_v001'];print(json.dumps({'ok':True,'models':len(records)}))
