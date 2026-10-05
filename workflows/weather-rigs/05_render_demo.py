"""독립 시연 파일을 재개방하고 모든 384프레임을 실제 렌더한다."""
import bpy,json,time
from pathlib import Path
root=Path(__file__).resolve().parents[2];out=root/'outputs/weather-rigs/v001';frames=out/'frames';frames.mkdir(exist_ok=True)
scene=bpy.context.scene;assert scene.name=='Weather_Rig_Demo_v001' and len(bpy.data.scenes)==1
assert not bpy.data.libraries
assert len([o for o in scene.objects if o.type=='ARMATURE' and o.animation_data and o.animation_data.action])==5
assert not any(i.source=='FILE' and not i.packed_file for i in bpy.data.images)
manifest=json.loads((out/'demo-manifest.json').read_text(encoding='utf-8'))
scene.frame_set(1)
# Normalize the library export into a normal standalone Blender project.
scene.render.filepath='//../outputs/weather-rigs/v001/frames/frame_'
bpy.ops.wm.save_as_mainfile(filepath=str(root/manifest['source']),compress=True,check_existing=False)
started=time.monotonic();scene.render.filepath=str(frames/'frame_')
bpy.ops.render.render(animation=True)
paths=sorted(frames.glob('frame_*.png'));assert len(paths)==384
report={'ok':True,'scene':scene.name,'frames':len(paths),'width':scene.render.resolution_x,'height':scene.render.resolution_y,
        'fps':scene.render.fps,'seconds':time.monotonic()-started,'external_dependencies':[]}
(out/'render-result.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
print(json.dumps(report))
