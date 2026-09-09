"""사용자 수정: 추출된 ㄷ/ㅊ에서 바로 더가치로 확장한다.

v006의 축소 퇴장과 기존 MP4 재등장을 없애고 하나의 8초 Blender 애니메이션으로 제작.
보행/손인사/추출 1~108프레임은 유지하며 기존 디스크 결과는 보존한다.
"""
import json
import math
from mathutils import Vector

scene = bpy.context.scene
assert scene.name == 'Thegachi_Opening_v006'
assert 'Thegachi_Opening_v007' not in bpy.data.scenes
out = PROJECT_ROOT / 'outputs/thegachi-opening/v007'
assert not out.exists()
out.mkdir(parents=True)
house = scene.objects['HP_BlueHouse_LogoContour']
person = scene.objects['HP_Extracted_Person_ch']
cam = scene.camera
assert cam.name == 'HP_Camera'
collection = house.users_collection[0]
original_objects = list(scene.objects)


def snapshot(frame):
    scene.frame_set(frame)
    return [v for obj in original_objects for row in obj.matrix_world for v in row] + [cam.data.ortho_scale, house.data.extrude]


before = {f: snapshot(f) for f in range(1, 109)}
scene.frame_set(108)
start = {obj.name: (obj.location.copy(), obj.scale.copy()) for obj in [house, person]}
start_ortho = cam.data.ortho_scale
scene.name = 'Thegachi_Opening_v007'
scene['output_version'] = 'v007'
scene['poster_frame'] = 176
scene['symbol_frame'] = 108
scene['review_frames'] = [25, 72, 96, 108, 132, 176]
scene['opening_duration_seconds'] = 8
scene['stage'] = 'Walk, overhead wave, extract symbols, expand directly to Thegachi wordmark, hold.'
scene['opening_story'] = '오른쪽에서 걷기 → 머리 위 손인사 → ㄷ/ㅊ 추출 → 곧바로 더가치 확장 → 홀드'
scene.frame_end = 192


def smooth(t):
    t = max(0., min(1., t))
    return t * t * (3 - 2 * t)


# Continue the same two visible objects from the exact extraction endpoint.
# No shrink-to-zero, replayed appearance, object swap, or cut to a second video.
for f in range(109, 193):
    scene.frame_set(f)
    t = smooth((f - 108) / 48)
    for obj, reference in [(house, 'TG_house_d'), (person, 'TG_person_ch')]:
        pos, scale = start[obj.name]
        obj.location = pos.lerp(Vector(bpy.data.objects[reference]['final_location']), t)
        obj.scale = scale.lerp(Vector((1, 1, 1)), t)
        obj.keyframe_insert('location', frame=f)
        obj.keyframe_insert('scale', frame=f)
    cam.data.ortho_scale = start_ortho + (12.7 - start_ortho) * t
    cam.data.keyframe_insert('ortho_scale', frame=f)

# Reuse the actual brand's four remaining vector shapes, independent of the old scene.
letters = []
for name, begin in [('eo', 116), ('g', 120), ('a', 124), ('i', 128)]:
    source = bpy.data.objects['TG_' + name]
    obj = bpy.data.objects.new('HP_Wordmark_' + name, source.data.copy())
    collection.objects.link(obj)
    obj.data.animation_data_clear()
    end = Vector(source['final_location'])
    for f in range(1, 193):
        t = smooth((f - begin) / 24)
        obj.location = end + Vector((0, -.24 * (1 - t), -.10 * (1 - t)))
        obj.rotation_euler = (0, math.radians(-12) * (1 - t), 0)
        obj.scale = (max(.0001, t),) * 3
        obj.hide_render = f <= begin
        for path in ['location', 'rotation_euler', 'scale', 'hide_render']:
            obj.keyframe_insert(path, frame=f)
    letters.append(obj)

# Timeline labels now describe a single continuous eight-second film.
scene.timeline_markers.clear()
for f, label in [(1, '01 오른쪽에서 걷기'), (54, '02 도착과 손인사'),
                 (88, '03 ㄷ/ㅊ 추출'), (108, '04 곧바로 더가치 확장'),
                 (156, '05 더가치 완성'), (192, '06 마무리')]:
    scene.timeline_markers.new(label, frame=f)

max_early_error = max(abs(a - b) for f, values in before.items() for a, b in zip(values, snapshot(f)))
assert max_early_error < 1e-5, max_early_error
minimum_scale = 100.
for f in range(108, 193):
    scene.frame_set(f)
    minimum_scale = min(minimum_scale, *house.scale, *person.scale)
    assert not house.hide_render and not person.hide_render
assert minimum_scale >= .9999, minimum_scale
for obj, reference in [(house, 'TG_house_d'), (person, 'TG_person_ch')]:
    assert (obj.location - Vector(bpy.data.objects[reference]['final_location'])).length < 1e-5
assert all(not obj.hide_render for obj in letters)

review = out / 'storyboard'
review.mkdir()
scene.render.resolution_x, scene.render.resolution_y = 960, 540
scene.render.resolution_percentage = 100
for f in [108, 120, 132, 144, 156, 176]:
    scene.frame_set(f)
    scene.render.filepath = str(review / f'frame-{f:03d}.png')
    bpy.ops.render.render(write_still=True)
scene.frame_set(176)
scene.render.filepath = '//../outputs/thegachi-opening/v007/preview.png'
report = {'ok': True, 'frames': 192, 'seconds': 8, 'fps': 24,
          'preserved_first_frames': 108, 'maximum_early_transform_error': max_early_error,
          'direct_expansion_frames': [108, 156], 'minimum_symbol_scale_during_expansion': minimum_scale,
          'same_house_and_person_objects': [house.name, person.name],
          'separate_video_join': False, 'final_hold_frames': [156, 192],
          'previous_v006_preserved_on_disk': True}
(out / 'continuity-verification.json').write_text(json.dumps(report, indent=2), encoding='utf-8')
print(json.dumps(report))
