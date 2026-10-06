"""Repair only this task's twenty draft meshes, preserving the original weather assets."""
import sys,importlib,json,time,shutil
sys.path.insert(0,str(PROJECT_ROOT/'workflows/storybook-cast'))
import geometry,rigging
importlib.reload(geometry);importlib.reload(rigging)
from catalog import THEMES
out=PROJECT_ROOT/'outputs/storybook-cast/v001';report=json.loads((out/'model-manifest.json').read_text(encoding='utf-8'));start=time.monotonic()
for record in report['characters']:
    key=record['key'];scene=bpy.data.scenes[record['scene']];collection=bpy.data.collections['SC_'+key];bpy.context.window.scene=scene
    assert set(o.name for o in scene.objects)=={record['rig'],record['mesh']}
    for obj in list(collection.objects):
        assert obj.name in (record['rig'],record['mesh']);data=obj.data;kind=obj.type;bpy.data.objects.remove(obj,do_unlink=True)
        if data.users==0:(bpy.data.armatures if kind=='ARMATURE' else bpy.data.meshes).remove(data)
    b=geometry.Builder(key,scene);importlib.import_module(THEMES[record['theme']]['module']).build(b,key);mesh=b.combine(collection);rig=rigging.build_rig(b,collection,mesh)
    rig['character_ko']=record['ko'];rig['role_ko']=record['role'];rig['theme']=record['theme'];record.update(rig=rig.name,mesh=mesh.name,vertices=len(mesh.data.vertices),polygons=len(mesh.data.polygons))
    print(json.dumps({'refined':key,'seconds':time.monotonic()-start}),flush=True)
for theme in THEMES:
    scene=bpy.data.scenes['SC_'+theme+'_v001'];bpy.context.window.scene=scene
    old=out/(theme+'-models.png');backup=out/(theme+'-draft.png')
    if not backup.exists():shutil.copy2(old,backup)
    scene.render.filepath=str(old);bpy.ops.render.render(write_still=True)
report['geometry_fixes']=['Parallel transported tube frames across vertical tangents','Outward tube/ring/star face winding','Explicit circular bevel profile 0.5']
(out/'model-manifest.json').write_text(json.dumps(report,indent=2,ensure_ascii=False),encoding='utf-8')
bpy.context.window.scene=bpy.data.scenes['SC_Forest_v001']
