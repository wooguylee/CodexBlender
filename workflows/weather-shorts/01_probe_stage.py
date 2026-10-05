"""브리찌: 기존 캐릭터를 복제한 제작 무대의 실제 렌더 성능/가시성 시험."""
import json
import sys
import time
sys.path.insert(0, str(PROJECT_ROOT / 'workflows/weather-shorts'))
from production import Production, KEYS

p = Production(PROJECT_ROOT, 0, '제작 무대 시험', 1)
for i,key in enumerate(KEYS):
    p.pose(key, (i-2)*2.8, arms=(.10,-.10))
out = PROJECT_ROOT / 'outputs/weather-shorts/v001/probe'
out.mkdir(parents=True,exist_ok=True)
times = {}
for engine in ('CYCLES','CYCLES'):
    # A repeated Cycles frame also proves deterministic static background pixels.
    index = len(times)
    p.scene.render.engine = engine
    p.scene.render.filepath = str(out / f'cycles-{index}.png')
    start=time.monotonic()
    bpy.ops.render.render(write_still=True)
    times[f'{engine}-{index}'] = time.monotonic()-start
p.scene.render.engine = 'CYCLES'
(out/'probe.json').write_text(json.dumps({'ok':True,'times_seconds':times,'objects':len(p.scene.objects)},indent=2),encoding='utf-8')
print(json.dumps(times))
