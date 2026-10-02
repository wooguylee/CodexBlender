"""진단 결과: Scale의 Clip이 캔버스 가장자리에 반투명 한 줄을 만듦. Extend로 경계 보간."""
import bpy,json
scene=bpy.data.scenes['Vvoori_Cafe_Winter_v001'];bpy.context.window.scene=scene
out=PROJECT_ROOT/'outputs/vvoori-cafe-winter/v001'
for key in ['Park_Fit','Cafe_Fit']:
    n=scene.compositing_node_group.nodes[key]
    n.inputs['Extension X'].default_value='Extend'
    n.inputs['Extension Y'].default_value='Extend'
for frame in [1,61,361,481]:
    scene.frame_set(frame);scene.render.filepath=str(out/f'edge-fixed-{frame:04d}.png');bpy.ops.render.render(write_still=True)
scene.frame_set(1);scene.render.filepath='//../outputs/vvoori-cafe-winter/v001/master-frames/'
print('Scale border sampling: Clip -> Extend; four probe renders complete')
