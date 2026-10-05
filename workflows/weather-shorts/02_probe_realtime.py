"""브리찌: 실시간 렌더러의 실제 속도와 반복 렌더 안정성 비교."""
import json
import time
scene=bpy.data.scenes['Weather_Short_00_v001']
bpy.context.window.scene=scene
out=PROJECT_ROOT/'outputs/weather-shorts/v001/probe'
engines=[i.identifier for i in scene.render.bl_rna.properties['engine'].enum_items]
engine=next((e for e in engines if 'EEVEE' in e),None)
if engine is None:
    # Dynamic render-engine enums may omit registered engines; known 5.x identifier.
    engine='BLENDER_EEVEE'
scene.render.engine=engine
properties={p.identifier for p in scene.eevee.bl_rna.properties}
if 'taa_render_samples' in properties:scene.eevee.taa_render_samples=16
if 'use_raytracing' in properties:scene.eevee.use_raytracing=False
scene.render.resolution_x=1280;scene.render.resolution_y=720
times=[]
for i in range(3):
    scene.render.filepath=str(out/f'eevee-{i}.png')
    start=time.monotonic();bpy.ops.render.render(write_still=True);times.append(time.monotonic()-start)
(out/'eevee-probe.json').write_text(json.dumps({'ok':True,'engine':engine,'times_seconds':times,'properties':sorted(properties)},indent=2),encoding='utf-8')
print(json.dumps({'engine':engine,'times_seconds':times}))
