"""사용자 요청: 추천 리깅 적용. 기존 v002 캐릭터의 실제 형상/이름을 읽기 전용으로 조사한다."""
import json
from mathutils import Vector
folder=PROJECT_ROOT/'outputs/weather-rigs/v001';folder.mkdir(parents=True,exist_ok=True)
report={}
for key in ('Mongsil','Haerong','Ttorr','Songsong','Solsol'):
    collection=bpy.data.collections['WF2_'+key]
    root=bpy.data.objects['WF2_'+key+'_Root'];inverse=root.matrix_world.inverted()
    records=[]
    for obj in collection.objects:
        if obj==root:continue
        matrix=inverse@obj.matrix_world
        record={'name':obj.name.removeprefix('WF2_'),'type':obj.type,'center':list(matrix.translation),
                'bounds':[[float(v) for v in matrix@Vector(corner)] for corner in obj.bound_box],
                'vertices':len(obj.data.vertices) if obj.type=='MESH' else None}
        if obj.type=='CURVE':
            record['paths']=[[list(matrix@point.co) for point in spline.bezier_points] for spline in obj.data.splines]
        records.append(record)
    report[key]=records
(folder/'source-inspection.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
print(json.dumps({'ok':True,'characters':{k:len(v) for k,v in report.items()}}))
