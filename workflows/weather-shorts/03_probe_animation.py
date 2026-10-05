"""연속 실제 렌더에서 프레임당 비용과 고정 배경 안정성을 확인한다."""
import json, time, math
scene=bpy.data.scenes['Weather_Short_00_v001']
bpy.context.window.scene=scene
obj=bpy.data.objects['WS0_Haerong_Root']
for frame in range(1,25):
    obj.location.z=.12*math.sin((frame-1)/24*math.tau)
    obj.keyframe_insert('location',frame=frame)
scene.frame_start=1;scene.frame_end=24
scene.render.filepath=str(PROJECT_ROOT/'outputs/weather-shorts/v001/probe/motion/frame-')
scene.render.image_settings.compression=15
start=time.monotonic();bpy.ops.render.render(animation=True)
report={'ok':True,'seconds_24_frames':time.monotonic()-start,'engine':scene.render.engine}
(PROJECT_ROOT/'outputs/weather-shorts/v001/probe/animation-probe.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
scene.frame_set(1)
print(json.dumps(report))
