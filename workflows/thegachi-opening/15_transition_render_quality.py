"""투명 전환의 그림자 노이즈를 낮추고 렌더 샘플 설정을 확인한다."""
import json

scene=bpy.context.scene
assert scene.name=='Thegachi_Opening_v005'
props={p.identifier for p in scene.eevee.bl_rna.properties} if hasattr(scene,'eevee') else set()
report={'eevee_sample_properties':sorted(p for p in props if 'sample' in p),'material_changes':[]}
for mat in bpy.data.materials:
    if mat.name.startswith(('HP_v005_','HP_Extracted_Yellow','HP_Extract_Background_Mat')):
        changes={}
        if hasattr(mat,'use_transparent_shadow'):
            mat.use_transparent_shadow=False
            changes['use_transparent_shadow']=False
        if hasattr(mat,'use_transparency_overlap'):
            mat.use_transparency_overlap=False
            changes['use_transparency_overlap']=False
        report['material_changes'].append({'material':mat.name,**changes})
if 'taa_render_samples' in props:
    scene.eevee.taa_render_samples=256
    report['taa_render_samples']=256
scene['transition_samples']=256
scene.frame_set(96)
scene.render.resolution_x,scene.render.resolution_y=960,540
(OUTPUT_DIR/'quality-settings.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
print(json.dumps(report))
