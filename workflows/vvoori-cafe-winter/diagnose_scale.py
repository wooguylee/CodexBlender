"""1672x941와 1920x1080 사이 반 픽셀 경계 alpha의 원인을 실제 노드에서 확인."""
import bpy,json
scene=bpy.data.scenes['Vvoori_Cafe_Winter_v001']
data={}
for key in ['Park_Fit','Cafe_Fit']:
    node=scene.compositing_node_group.nodes[key]
    data[key]={'inputs':{s.name:str(getattr(s,'default_value',None)) for s in node.inputs},
        'properties':{p.identifier:str(getattr(node,p.identifier)) for p in node.bl_rna.properties if p.identifier in ['space','frame_method','relative','filter_type']}}
(PROJECT_ROOT/'outputs/vvoori-cafe-winter/v001/scale-diagnosis.json').write_text(json.dumps(data,indent=2),encoding='utf-8')
print(json.dumps(data,indent=2))
