"""Scene 전용 라이브러리 파일을 바로 열리는 일반 Blender 원본으로 마무리한다."""
import bpy,shutil,json
from pathlib import Path
root=Path(__file__).resolve().parents[2];out=root/'outputs/autumn-cafe/v001'
scene=bpy.data.scenes['Autumn_Cafe_v001'];bpy.context.window.scene=scene
editing=scene.view_layers.get('FullSceneForEditing') or scene.view_layers.new('FullSceneForEditing')
editing.use=False;bpy.context.window.view_layer=editing
scene.frame_set(2);scene.frame_set(1);bpy.context.view_layer.update()
for screen in bpy.data.screens:
    for area in screen.areas:
        if area.type=='VIEW_3D':area.spaces.active.region_3d.view_perspective='CAMERA'
source=root/'scenes/autumn-cafe-v001.blend'
backup=out/'source-before-window-state.blend';assert not backup.exists();shutil.copyfile(source,backup)
bpy.ops.wm.save_as_mainfile(filepath=str(source),check_existing=False,compress=True,relative_remap=True)
print(json.dumps({'ok':True,'scenes':list(bpy.data.scenes.keys()),'saved_normal_project':True}))
