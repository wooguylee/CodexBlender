"""Scene 라이브러리 로드의 목록 변환 때문에 실패한 JSON 기록만 복구한다."""
import bpy,json
scene=bpy.context.scene;assert scene.name=='Autumn_Cafe_v001'
assert 'FullSceneForEditing' in scene.view_layers
report={'ok':True,'active_scene':scene.name,'camera':scene.camera.name,'preserved_scenes':{s.name:len(s.objects) for s in bpy.data.scenes if s!=scene},'packed_backgrounds':[{'name':n.image.name,'packed':bool(n.image.packed_file)} for n in scene.compositing_node_group.nodes if n.type=='IMAGE'],'original':'scenes/autumn-cafe-v001.blend','note':'Historical scenes loaded from existing versioned archive. Source was saved before the JSON serialization error; only the report is repaired here.'}
(PROJECT_ROOT/'outputs/autumn-cafe/v001/final-scene-report.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
scene.frame_set(1)
print(json.dumps(report,indent=2))
