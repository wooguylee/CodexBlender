"""독립 Blender에서 원본 검증, 사건별 그림 또는 전체 프레임 렌더. 완료는 파일로 증명한다."""
from pathlib import Path
import argparse, hashlib, json, math, sys, time
import bpy

parser=argparse.ArgumentParser()
parser.add_argument('--mode',choices=['storyboard','full'],required=True)
args=parser.parse_args(sys.argv[sys.argv.index('--')+1:])
root=Path(__file__).resolve().parents[2]
scene=bpy.context.scene
assert len(bpy.data.scenes)==1
slug=scene['episode_slug'];folder=root/'outputs/weather-shorts/v001'/slug
story=json.loads((folder/'story.json').read_text(encoding='utf-8'))
assert scene.name==story['scene'] and len(scene.objects)==story['objects']
assert (scene.render.resolution_x,scene.render.resolution_y,scene.render.fps)==(1920,1080,24)
assert scene.frame_end==story['frames']
assert not bpy.data.libraries
assert not any(i.source=='FILE' and not i.packed_file for i in bpy.data.images)
assert all(font.filepath=='<builtin>' for font in bpy.data.fonts)
assert len([o for o in scene.objects if o.name.endswith('_Root')])==5
assert len([o for o in scene.objects if o.animation_data])>=25
original_range=(scene.frame_start,scene.frame_end)
scene.frame_set(1)
source=Path(bpy.data.filepath)
# Normalize the Scene-library export into a standalone native file once.
if not (folder/'native-source.json').exists():
    for screen in bpy.data.screens:
        for area in screen.areas:
            if area.type=='VIEW_3D':area.spaces.active.region_3d.view_perspective='CAMERA'
    bpy.ops.wm.save_as_mainfile(filepath=str(source),check_existing=False,compress=True,relative_remap=True)
    (folder/'native-source.json').write_text(json.dumps({'ok':True,'scene':scene.name,'objects':len(scene.objects),
        'frames':scene.frame_end,'independent_reopen':True,'external_dependencies':[]},indent=2),encoding='utf-8')

started=time.monotonic()
if args.mode=='storyboard':
    scene.render.resolution_x=960;scene.render.resolution_y=540
    scene.eevee.taa_render_samples=16
    dest=folder/'storyboard';dest.mkdir(exist_ok=True)
    samples=[]
    for second in story['beats']:
        frame=int(second*24)+1;scene.frame_set(frame)
        for obj in scene.objects:
            assert all(math.isfinite(v) for v in (*obj.location,*obj.rotation_euler,*obj.scale)),obj.name
        path=dest/f'beat-{second:02d}.png'
        scene.render.filepath=str(path)
        bpy.ops.render.render(write_still=True)
        samples.append({'second':second,'frame':frame,'image':path.relative_to(root).as_posix()})
    (folder/'storyboard-verification.json').write_text(json.dumps({'ok':True,'samples':samples,
        'seconds':time.monotonic()-started},indent=2),encoding='utf-8')
else:
    dest=folder/'frames';dest.mkdir(exist_ok=True)
    source_hash=hashlib.sha256(source.read_bytes()).hexdigest()
    identity=folder/'render-source.json'
    if identity.exists():assert json.loads(identity.read_text(encoding='utf-8'))['sha256']==source_hash, 'Source changed; archive earlier frames before rendering.'
    else:identity.write_text(json.dumps({'source':source.relative_to(root).as_posix(),'sha256':source_hash},indent=2),encoding='utf-8')
    scene.render.filepath=str(dest/'frame-')
    scene.render.image_settings.compression=15
    scene.render.use_overwrite=False
    scene.render.use_placeholder=False
    scene.frame_step=1
    # Incomplete writes are archived before resuming, so Blender can replace them.
    existing=set()
    for path in dest.glob('frame-*.png'):
        valid=False
        if path.stat().st_size>1000:
            with path.open('rb') as stream:
                signature=stream.read(8);stream.seek(-12,2);ending=stream.read()
            valid=signature==b'\x89PNG\r\n\x1a\n' and ending==b'\x00\x00\x00\x00IEND\xaeB`\x82'
        if valid:existing.add(int(path.stem.removeprefix('frame-')))
        else:
            rejected=folder/'incomplete-frames';rejected.mkdir(exist_ok=True)
            path.replace(rejected/(path.stem+'-'+str(time.time_ns())+'.png'))
    remaining=[f for f in range(1,story['frames']+1) if f not in existing]
    if remaining:
        scene.frame_start=min(remaining);scene.frame_end=max(remaining)
        def progress(s):
            if s.frame_current%24==0 or s.frame_current==s.frame_end:
                payload={'state':'rendering','frame':s.frame_current,'total':story['frames'],
                         'elapsed_seconds':round(time.monotonic()-started,2)}
                temp=folder/'render-progress.tmp'
                temp.write_text(json.dumps(payload),encoding='utf-8');temp.replace(folder/'render-progress.json')
        bpy.app.handlers.render_write.append(progress)
        bpy.ops.render.render(animation=True)
        bpy.app.handlers.render_write.remove(progress)
    actual=sorted(dest.glob('frame-*.png'))
    assert len(actual)==story['frames'],(len(actual),story['frames'])
    assert all(p.stat().st_size>1000 for p in actual)
    report={'ok':True,'state':'rendered','frames':len(actual),'resolution':[1920,1080],
            'fps':24,'seconds':time.monotonic()-started,'reused_frames':len(existing),
            'independent_native_source':True,'engine':scene.render.engine,'samples':scene.eevee.taa_render_samples}
    (folder/'render-result.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
    (folder/'render-progress.json').write_text(json.dumps(report),encoding='utf-8')
print(json.dumps({'ok':True,'episode':slug,'mode':args.mode,'seconds':time.monotonic()-started}))
