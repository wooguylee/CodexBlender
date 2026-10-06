"""해마의 꼬리 접지로 상쇄되던 휴식 자세를 몸통 수축으로 보완한다."""
import bpy,sys,json,importlib,shutil
from pathlib import Path
root=Path(PROJECT_ROOT);folder=root/'workflows/storybook-cast'
if str(folder) not in sys.path:sys.path.insert(0,str(folder))
import motions,exporting
importlib.reload(motions);importlib.reload(exporting)
path=root/'outputs/storybook-cast/v001/export-manifest.json'
report=json.loads(path.read_text(encoding='utf-8'));record=next(c for c in report['characters'] if c['key']=='HaniSeahorse')
backup=root/'outputs/storybook-cast/v001/revisions/HaniSeahorse-initial';backup.mkdir(parents=True,exist_ok=False)
for field in ('native','fbx'):
    source=(root/record[field]).resolve();assert source.is_relative_to((root/'exports/storybook-cast/v001').resolve())
    shutil.move(str(source),str(backup/source.name))
shutil.copy2(path,backup/'export-manifest.json')
report['characters']=[c for c in report['characters'] if c['key']!='HaniSeahorse'];report['ok']=False;path.write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
rig=bpy.data.objects['HaniSeahorse_Rig'];rig.animation_data.action=None
for action in list(bpy.data.actions):
    if action.name.startswith('HaniSeahorse_'):bpy.data.actions.remove(action)
exporting.export_theme(root,'Sea')
