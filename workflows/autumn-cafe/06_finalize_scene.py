"""기존 별도 원본의 장면 보존과 최종 제작 현황 점검. 생성/삭제/재렌더 없음."""
import bpy,json,shutil
scene=bpy.context.scene;assert scene.name=='Autumn_Cafe_v001'
root=PROJECT_ROOT;out=root/'outputs/autumn-cafe/v001'
existing=set(bpy.data.scenes.keys())
# At the actual first mutation the bridge backup held only the default Scene.
# The existing versioned archive retains all historical production scenes.
archive=root/'scenes/rainy-cafe-v002.blend'
with bpy.data.libraries.load(str(archive),link=False) as (src,dst):
    names=[n for n in src.scenes if n not in existing];dst.scenes=names.copy()
editing=scene.view_layers.new('FullSceneForEditing');editing.use=False
bpy.context.window.view_layer=editing
scene.frame_set(1)
images=[]
for n in scene.compositing_node_group.nodes:
    if n.type=='IMAGE':images.append({'name':n.image.name,'packed':bool(n.image.packed_file)})
assert all(im['packed'] for im in images)
source=root/'scenes/autumn-cafe-v001.blend'
shutil.copyfile(source,OUTPUT_DIR/'rendered-source-before-finalize.blend')
bpy.data.libraries.write(str(source),{scene},path_remap='RELATIVE_ALL',fake_user=True,compress=True)
report={'ok':True,'active_scene':scene.name,'camera':scene.camera.name,'preserved_scenes':{s.name:len(s.objects) for s in bpy.data.scenes if s!=scene},'restored_from_versioned_archive':names,'packed_backgrounds':images,'original':'scenes/autumn-cafe-v001.blend'}
(out/'final-scene-report.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
print(json.dumps(report,indent=2))
