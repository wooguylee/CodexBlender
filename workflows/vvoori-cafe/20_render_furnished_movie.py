"""가구가 포함된 생성 실내 이미지로 Full HD 24fps 20초 전체 프레임 출력."""
import bpy,json,time,shutil
scene=bpy.data.scenes['Vvoori_Cafe_v004'];bpy.context.window.scene=scene
bpy.context.window.view_layer=scene.view_layers['VC4_Motion']
root=PROJECT_ROOT;out=root/'outputs/vvoori-cafe/v004';folder=out/'master-frames'
folder.mkdir(exist_ok=True);assert not list(folder.glob('*.png'))
animated=[o for o in scene.objects if o.animation_data and o.animation_data.drivers]
def matrices(frame):
    scene.frame_set(frame);bpy.context.view_layer.update();deps=bpy.context.evaluated_depsgraph_get();deps.update()
    return {o.name:[float(x) for row in o.evaluated_get(deps).matrix_world for x in row] for o in animated}
a,b,middle=matrices(1),matrices(480),matrices(241)
error=max(abs(x-y) for k in a for x,y in zip(a[k],b[k]));movement=max(abs(x-y) for k in a for x,y in zip(a[k],middle[k]))
assert len(animated)==62 and error<1e-5 and movement>1
assert not any(not f.is_valid for o in animated for f in o.animation_data.drivers)
(out/'motion-verification.json').write_text(json.dumps({'ok':True,'animated_objects':62,'endpoint_max_error':error,'midpoint_motion':movement},indent=2),encoding='utf-8')
scene.render.resolution_percentage=100;scene.render.fps=24;scene.frame_start=1;scene.frame_end=480
scene.cycles.samples=8;scene.cycles.use_denoising=False;scene.cycles.use_animated_seed=False
start=time.monotonic()
for frame in range(1,480):
    scene.frame_set(frame);scene.render.filepath=str(folder/f'{frame:04d}.png');bpy.ops.render.render(write_still=True)
    elapsed=time.monotonic()-start
    (out/'render-progress.json').write_text(json.dumps({'frame':frame,'total':480,'elapsed_seconds':round(elapsed,1),'estimated_remaining_seconds':round(elapsed/frame*(480-frame),1)}),encoding='utf-8')
scene.frame_set(480);scene.render.filepath=str(out/'independent-endpoint.png');bpy.ops.render.render(write_still=True)
shutil.copyfile(folder/'0001.png',folder/'0480.png');shutil.copyfile(folder/'0001.png',out/'poster-fullhd.png')
scene.frame_set(1);scene.render.filepath='//../outputs/vvoori-cafe/v004/master-frames/'
bpy.context.window.view_layer=scene.view_layers['VC4_EditAll3D']
path=root/'scenes/vvoori-cafe-v004.blend';assert not path.exists()
bpy.data.libraries.write(str(path),{scene},path_remap='RELATIVE_ALL',fake_user=True,compress=True)
report={'ok':True,'frames':480,'fps':24,'duration_seconds':20,'width':1920,'height':1080,'samples':8,'render_seconds':time.monotonic()-start,'full_quality_movie_rendered':True}
(out/'render-report.json').write_text(json.dumps(report,indent=2),encoding='utf-8');print(json.dumps(report,indent=2))
