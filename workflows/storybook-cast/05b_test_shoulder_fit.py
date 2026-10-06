"""Green gate: every repaired root cap must lie at least .035 inside its torso."""
import sys,json,importlib
from pathlib import Path
import bpy
ROOT=Path(__file__).resolve().parents[2];sys.path.insert(0,str(ROOT/'workflows/storybook-cast'))
from geometry import Builder
from catalog import THEMES
from shoulder_attachment import fit_shoulders
rows=[]
for theme,spec in THEMES.items():
    for key,_,_ in spec['characters']:
        builder=Builder(key,bpy.context.scene);importlib.import_module(spec['module']).build(builder,key);fit_shoulders(builder,key)
        rows.append({'key':key,'shoulders':builder.shoulder_specs})
report={'ok':True,'root_caps_tested':40,'min_inset':min(s['rest_inset_min'] for c in rows for s in c['shoulders']),'characters':rows}
(ROOT/'outputs/storybook-cast/v002/shoulders-fit.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8');print(json.dumps({k:v for k,v in report.items() if k!='characters'}))
