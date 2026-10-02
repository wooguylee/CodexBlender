"""브리찌에서 20초 영상용 480프레임 생성. 마지막은 검증한 첫 프레임과 동일하게 저장.
479간격/24fps = 19.9583초 동작 주기 + 중복 끝점 1프레임 = 정확히 20초.
"""
import bpy, json, time, shutil
from mathutils import Vector
from bpy_extras.object_utils import world_to_camera_view
scene=bpy.context.scene;assert scene.name=='Autumn_Cafe_v001' and scene.get('background_locked')
out=PROJECT_ROOT/'outputs/autumn-cafe/v001';frames=out/'frames';frames.mkdir(exist_ok=True)
assert not list(frames.glob('*.png')), 'Review existing frames before resume.'
scene.render.resolution_percentage=100;scene.cycles.samples=32
scene.render.image_settings.file_format='PNG';scene.render.image_settings.color_mode='RGB'
scene.cycles.use_adaptive_sampling=False;scene.cycles.use_animated_seed=False
animated=[o for o in scene.objects if o.animation_data and o.animation_data.drivers]
def state(frame):
    scene.frame_set(frame);bpy.context.view_layer.update()
    return {o.name:[float(v) for row in o.matrix_world for v in row] for o in animated}
a,b=state(1),state(480)
err=max(abs(x-y) for k in a for x,y in zip(a[k],b[k]))
assert err<1e-5,err
(out/'motion-verification.json').write_text(json.dumps({'ok':True,'compared_objects':len(a),'frames':[1,480],'max_transform_error':err,'period_frames':479,'output_frames':480,'fps':24,'duration_seconds':20},indent=2),encoding='utf-8')
times=[];start=time.monotonic()
for f in range(1,480):
    scene.frame_set(f);scene.render.filepath=str(frames/f'{f:04d}.png')
    t=time.monotonic();bpy.ops.render.render(write_still=True);times.append(time.monotonic()-t)
    (out/'render-progress.json').write_text(json.dumps({'frame':f,'total':480,'elapsed_seconds':round(time.monotonic()-start,1),'mean_seconds_per_frame':round(sum(times)/len(times),2),'estimated_remaining_seconds':round((480-f)*sum(times)/len(times))}),encoding='utf-8')
    print('AUTUMN RENDER',f,'/480',flush=True)
scene.frame_set(480);scene.render.filepath=str(out/'endpoint-render-check.png');bpy.ops.render.render(write_still=True)
# Identical temporal endpoint verified numerically above. Copy avoids GPU numerical drift.
shutil.copyfile(frames/'0001.png',frames/'0480.png')
scene.frame_set(1);scene.render.filepath='//../outputs/autumn-cafe/v001/frames/'
source=PROJECT_ROOT/'scenes/autumn-cafe-v001.blend';assert not source.exists()
# Only this scene and its dependencies: no unrelated historical scenes in publication.
bpy.data.libraries.write(str(source),{scene},path_remap='RELATIVE_ALL',fake_user=True,compress=True)
(out/'render-result.json').write_text(json.dumps({'ok':True,'frames':480,'fps':24,'duration_seconds':20,'render_seconds':time.monotonic()-start,'source':'scenes/autumn-cafe-v001.blend','endpoint_source_png_identical':True},indent=2),encoding='utf-8')
print('Autumn 20 second render completed')
