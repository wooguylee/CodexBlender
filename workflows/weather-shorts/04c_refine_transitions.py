"""경계 시각에 기본 위치로 복귀하던 조건문을 수정하고 기존 제작 Scene의 연기만 다시 굽는다."""
import hashlib, importlib, json, math, shutil, sys
sys.path.insert(0,str(PROJECT_ROOT/'workflows/weather-shorts'))
import production,stories
importlib.reload(production);importlib.reload(stories)
from production import Production,KEYS,FPS

out=PROJECT_ROOT/'outputs/weather-shorts/v001'
audit=[]
for episode in stories.EPISODES:
    n=episode['id'];p=Production.__new__(Production)
    p.root=PROJECT_ROOT;p.number=n;p.prefix=f'WS{n}_';p.name=f'Weather_Short_{n:02d}_v001'
    p.scene=bpy.data.scenes[p.name];bpy.context.window.scene=p.scene;p.scene.frame_set(1)
    p.base={};p.dynamic=set();p.events=[]
    p.collection=bpy.data.collections[p.prefix+'Stage']
    p.characters={k:bpy.data.collections[p.prefix+k] for k in KEYS}
    p.objects={o.name.removeprefix(p.prefix):o for o in p.scene.objects}
    p.controls={k:{ctl:p.objects[k+'_'+('Root' if ctl=='root' else ctl)] for ctl in ('root','armL','armR','legL','legR')} for k in KEYS}
    p.shadows={k:p.objects[k+'_GroundShadow'] for k in KEYS}
    p.bind_rest()
    obj=lambda name:p.objects[name]
    seq=lambda name,count:[obj(name+str(i)) for i in range(count)]
    props={}
    if n in (1,2,4,5):props['gusts']=seq('Gust_',4)
    if n in (1,2,4):props['zzz']=seq('Zzz',3)
    if n==1:props['numbers']=[obj('Countdown'+str(i)) for i in (3,2,1)]
    if n==2:props.update(star=obj('Mongsil_HuggedStar'),ice=obj('IceSlide'),sparkles=seq('IceSparkle',12))
    if n==3:
        props.update(rain=seq('FlowerRain',26),snow=seq('FlowerSnow',18),heat=seq('Heat_',3),puddle=obj('FlowerPuddle'),
                     flower=obj('FlowerRoot'),head=obj('FlowerHead'),petals=seq('Petal',8),crystals=seq('IceCrystal',6),pollen=seq('Pollen',45),tints=[])
        for material in stories.bpy_materials(p):
            if any(x in material.name for x in ('Cloud_marshmallow','Sun_butter','Sun_mango','Raindrop_blue','Snow_pearl','Snow_branches','Wind_mint')):
                inp=material.node_tree.nodes['Principled BSDF'].inputs['Base Color'];props['tints'].append((inp,tuple(inp.default_value)))
    if n==4:props.update(rain=seq('StudioRain',42),snow=seq('StudioSnow',35))
    if n==5:props.update(bubble=obj('BigBubble'),hats=seq('BubbleHat',5),burst=seq('BubbleBurst',20),crystals=obj('Songsong_CrystalControl'))
    folder=out/episode['slug'];source=PROJECT_ROOT/f'scenes/weather-short-{n:02d}-v001.blend'
    backup=folder/'source-before-transition-review.blend';assert not backup.exists();shutil.copy2(source,backup)
    shutil.copy2(folder/'trajectories.json',folder/'trajectories-before-transition-review.json')
    frames=list(range(1,p.scene.frame_end+1,2))
    if frames[-1]!=p.scene.frame_end:frames.append(p.scene.frame_end)
    tracks=[]
    for frame in frames:
        p.scene.frame_set(frame);p.reset();stories.TICKS[n](p,props,(frame-1)/FPS);p.keyframe(frame)
        tracks.append({'frame':frame,'roots':{k:list(p.controls[k]['root'].location) for k in KEYS}})
    for action in bpy.data.actions:
        if not action.name.startswith(p.prefix):continue
        for layer in action.layers:
            for strip in layer.strips:
                for bag in strip.channelbags:
                    for curve in bag.fcurves:
                        for point in curve.keyframe_points:point.interpolation='LINEAR'
    p.scene.frame_set(1)
    bpy.data.libraries.write(str(source),{p.scene},path_remap='RELATIVE',fake_user=True,compress=True)
    if (folder/'native-source.json').exists():(folder/'native-source.json').replace(folder/'native-source-before-transition-review.json')
    (folder/'trajectories.json').write_text(json.dumps(tracks,separators=(',',':')),encoding='utf-8')
    deltas=[];accelerations=[]
    for a,b in zip(tracks,tracks[1:]):
        for key in KEYS:deltas.append((math.dist(a['roots'][key],b['roots'][key]),(b['frame']-1)/FPS,key))
    for a,b,c in zip(tracks,tracks[1:],tracks[2:]):
        for key in KEYS:
            values=[c['roots'][key][i]-2*b['roots'][key][i]+a['roots'][key][i] for i in range(3)]
            accelerations.append((math.sqrt(sum(v*v for v in values)),(b['frame']-1)/FPS,key))
    largest=sorted(deltas,reverse=True)[:5];jerks=sorted(accelerations,reverse=True)[:5]
    # 12 Hz source keys: permits the deliberate fast studio entrance and cloud closeup.
    assert largest[0][0]<(.72 if n==4 else .50),(n,largest)
    assert jerks[0][0]<.35,(n,jerks)
    audit.append({'id':n,'maximum_two_frame_displacements':largest,'maximum_second_differences':jerks})
(out/'transition-review.json').write_text(json.dumps({'ok':True,'episodes':audit,'fix':'Continuous approach/return envelopes and inclusive timing boundaries.'},indent=2),encoding='utf-8')
bpy.context.window.scene=bpy.data.scenes['Weather_Short_01_v001'];bpy.context.scene.frame_set(241)
print(json.dumps({'ok':True,'episodes':5,'transition_audit':audit}))
