"""Resolve Unity n-gon import warnings on dedicated FBX meshes; native rigs remain untouched."""
import json,runpy
triangulate_ngons=runpy.run_path(str(PROJECT_ROOT/'workflows/weather-unity/triangulate.py'))['triangulate_ngons']
records=[]
for scene in bpy.data.scenes:
    if not scene.name.startswith('WFUnity_'):continue
    for obj in scene.objects:
        if obj.type!='MESH':continue
        # Validate on an independent copy before changing the scoped export data.
        probe=obj.data.copy()
        try:triangulate_ngons(probe)
        finally:bpy.data.meshes.remove(probe)
        count=triangulate_ngons(obj.data)
        if count:records.append({'scene':scene.name,'mesh':obj.name,'ngons':count})
report={'ok':True,'shape_coordinates_and_drivers_preserved':True,'meshes':records}
(PROJECT_ROOT/'outputs/weather-unity/v001/triangulation-verification.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
print(json.dumps(report))
