"""실행 세션 GPU 선택, 고정 이미지의 렌더 크기 대응 및 알파 레이어 확인."""
import bpy
import json

scene = bpy.context.scene
assert scene.name == 'Vvoori_Cafe_v001'
prefs = bpy.context.preferences.addons['cycles'].preferences
prefs.compute_device_type = 'OPTIX'
prefs.get_devices()
assert any(d.type == 'OPTIX' for d in prefs.devices)
for device in prefs.devices:
    device.use = device.type == 'OPTIX'
scene.cycles.device = 'GPU'
ng = scene.compositing_node_group
for name in ['01_ParkBackground', '04_CafeForeground']:
    node = ng.nodes[name]
    links = list(node.outputs['Image'].links)
    assert len(links) == 1
    assert links[0].to_node.type == 'ALPHAOVER', 'Scale already connected; do not run twice.'
    scale = ng.nodes.get(name + '_FitRenderSize') or ng.nodes.new('CompositorNodeScale')
    scale.name = name + '_FitRenderSize'
    scale.inputs['Type'].default_value = 'Render Size'
    scale.location = (node.location.x+180, node.location.y)
    destination = links[0].to_socket
    ng.links.remove(links[0])
    ng.links.new(node.outputs['Image'], scale.inputs['Image'])
    ng.links.new(scale.outputs['Image'], destination)
scene.frame_set(1)
scene.render.filepath = str(PROJECT_ROOT/'outputs/vvoori-cafe/v001/poster-fullhd.png')
bpy.ops.render.render(write_still=True)
scene.render.filepath = '//../outputs/vvoori-cafe/v001/master-frames/'
print(json.dumps({'ok': True, 'device': 'OPTIX', 'scaled_image_nodes': 2}))
