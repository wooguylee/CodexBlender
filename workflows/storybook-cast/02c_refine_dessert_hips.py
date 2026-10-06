"""마카롱과 슈크림의 몸통 안으로 허벅지 시작점을 연결한다. 다른 18종은 보존."""
import bpy,sys,json,importlib,shutil
root=PROJECT_ROOT;sys.path.insert(0,str(root/'workflows/storybook-cast'))
import geometry,rigging,theme_dessert,exporting
importlib.reload(theme_dessert)
out=root/'outputs/storybook-cast/v001';path=out/'export-manifest.json';modelpath=out/'model-manifest.json'
report=json.loads(path.read_text(encoding='utf-8'));models=json.loads(modelpath.read_text(encoding='utf-8'))
keys={'RoniMacaron','ShushuPuff'};backup=out/'revisions/dessert-hips-initial';backup.mkdir(parents=True,exist_ok=False)
shutil.copy2(path,backup/path.name);shutil.copy2(out/'native-verification.json',backup/'native-verification.json')
for record in report['characters']:
    if record['key'] not in keys:continue
    for field in ('native','fbx'):
        source=(root/record[field]).resolve();assert source.is_relative_to((root/'exports/storybook-cast/v001').resolve())
        shutil.move(str(source),str(backup/source.name))
for record in models['characters']:
    key=record['key']
    if key not in keys:continue
    scene=bpy.data.scenes[record['scene']];collection=bpy.data.collections['SC_'+key];bpy.context.window.scene=scene
    assert set(o.name for o in collection.objects)=={record['rig'],record['mesh']}
    for obj in list(collection.objects):
        data=obj.data;kind=obj.type;bpy.data.objects.remove(obj,do_unlink=True)
        if data.users==0:(bpy.data.armatures if kind=='ARMATURE' else bpy.data.meshes).remove(data)
    for action in list(bpy.data.actions):
        if action.name.startswith(key+'_'):bpy.data.actions.remove(action)
    b=geometry.Builder(key,scene);theme_dessert.build(b,key);mesh=b.combine(collection);rig=rigging.build_rig(b,collection,mesh)
    rig['character_ko']=record['ko'];rig['role_ko']=record['role'];rig['theme']='Dessert';record.update(rig=rig.name,mesh=mesh.name,vertices=len(mesh.data.vertices),polygons=len(mesh.data.polygons))
modelpath.write_text(json.dumps(models,ensure_ascii=False,indent=2),encoding='utf-8')
report['characters']=[c for c in report['characters'] if c['key'] not in keys];report['ok']=False;path.write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
exporting.export_theme(root,'Dessert')
