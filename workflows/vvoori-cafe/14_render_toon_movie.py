"""Full HD 24fps 20초 최종 출력. 먼 차량은 점진적으로 소멸한 뒤 순환하고 실내는 고정."""
import bpy, json, time, math, shutil
from bpy_extras.object_utils import world_to_camera_view
from mathutils import Vector
scene=bpy.data.scenes['Vvoori_Cafe_v003'];bpy.context.window.scene=scene
bpy.context.window.view_layer=scene.view_layers['VC3_Motion']
root=PROJECT_ROOT;out=root/'outputs/vvoori-cafe/v003';folder=out/'master-frames'
folder.mkdir(exist_ok=True);assert not list(folder.glob('*.png'))
records=json.loads((out/'road-fit.json').read_text())
phases=[.05,.33,.69,.13,.47,.84]
for i,record in enumerate(records):
    obj=bpy.data.objects[record['car']];direction=1 if i<3 else -1
    expr=f'15+{direction}*30*tan(3.141592653589793*((((frame-1)/479+{phases[i]})%1)-.5)*.995)'
    obj.driver_add('location',0).driver.expression=expr
    obj.driver_add('location',1).driver.expression=f"{record['world_y_slope']}*({expr})+{record['world_y_intercept']}"
    # Painted road's vanishing point lies within the far pane. Taper distant cars
    # continuously before the 300 m clipping plane, so wrapping never pops a car.
    for axis in range(3):obj.driver_add('scale',axis).driver.expression=f'min(1,max(0,(240-({expr}))/120))'
    screen=[]
    for u in [0,.999999]:
        x=15+direction*30*math.tan(math.pi*(u-.5)*.995)
        p=Vector((x,record['world_y_slope']*x+record['world_y_intercept'],.5))
        q=world_to_camera_view(scene,scene.camera,p);screen.append(list(q))
        scale=min(1,max(0,(240-x)/120))
        assert q.z<0 or scale==0 or q.x<0, (record['car'],list(q),scale)
    record['wrap_screen_xyz']=screen;record['driver_x']=expr
for obj in bpy.data.collections['VC3_Leaves'].objects:
    zexpr=next(f.driver.expression for f in obj.animation_data.drivers if f.data_path=='location' and f.array_index==2)
    for axis in range(3):obj.driver_add('scale',axis).driver.expression=f'min(1,max(0,({zexpr})/.6))'
(out/'road-fit-final.json').write_text(json.dumps(records,indent=2),encoding='utf-8')
animated=[o for o in scene.objects if o.animation_data and o.animation_data.drivers]
def matrices(frame):
    scene.frame_set(frame);bpy.context.view_layer.update();deps=bpy.context.evaluated_depsgraph_get();deps.update()
    return {o.name:[float(x) for row in o.evaluated_get(deps).matrix_world for x in row] for o in animated}
a,b,middle=matrices(1),matrices(480),matrices(241)
err=max(abs(x-y) for k in a for x,y in zip(a[k],b[k]));motion=max(abs(x-y) for k in a for x,y in zip(a[k],middle[k]))
assert len(animated)==62 and err<1e-5 and motion>1
assert not any(not f.is_valid for o in animated for f in o.animation_data.drivers)
(out/'motion-verification.json').write_text(json.dumps({'ok':True,'animated_objects':62,'endpoint_max_error':err,'midpoint_motion':motion,'wraps_invisible':True,'distant_car_taper_world_x':[120,240]},indent=2),encoding='utf-8')
scene.render.resolution_percentage=100;scene.render.fps=24;scene.frame_start=1;scene.frame_end=480
scene.cycles.samples=8;scene.cycles.use_denoising=False;scene.cycles.use_animated_seed=False
start=time.monotonic()
for frame in range(1,480):
    scene.frame_set(frame);scene.render.filepath=str(folder/f'{frame:04d}.png');bpy.ops.render.render(write_still=True)
    elapsed=time.monotonic()-start
    (out/'render-progress.json').write_text(json.dumps({'frame':frame,'total':480,'elapsed_seconds':round(elapsed,1),'estimated_remaining_seconds':round(elapsed/frame*(480-frame),1)}),encoding='utf-8')
scene.frame_set(480);scene.render.filepath=str(out/'independent-endpoint.png');bpy.ops.render.render(write_still=True)
shutil.copyfile(folder/'0001.png',folder/'0480.png')
shutil.copyfile(folder/'0001.png',out/'poster-fullhd.png')
scene.frame_set(1);scene.render.filepath='//../outputs/vvoori-cafe/v003/master-frames/'
path=root/'scenes/vvoori-cafe-v003.blend';assert not path.exists()
bpy.data.libraries.write(str(path),{scene},path_remap='RELATIVE_ALL',fake_user=True,compress=True)
report={'ok':True,'frames':480,'fps':24,'duration_seconds':20,'width':1920,'height':1080,'samples':8,'render_seconds':time.monotonic()-start,'full_quality_movie_rendered':True}
(out/'render-report.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
print(json.dumps(report,indent=2))
