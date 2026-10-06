"""브리찌: 검증에서 확인된 v002 복어 착석의 지느러미 높이만 재베이크."""
import sys,json,importlib
from pathlib import Path
import bpy
sys.path.insert(0,str(PROJECT_ROOT/'workflows/storybook-cast'))
import motions,exporting
importlib.reload(motions);importlib.reload(exporting)
out=PROJECT_ROOT/'outputs/storybook-cast/v002';manifest=out/'export-manifest.json'
report=json.loads(manifest.read_text(encoding='utf-8'));record=next(c for c in report['characters'] if c['key']=='BobaPuffer')
backup=out/'puffer-before-sit-fix';backup.mkdir(exist_ok=False)
(backup/'export-record.json').write_text(json.dumps(record,ensure_ascii=False,indent=2),encoding='utf-8')
for field in ('native','fbx'):
    source=(PROJECT_ROOT/record[field]).resolve()
    assert source.is_relative_to((PROJECT_ROOT/'exports/storybook-cast/v002').resolve())
    source.rename(backup/source.name)
rig=bpy.data.objects[record['rig']];rig.animation_data_clear()
for action in list(bpy.data.actions):
    if action.name.startswith('BobaPuffer_v002_'):bpy.data.actions.remove(action)
report['characters']=[c for c in report['characters'] if c['key']!='BobaPuffer'];report['ok']=False
manifest.write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
exporting.export_theme(PROJECT_ROOT,'Sea',version='v002')
