"""영상 QA 수정: 등장 중 회전한 집이 배경면 뒤로 들어가는 문제의 원인 계측/수정.

v001 영상/원본은 유지. 배경의 화면 색은 유지하면서 기하학적 면을 뒤로 이동한다.
"""
import json
from mathutils import Vector

scene = bpy.context.scene
assert scene.name == 'Thegachi_Opening_v001'
parts = [scene.objects['TG_'+n] for n in ['house_d','person_ch','eo','g','a','i']]
backdrop = scene.objects['TG_Backdrop']
original_z = backdrop.location.z


def min_depth(frame):
    scene.frame_set(frame)
    bpy.context.view_layer.update()
    return min((o.matrix_world @ Vector(corner)).z for o in parts for corner in o.bound_box)


before = [{'frame':f,'minimum_z':min_depth(f),'background_z':original_z} for f in [10,14,20,34,120]]
assert any(row['minimum_z'] < original_z for row in before), 'Hypothesis not confirmed; do not apply speculative fix.'
scene.name = 'Thegachi_Opening_v002'
scene['output_version'] = 'v002'
backdrop.location.z = -4.
# Preserve the old world-position input to the radial background material exactly.
mat = backdrop.data.materials[0]
nodes,links = mat.node_tree.nodes,mat.node_tree.links
geometry = next(n for n in nodes if n.type == 'NEW_GEOMETRY')
length = next(n for n in nodes if n.type == 'VECT_MATH' and n.operation=='LENGTH')
offset = nodes.new('ShaderNodeVectorMath')
offset.operation = 'ADD'
offset.inputs[1].default_value = (0,0,original_z-backdrop.location.z)
links.new(geometry.outputs['Position'], offset.inputs[0])
links.new(offset.outputs[0], length.inputs[0])
minimum = min(min_depth(f) for f in range(1,145))
assert minimum > backdrop.location.z+.5, 'Insufficient background clearance.'
out = PROJECT_ROOT/'outputs/thegachi-opening/v002'
out.mkdir(parents=True,exist_ok=True)
report = {'ok':True,'cause':'Rotated logo extends behind the old background plane.',
          'before':before,'after_background_z':backdrop.location.z,
          'all_144_frames_minimum_logo_z':minimum,
          'minimum_clearance':minimum-backdrop.location.z,
          'original_v001_preserved':True}
(out/'clearance-verification.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
print(json.dumps(report))
# Re-render the same review frames to compare the correction with the retained v001 frames.
review = PROJECT_ROOT/'workflows/thegachi-opening/04_review_keyframes.py'
exec(compile(review.read_text(encoding='utf-8'),str(review),'exec'),globals())
