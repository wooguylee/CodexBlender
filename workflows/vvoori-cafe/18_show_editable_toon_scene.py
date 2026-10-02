"""사용자 Blender 창에서 실제 창틀/가구/차량을 편집할 수 있는 뷰 레이어를 표시."""
import bpy
scene=bpy.data.scenes['Vvoori_Cafe_v003'];bpy.context.window.scene=scene
bpy.context.window.view_layer=scene.view_layers['VC3_EditAll3D']
scene.frame_set(1)
for screen in bpy.data.screens:
    for area in screen.areas:
        if area.type=='VIEW_3D':area.spaces.active.region_3d.view_perspective='CAMERA'
print('Editable 3D view: VC3_EditAll3D. Production render layer: VC3_Motion.')
