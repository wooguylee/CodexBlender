"""완성된 5편의 원본을 유지한 채 브리찌 작업 화면을 거품 모자 장면으로 정리한다."""
import json
scene=bpy.data.scenes['Weather_Short_05_v001']
assert scene.camera.name=='WS5_Camera'
assert all(f'Weather_Short_{i:02d}_v001' in bpy.data.scenes for i in range(1,6))
bpy.context.window.scene=scene
scene.frame_set(577)
for area in bpy.context.screen.areas:
    if area.type=='VIEW_3D':
        area.spaces.active.region_3d.view_perspective='CAMERA'
        area.spaces.active.region_3d.view_camera_zoom=0
print(json.dumps({'ok':True,'scene':scene.name,'frame':scene.frame_current,'camera':scene.camera.name,'episode_scenes':5}))
