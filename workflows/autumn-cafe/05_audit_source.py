"""별도 Blender 프로세스에서 원본/보존 백업을 읽기 전용 점검한다."""
import bpy, json
from pathlib import Path
root=Path(__file__).resolve().parents[2]
paths=['outputs/jobs/20261002T045215-2dda65d6ee/before.blend','scenes/rainy-cafe-v002.blend','scenes/autumn-cafe-v001.blend']
report={}
for rel in paths:
    path=root/rel
    if not path.exists():continue
    with bpy.data.libraries.load(str(path),link=False) as (src,dst):
        report[rel]={'scene_names':list(src.scenes),'object_count':len(src.objects),'image_count':len(src.images),'bytes':path.stat().st_size}
(root/'outputs/autumn-cafe/v001/source-library-audit.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
print(json.dumps(report,indent=2))
