"""최초 실행의 노드 API 오류 이후, 이미 생성된 v002의 합성 설정만 이어서 마친 이력.

정상 재현에서는 수정된 06번만 실행한다. 이 파일은 재생성/덮어쓰기를 하지 않는다.
"""
import bpy
import json
import hashlib

scene = bpy.data.scenes['Vvoori_Cafe_v002']
source = bpy.data.scenes['Vvoori_Cafe_v001']
ng = scene.compositing_node_group
assert ng.nodes.get('VC2_NormalizeGeneratedAlpha') is None
out = PROJECT_ROOT/'outputs/vvoori-cafe/v002'
images = {name: ng.nodes[name].image for name in ['01_ParkBackground', '04_CafeForeground']}
old_paths = ['scenes/vvoori-cafe-v001.blend', 'scenes/autumn-cafe-v001.blend',
             'outputs/vvoori-cafe/v001/vvoori-cafe-review-20s.mp4']
hashes = {p: hashlib.sha256((PROJECT_ROOT/p).read_bytes()).hexdigest() for p in old_paths}
prior = {s.name: sorted(o.name for o in s.objects) for s in bpy.data.scenes if s != scene}
code = (PROJECT_ROOT/'workflows/vvoori-cafe/06_apply_generated_images.py').read_text(encoding='utf-8')
tail = code[code.index('# The generated RGBA'):]
exec(compile(tail, '06_apply_generated_images.py:finish', 'exec'), globals())
