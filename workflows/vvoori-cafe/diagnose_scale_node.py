"""Blender 5.2 compositor Scale API의 실제 속성과 입력을 읽기 전용 조회."""
import bpy
import json

node = bpy.context.scene.compositing_node_group.nodes['01_ParkBackground_FitRenderSize']
report = {'properties': [p.identifier for p in node.bl_rna.properties],
          'inputs': [{'name': s.name, 'id': s.identifier, 'type': s.type,
                      'default': str(getattr(s, 'default_value', None))} for s in node.inputs]}
(PROJECT_ROOT/'outputs/vvoori-cafe/v001/scale-api.json').write_text(json.dumps(report, indent=2), encoding='utf-8')
print(json.dumps(report, indent=2))
