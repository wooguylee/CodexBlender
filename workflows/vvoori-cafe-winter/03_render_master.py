"""1920x1080/24fps 480장 실제 렌더. 마지막 프레임 복사/홀드 없이 정확히 20초."""
import bpy, json, time, shutil
scene=bpy.data.scenes['Vvoori_Cafe_Winter_v001'];bpy.context.window.scene=scene
out=PROJECT_ROOT/'outputs/vvoori-cafe-winter/v001'
frames=out/'master-frames';frames.mkdir(exist_ok=True)
assert not list(frames.glob('*.png')),'Existing frames preserved: use a new version or an explicit recovery script'
assert json.loads((out/'motion-audit.json').read_text())['ok']
scene.render.resolution_percentage=100;scene.render.resolution_x=1920;scene.render.resolution_y=1080
scene.render.fps=24;scene.frame_start=1;scene.frame_end=480
scene.cycles.samples=16;scene.cycles.use_denoising=False;scene.cycles.use_animated_seed=False
scene.render.dither_intensity=0
start=time.monotonic()
for frame in range(1,481):
    scene.frame_set(frame);scene.render.filepath=str(frames/f'{frame:04d}.png')
    bpy.ops.render.render(write_still=True)
    elapsed=time.monotonic()-start
    (out/'render-progress.json').write_text(json.dumps({'frame':frame,'total':480,
        'elapsed_seconds':round(elapsed,1),'estimated_remaining_seconds':round(elapsed/frame*(480-frame),1)}),encoding='utf-8')
scene.frame_set(481);scene.render.filepath=str(out/'independent-next-cycle.png')
bpy.ops.render.render(write_still=True)
shutil.copyfile(frames/'0001.png',out/'poster-fullhd.png')
scene.frame_set(1);scene.render.filepath='//../outputs/vvoori-cafe-winter/v001/master-frames/'
path=PROJECT_ROOT/'scenes/vvoori-cafe-winter-v001.blend';assert not path.exists()
bpy.data.libraries.write(str(path),{scene},path_remap='RELATIVE_ALL',fake_user=True,compress=True)
report={'ok':True,'width':1920,'height':1080,'fps':24,'frames':480,'duration_seconds':20,
        'rendered_frame_range':[1,480],'duplicated_endpoint':False,'verification_only_frame':481,
        'samples':16,'seconds':round(time.monotonic()-start,2),'source':path.relative_to(PROJECT_ROOT).as_posix()}
(out/'render-report.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
print(json.dumps(report,indent=2))
