"""영상 출력 전, 등장/심벌/펼치기/완성/조명 이동의 실제 렌더와 장면을 검증한다."""
import json
import time
from mathutils import Vector

scene = bpy.context.scene
version = scene.get('output_version', 'v001')
assert scene.name == 'Thegachi_Opening_' + version
out = PROJECT_ROOT / 'outputs/thegachi-opening' / version
folder = out / 'storyboard'
folder.mkdir(parents=True, exist_ok=True)
assert not list(folder.glob('*.png')), 'Review output already exists; use a new version.'
scene.render.resolution_x, scene.render.resolution_y = 960,540
scene.render.image_settings.file_format = 'PNG'
report = {'scene':scene.name,'samples':[],'original_scene_preserved':'Scene' in bpy.data.scenes}
for frame in [14,34,60,82,104,120]:
    scene.frame_set(frame)
    scene.render.filepath = str(folder / f'frame-{frame:03d}.png')
    start = time.monotonic()
    bpy.ops.render.render(write_still=True)
    report['samples'].append({'frame':frame,'render_seconds':round(time.monotonic()-start,3),
                              'file':f'storyboard/frame-{frame:03d}.png'})
scene.frame_set(144)
for name in ['house_d','person_ch','eo','g','a','i']:
    obj = scene.objects['TG_'+name]
    assert (obj.location-Vector(obj['final_location'])).length < .00001, name
    assert (obj.scale-Vector((1,1,1))).length < .00001, name
    assert obj.animation_data and obj.animation_data.action
report['final_original_vector_layout_verified'] = True
report['external_dependencies'] = [{'name':i.name,'path':i.filepath} for i in bpy.data.images if i.source=='FILE' and i.users]
scene.render.resolution_x, scene.render.resolution_y = 1280,720
scene.frame_set(120)
scene.render.filepath = f'//../outputs/thegachi-opening/{version}/preview.png'
(out/'keyframe-verification.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps(report,ensure_ascii=False))
