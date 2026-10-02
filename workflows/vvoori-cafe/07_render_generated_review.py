"""브리찌에서 AI 이미지가 적용된 v002 포스터와 20초 검토 프레임 출력."""
import bpy
import runpy
scene = bpy.context.scene
assert scene.name == 'Vvoori_Cafe_v002'
scene.render.filepath = str(PROJECT_ROOT/'outputs/vvoori-cafe/v002/poster-fullhd.png')
bpy.ops.render.render(write_still=True)
runpy.run_path(str(PROJECT_ROOT/'workflows/vvoori-cafe/02_render_review.py'),
              init_globals={'VERSION': 'v002', 'PROJECT_ROOT': PROJECT_ROOT})
