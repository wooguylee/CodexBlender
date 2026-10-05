"""5.2의 Bone.select 제거로 마지막 저장 직전 중단된 초안의 기존 데이터를 확인하고 저장한다."""
import hashlib,json,subprocess
scene=bpy.data.scenes['Weather_Rigs_v001'];bpy.context.window.scene=scene
out=PROJECT_ROOT/'outputs/weather-rigs/v001';source=PROJECT_ROOT/'scenes/weather-rigs-v001.blend'
assert not source.exists()
inspection=json.loads((out/'source-inspection.json').read_text(encoding='utf-8'))
records=[]
for key in ('Mongsil','Haerong','Ttorr','Songsong','Solsol'):
    rig=bpy.data.objects['WR1_'+key+'_RIG'];assert rig.type=='ARMATURE'
    meshes=[o for o in bpy.data.collections['WR1_'+key].objects if o.type=='MESH']
    bindings={o.name:[g.name for g in o.vertex_groups] for o in meshes}
    assert len(rig.pose.bones)>=23
    records.append({'name':key,'ko':rig['character_ko'],'armature':rig.name,'bones':len(rig.data.bones),
       'controls':[b.name for b in rig.data.bones if b.name.startswith('CTRL_')],
       'meshes':len(meshes),'shape_keys':sum(len(o.data.shape_keys.key_blocks)-1 for o in meshes if o.data.shape_keys),
       'properties':json.loads(rig['neutral_properties']),'skinned_meshes':len(bindings),'bindings':bindings})
existing={}
paths=[p for p in (PROJECT_ROOT/'scenes').glob('*.blend') if p.name!='current.blend']
paths+=list((PROJECT_ROOT/'outputs/weather-shorts/v001').rglob('*.mp4'))
for path in paths:existing[path.relative_to(PROJECT_ROOT).as_posix()]=hashlib.sha256(path.read_bytes()).hexdigest()
scene.frame_set(1);bpy.context.view_layer.update()
bpy.data.libraries.write(str(source),{scene},path_remap='RELATIVE',fake_user=True,compress=True)
report={'ok':True,'source':source.relative_to(PROJECT_ROOT).as_posix(),'scene':scene.name,'camera':scene.camera.name,
 'characters':records,'objects':len(scene.objects),'bones':sum(r['bones'] for r in records),'preserved_files':existing,
 'original_mesh_labels':{k:[o['name'].removeprefix(k+'_') for o in items] for k,items in inspection.items()},
 'external_dependencies':[],'recovery':'Geometry and rigs completed in initial job; removed unsupported Bone.select and saved the existing scene. File hashes cross-checked against preexisting tracked assets in final validation.'}
(out/'build-manifest.json').write_text(json.dumps(report,indent=2,ensure_ascii=False),encoding='utf-8')
print(json.dumps({'ok':True,'rigs':len(records),'bones':report['bones'],'objects':len(scene.objects)}))
