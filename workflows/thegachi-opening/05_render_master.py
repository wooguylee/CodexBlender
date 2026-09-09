"""4단계: 승인된 오프닝을 Full HD PNG 시퀀스로 출력. MP4 인코딩은 다음 스크립트."""
import json
import time

scene = bpy.context.scene
version = scene.get('output_version', 'v001')
assert scene.name == 'Thegachi_Opening_' + version
out = PROJECT_ROOT/'outputs/thegachi-opening'/version
frames = out/'frames'
frames.mkdir(parents=True,exist_ok=True)
assert not list(frames.glob('*.png')), 'Frames already exist; inspect or create a new version.'
scene.render.resolution_x, scene.render.resolution_y = 1920,1080
scene.render.resolution_percentage = 100
scene.render.image_settings.file_format = 'PNG'
scene.render.image_settings.color_mode = 'RGB'
scene.render.image_settings.color_depth = '8'
scene.render.image_settings.compression = 20
scene.render.fps = 24
scene.render.fps_base = 1
scene.render.use_file_extension = True
scene.frame_start = 1
total = scene.frame_end
if hasattr(scene,'eevee') and hasattr(scene.eevee,'taa_render_samples'):
    scene.eevee.taa_render_samples = 64
started = time.monotonic()
for frame in range(1,total+1):
    scene.frame_set(frame)
    if scene.get('transition_samples') and hasattr(scene,'eevee'):
        scene.eevee.taa_render_samples=int(scene['transition_samples']) if 89<=frame<=108 else 64
    scene.render.filepath = str(frames/f'{frame:04d}.png')
    bpy.ops.render.render(write_still=True)
    if frame % 12 == 0:
        (out/'render-progress.json').write_text(json.dumps({'frame':frame,'total':total,
            'elapsed_seconds':round(time.monotonic()-started,2)}),encoding='utf-8')
        print(f'Rendered {frame}/{total}',flush=True)
assert len(list(frames.glob('*.png'))) == total
scene.frame_set(scene.get('poster_frame',120))
scene.render.filepath = f'//../outputs/thegachi-opening/{version}/frames/'
dest = PROJECT_ROOT/'scenes'/f'thegachi-opening-{version}.blend'
assert not dest.exists(), 'Named source exists; do not overwrite.'
bpy.ops.wm.save_as_mainfile(filepath=str(dest),copy=True,relative_remap=True,compress=True)
report = {'ok':True,'frames':total,'width':1920,'height':1080,'fps':24,'seconds':total/24,
          'transition_samples':scene.get('transition_samples',64),
          'poster_frame':scene.get('poster_frame',120),'symbol_frame':scene.get('symbol_frame',34),
          'review_frames':list(scene.get('review_frames',[14,34,60,82,104,120])),
          'render_seconds':round(time.monotonic()-started,2),'engine':scene.render.engine,
          'scene':scene.name,'source':f'scenes/thegachi-opening-{version}.blend',
          'preserved_scenes':[s.name for s in bpy.data.scenes]}
(out/'render-result.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps(report,ensure_ascii=False))
