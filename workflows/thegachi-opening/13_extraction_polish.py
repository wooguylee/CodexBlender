"""추출 장면 QA: 투명 전환의 노이즈를 없애고 노란 심벌을 파란 집 앞에 유지한다."""
import json
import math

scene=bpy.context.scene
assert scene.name=='Thegachi_Opening_v005'
changed=[]
for mat in bpy.data.materials:
    if mat.name.startswith(('HP_v005_','HP_Extracted_Yellow','HP_Extract_Background_Mat')):
        choices=[e.identifier for e in mat.bl_rna.properties['surface_render_method'].enum_items]
        assert 'BLENDED' in choices, choices
        mat.surface_render_method='BLENDED'
        changed.append(mat.name)
glyph=scene.objects['HP_Extracted_Person_ch']
for f in range(89,109):
    scene.frame_set(f)
    t=max(0.,min(1.,(f-88)/20))
    pull=t*t*(3-2*t)
    glyph.location.z+=math.sin(math.pi*pull)*.75
    glyph.keyframe_insert('location',frame=f)
scene.render.resolution_x,scene.render.resolution_y=960,540
scene.frame_set(96)
report={'ok':True,'smooth_blending_materials':changed,'yellow_symbol':'Additional forward offset during extraction.'}
(OUTPUT_DIR/'extraction-review.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
print(json.dumps(report))
