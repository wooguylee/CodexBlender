"""첫 미리보기에서 확인한 과한 통창 반사와 노출을 보정한다."""
import bpy
scene=bpy.context.scene;assert scene.name=='Autumn_Cafe_v001'
for o in bpy.data.collections['AC_LightingCamera'].objects:
    if o.type=='LIGHT':
        o.visible_glossy=False
        if 'bounce' in o.name or 'fill' in o.name:o.data.energy*=.45
scene.world.node_tree.nodes['Background'].inputs['Strength'].default_value=.22
scene.view_settings.exposure=-.55
scene.cycles.samples=56
# Very clean low-reflection glass preserves a clear view of the autumn park.
glass=bpy.data.materials['AC_Clear window'];nt=glass.node_tree;nt.nodes.clear()
tr=nt.nodes.new('ShaderNodeBsdfTransparent');tr.inputs['Color'].default_value=(.99,1,1,1)
op=nt.nodes.new('ShaderNodeOutputMaterial');nt.links.new(tr.outputs[0],op.inputs[0])
print('Window glare removed and afternoon exposure refined')
