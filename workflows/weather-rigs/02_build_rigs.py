"""사용자가 승인한 다섯 캐릭터 맞춤 리깅을 브리찌로 제작. 기존 자산은 보존한다."""
import hashlib,importlib,json,sys,time
sys.path.insert(0,str(PROJECT_ROOT/'workflows/weather-rigs'))
import rig_factory
importlib.reload(rig_factory)
from rig_factory import Stage,CharacterRig,KEYS

out=PROJECT_ROOT/'outputs/weather-rigs/v001';out.mkdir(parents=True,exist_ok=True)
source=PROJECT_ROOT/'scenes/weather-rigs-v001.blend';assert not source.exists()
existing={}
for path in (PROJECT_ROOT/'scenes').glob('*.blend'):
    if path.name!='current.blend':existing[path.relative_to(PROJECT_ROOT).as_posix()]=hashlib.sha256(path.read_bytes()).hexdigest()
for path in (PROJECT_ROOT/'outputs/weather-shorts/v001').rglob('*.mp4'):
    existing[path.relative_to(PROJECT_ROOT).as_posix()]=hashlib.sha256(path.read_bytes()).hexdigest()
def signature(scene):return {'camera':scene.camera.name if scene.camera else None,'objects':sorted((o.name,o.data.name if o.data else None,o.parent.name if o.parent else None) for o in scene.objects)}
before={scene.name:signature(scene) for scene in bpy.data.scenes}
(out/'preservation-before.json').write_text(json.dumps({'files':existing,'scenes':before},indent=2),encoding='utf-8')
started=time.monotonic();stage=Stage(PROJECT_ROOT)
for i,key in enumerate(KEYS):
    rig=CharacterRig(stage,key,i)
    print(json.dumps({'built':key,'bones':len(rig.rig.data.bones),'meshes':len(rig.meshes),'elapsed':time.monotonic()-started}))
bpy.context.window.scene=stage.scene;stage.scene.frame_set(1);bpy.context.view_layer.update()
assert len([o for o in stage.scene.objects if o.type=='ARMATURE'])==5
for name,expected in before.items():assert signature(bpy.data.scenes[name])==expected,name
records=[stage.rigs[key].metadata() for key in KEYS]
stage.scene['rig_library']='Five native armatures; no Python handlers or addons required for controls.'
stage.scene.render.filepath='//../outputs/weather-rigs/v001/rig-neutral.png'
for area in bpy.context.screen.areas:
    if area.type=='VIEW_3D':area.spaces.active.region_3d.view_perspective='CAMERA'
bpy.ops.object.select_all(action='DESELECT')
active=stage.rigs['Mongsil'].rig;active.select_set(True);bpy.context.view_layer.objects.active=active
active.data.bones.active=active.data.bones['CTRL_Body']
for pose_bone in active.pose.bones:pose_bone.select=False
active.pose.bones['CTRL_Body'].select=True
bpy.data.libraries.write(str(source),{stage.scene},path_remap='RELATIVE',fake_user=True,compress=True)
report={'ok':True,'source':source.relative_to(PROJECT_ROOT).as_posix(),'scene':stage.scene.name,'camera':stage.scene.camera.name,
        'characters':records,'objects':len(stage.scene.objects),'bones':sum(r['bones'] for r in records),
        'preserved_files':existing,'preserved_scenes':list(before),'seconds':time.monotonic()-started,
        'external_dependencies':[],'original_mesh_labels':{k:stage.rigs[k].original_labels for k in KEYS}}
(out/'build-manifest.json').write_text(json.dumps(report,indent=2,ensure_ascii=False),encoding='utf-8')
print(json.dumps({'ok':True,'rigs':5,'bones':report['bones'],'source':report['source'],'seconds':report['seconds']}))
