"""32-bit Blender Vector의 미소 각도 오차 허용 후, 구도 가이드 출력만 이어서 완료."""
import bpy, math, json
from mathutils import Vector
from bpy_extras.object_utils import world_to_camera_view
root=PROJECT_ROOT;out=root/'outputs/vvoori-cafe/v003'
scene=bpy.data.scenes['Vvoori_Cafe_v003'];cam=scene.camera
traffic=bpy.data.collections['VC3_Traffic'];leaves=bpy.data.collections['VC3_Leaves']
window=bpy.data.collections['VC3_WindowSet'];foreground=bpy.data.collections['VC3_Foreground']
rig=bpy.data.collections['VC3_Rig'];guides=bpy.data.collections['VC3_Guides']
assert len(guides.objects)==0
direction=cam.rotation_euler.to_matrix()@Vector((0,0,-1))
angle=math.degrees(math.atan2(direction.x,direction.y));assert abs(angle-50)<1e-4
code=(root/'workflows/vvoori-cafe/11_build_oblique_toon_layout.py').read_text(encoding='utf-8')
helpers=code[code.index('def flat('):code.index('# Independent copies')]
tail=code[code.index('# Temporary layout geometry'):]
exec(compile(helpers,'11_layout:helpers','exec'),globals())
exec(compile(tail,'11_layout:finish','exec'),globals())
