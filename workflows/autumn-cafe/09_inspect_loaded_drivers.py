"""라이브러리 방식으로 저장된 원본의 초기 depsgraph 평가를 진단한다."""
import bpy,json
from pathlib import Path
scene=bpy.data.scenes['Autumn_Cafe_v001'];bpy.context.window.scene=scene
bpy.context.window.view_layer=scene.view_layers['MovingLeavesAndTraffic']
objs=[o for o in scene.objects if o.animation_data and o.animation_data.drivers]
report={'scene':scene.name,'frames':{},'deltas':{}}
for tag,f in [('initial',1),('middle',241),('end',480),('repeat',1),('warmend',480)]:
    scene.frame_set(f);bpy.context.view_layer.update();deps=bpy.context.evaluated_depsgraph_get();deps.update()
    report['frames'][tag]={o.name:{'matrix':[float(v) for r in o.evaluated_get(deps).matrix_world for v in r],'location':list(o.location),'valid':[d.is_valid for d in o.animation_data.drivers]} for o in objs}
for k in report['frames']['initial']:
    aa=report['frames']['initial'][k]['matrix'];bb=report['frames']['end'][k]['matrix'];cc=report['frames']['repeat'][k]['matrix']
    d=max(abs(x-y) for x,y in zip(aa,bb));dd=max(abs(x-y) for x,y in zip(bb,cc))
    if d>1e-5 or dd>1e-5:report['deltas'][k]={'initial_end':d,'end_repeat':dd}
root=Path(__file__).resolve().parents[2];(root/'outputs/autumn-cafe/v001/loaded-driver-diagnosis.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
print(json.dumps(report['deltas'],indent=2))
