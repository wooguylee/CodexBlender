"""브리찌로 다섯 편의 독립 Scene, 소품, 연기 키프레임, 원본을 제작한다."""
import hashlib
import importlib
import json
import math
import sys
import time
sys.path.insert(0,str(PROJECT_ROOT/'workflows/weather-shorts'))
import production, stories
importlib.reload(production);importlib.reload(stories)
from production import Production, KEYS, FPS

out=PROJECT_ROOT/'outputs/weather-shorts/v001'
out.mkdir(parents=True,exist_ok=True)
existing={}
for path in (PROJECT_ROOT/'scenes').glob('*.blend'):
    if path.name!='current.blend' and not path.name.startswith('weather-short-'):
        existing[path.relative_to(PROJECT_ROOT).as_posix()]=hashlib.sha256(path.read_bytes()).hexdigest()
before={s.name: {'camera':s.camera.name if s.camera else None,
                  'objects':{o.name:[float(v) for row in o.matrix_world for v in row] for o in s.objects}}
        for s in bpy.data.scenes if not s.name.startswith('Weather_Short_')}


def linear_keys():
    for action in bpy.data.actions:
        if not action.name.startswith('WS'):continue
        curves=[]
        if hasattr(action,'fcurves'):curves.extend(action.fcurves)
        for layer in action.layers:
            for strip in layer.strips:
                if hasattr(strip,'channelbags'):
                    for bag in strip.channelbags:curves.extend(bag.fcurves)
        for curve in curves:
            for point in curve.keyframe_points:point.interpolation='LINEAR'


records=[]
for episode in stories.EPISODES:
    started=time.monotonic()
    p=Production(PROJECT_ROOT,episode['id'],episode['title'],episode['duration'])
    props=stories.prepare(p,episode)
    folder=out/episode['slug'];folder.mkdir(parents=True,exist_ok=True)
    # Keyframe at 12 Hz with linear interpolation; render at native 24 fps.
    frames=list(range(1,p.scene.frame_end+1,2))
    if frames[-1]!=p.scene.frame_end:frames.append(p.scene.frame_end)
    tracks=[]
    for frame in frames:
        p.scene.frame_set(frame)
        p.reset();t=(frame-1)/FPS
        stories.TICKS[episode['id']](p,props,t)
        for obj in p.dynamic:
            assert all(math.isfinite(v) for v in (*obj.location,*obj.rotation_euler,*obj.scale)),obj.name
        p.keyframe(frame)
        tracks.append({'frame':frame,'roots':{k:list(p.controls[k]['root'].location) for k in KEYS}})
    linear_keys()
    p.scene.frame_set(1)
    bpy.context.view_layer.update()
    p.scene.render.filepath='//../outputs/weather-shorts/v001/'+episode['slug']+'/frames/frame-'
    p.scene['episode_slug']=episode['slug']
    p.scene['duration_seconds']=episode['duration']
    p.scene['animation_method']='Baked root, limb, expression and prop controls; linear interpolation at 24 fps.'
    source=PROJECT_ROOT/'scenes'/f"weather-short-{episode['id']:02d}-v001.blend"
    assert not source.exists()
    bpy.data.libraries.write(str(source),{p.scene},path_remap='RELATIVE',fake_user=True,compress=True)
    record={**episode,'scene':p.scene.name,'camera':p.scene.camera.name,'frames':p.scene.frame_end,
            'resolution':[1920,1080],'fps':FPS,'engine':p.scene.render.engine,'samples':16,
            'objects':len(p.scene.objects),'animated_objects':len(p.dynamic),
            'source':source.relative_to(PROJECT_ROOT).as_posix(),'bake_seconds':time.monotonic()-started}
    (folder/'story.json').write_text(json.dumps(record,indent=2,ensure_ascii=False),encoding='utf-8')
    (folder/'trajectories.json').write_text(json.dumps(tracks,separators=(',',':')),encoding='utf-8')
    records.append(record)
    print(json.dumps({'built':episode['slug'],'objects':record['objects'],'frames':record['frames']},ensure_ascii=False))
for name,state in before.items():
    s=bpy.data.scenes[name]
    assert state=={'camera':s.camera.name if s.camera else None,
                   'objects':{o.name:[float(v) for row in o.matrix_world for v in row] for o in s.objects}},name
report={'ok':True,'episodes':records,'existing_source_sha256':existing,'preserved_scenes':list(before)}
(out/'production-manifest.json').write_text(json.dumps(report,indent=2,ensure_ascii=False),encoding='utf-8')
bpy.context.window.scene=bpy.data.scenes[records[0]['scene']]
bpy.context.scene.frame_set(1)
print(json.dumps({'ok':True,'episodes':len(records),'total_frames':sum(r['frames'] for r in records)}))
