"""심벌이 벌어져 공간이 생긴 뒤 나머지 글자를 드러내 겹침을 줄인다."""
import json
import math
from mathutils import Vector

scene = bpy.context.scene
assert scene.name == 'Thegachi_Opening_v007'
out = PROJECT_ROOT / 'outputs/thegachi-opening/v007'


def ease(t):
    t = max(0., min(1., t))
    return t * t * (3 - 2 * t)


for name, begin in [('eo', 132), ('g', 128), ('a', 132), ('i', 136)]:
    obj = scene.objects['HP_Wordmark_' + name]
    end = Vector(bpy.data.objects['TG_' + name]['final_location'])
    for f in range(1, 193):
        t = ease((f - begin) / 20)
        obj.location = end + Vector((0, -.24 * (1 - t), -.10 * (1 - t)))
        obj.rotation_euler = (0, math.radians(-12) * (1 - t), 0)
        obj.scale = (max(.0001, t),) * 3
        obj.hide_render = f <= begin
        for path in ['location', 'rotation_euler', 'scale', 'hide_render']:
            obj.keyframe_insert(path, frame=f)
review = out / 'reveal-review'
review.mkdir(exist_ok=True)
for f in [132, 144, 156]:
    scene.frame_set(f)
    scene.render.filepath = str(review / f'frame-{f:03d}.png')
    bpy.ops.render.render(write_still=True)
scene.frame_set(176)
scene.render.filepath = '//../outputs/thegachi-opening/v007/preview.png'
print(json.dumps({'ok': True, 'letter_reveal_frames': [128, 156], 'purpose': 'Create room before revealing remaining letters.'}))
