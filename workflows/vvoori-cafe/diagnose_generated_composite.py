"""Blender 5.2의 공유 Math 노드와 Set Alpha 속성을 실제 RNA에서 확인."""
import bpy
import json
scene = bpy.data.scenes['Vvoori_Cafe_v002']
ng = scene.compositing_node_group
report = {}
for node_type in ['ShaderNodeMath', 'CompositorNodeSetAlpha']:
    node = ng.nodes.new(node_type)
    report[node_type] = {'properties': [p.identifier for p in node.bl_rna.properties],
                        'inputs': [{'name': s.name, 'type': s.type, 'value': str(getattr(s, 'default_value', None))} for s in node.inputs]}
    ng.nodes.remove(node)
(PROJECT_ROOT/'outputs/vvoori-cafe/v002/node-api.json').write_text(json.dumps(report, indent=2), encoding='utf-8')
print(json.dumps(report, indent=2))
