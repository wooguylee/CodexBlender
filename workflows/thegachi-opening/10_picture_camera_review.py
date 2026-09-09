"""기준 그림 시각 QA: Y-up 건축 장면의 카메라 수평을 명시적으로 정렬한다."""
import json
from mathutils import Vector, Matrix

scene=bpy.context.scene
assert scene.name=='Thegachi_HousePerson_v004'
cam=scene.camera
before=list(cam.rotation_euler)
target=Vector((-.25,0,.15))
forward=(target-cam.location).normalized()
right=forward.cross(Vector((0,1,0))).normalized()
up=right.cross(forward).normalized()
cam.rotation_euler=Matrix((right,up,-forward)).transposed().to_euler()
assert abs(right.y)<.00001
# Close the small gap between the trouser hems and the shoes.
origin=Vector((1.20,-2.52,1.60))
for side,x in [('L',-.24),('R',.24)]:
    obj=scene.objects['HP_Person_trouser_'+side]
    a=origin+Vector((x,.24,0))
    b=origin+Vector((x*.66,1.24,0))
    old_length=(Vector((x*.66,1.24,0))-Vector((x,.35,0))).length
    obj.location=(a+b)/2
    obj.rotation_euler=(b-a).to_track_quat('Z','Y').to_euler()
    obj.scale.z=(b-a).length/old_length
scene.render.resolution_x,scene.render.resolution_y=1920,1080
scene.render.filepath='//../outputs/thegachi-opening/v004/house-person-picture-reviewed.png'
dest=PROJECT_ROOT/'scenes/thegachi-house-person-v004-reviewed.blend'
assert not dest.exists()
bpy.ops.wm.save_as_mainfile(filepath=str(dest),copy=True,relative_remap=True,compress=True)
report={'ok':True,'scene':scene.name,'camera_rotation_before':before,
        'camera_rotation_after':list(cam.rotation_euler),'screen_right_world_y':right.y,
        'source':'scenes/thegachi-house-person-v004-reviewed.blend',
        'legacy_video_untouched':True,'stage':'reference_picture_only'}
(OUTPUT_DIR/'camera-review.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
print(json.dumps(report))
