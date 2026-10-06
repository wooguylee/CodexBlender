"""Read-only to delivered assets: reproduce exposed/detached shoulder roots."""
import sys,json,importlib
from pathlib import Path
import bpy
ROOT=Path(__file__).resolve().parents[2];sys.path.insert(0,str(ROOT/'workflows/storybook-cast'))
from geometry import Builder
from catalog import THEMES
from shoulder_attachment import original_measurement
rows=[]
for theme,spec in THEMES.items():
    for key,_,_ in spec['characters']:
        builder=Builder(key,bpy.context.scene);importlib.import_module(spec['module']).build(builder,key);rows.append(original_measurement(builder,key))
checks=[s for c in rows for s in c['shoulders']]
report={'ok':all(s['root_fully_inside'] for s in checks),'shoulder_surface_samples_tested':len(checks),'exposed_surface_samples':sum(not s['root_fully_inside'] for s in checks),'tube_root_rings_tested':sum(s['sample_kind']=='tube_root_ring' for s in checks),'wing_surface_samples_tested':sum(s['sample_kind']=='wing_surface' for s in checks),'joint_centers_outside':sum(s['joint_signed_distance']>0 for s in checks),'characters':rows}
out=ROOT/'outputs/storybook-cast/v002';out.mkdir(parents=True,exist_ok=True);(out/'shoulders-before.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps({k:v for k,v in report.items() if k!='characters'}))
assert report['ok'],'Existing model shoulder roots fail torso containment; see shoulders-before.json'
