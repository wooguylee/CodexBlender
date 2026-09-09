"""2단계: 원본의 파랑/노랑/회색을 유지하는 새틴 금속과 짙은 남색 배경."""
import json
from mathutils import Vector

scene = bpy.context.scene
assert scene.name == 'Thegachi_Opening_v001'


def srgb(code):
    vals = [int(code[i:i+2],16)/255 for i in (0,2,4)]
    return tuple(v/12.92 if v<=.04045 else ((v+.055)/1.055)**2.4 for v in vals)


for name, metal, rough, coat in [
    ('TG_Blue_Gradient', .3, .27, .25),
    ('TG_Yellow_Person', .35, .28, .25),
    ('TG_Silver_Letters', .65, .3, .18),
]:
    p = bpy.data.materials[name].node_tree.nodes['Principled BSDF']
    p.inputs['Metallic'].default_value = metal
    p.inputs['Roughness'].default_value = rough
    p.inputs['Coat Weight'].default_value = coat
    p.inputs['Coat Roughness'].default_value = .24

# Curves do not reliably supply mesh Generated coordinates. Use local Object X.
mat = bpy.data.materials['TG_Blue_Gradient']
nodes, links = mat.node_tree.nodes, mat.node_tree.links
tex = next(n for n in nodes if n.type == 'TEX_COORD')
sep = next(n for n in nodes if n.type == 'SEPXYZ')
ramp = next(n for n in nodes if n.type == 'VALTORGB')
mapping = nodes.new('ShaderNodeMapRange')
mapping.inputs['From Min'].default_value = -1.11
mapping.inputs['From Max'].default_value = 1.11
links.new(tex.outputs['Object'], sep.inputs[0])
links.new(sep.outputs['X'], mapping.inputs['Value'])
links.new(mapping.outputs[0], ramp.inputs[0])

back = bpy.data.materials['TG_Backdrop']
nodes, links = back.node_tree.nodes, back.node_tree.links
p = nodes.get('Principled BSDF')
p.inputs['Roughness'].default_value = .72
geometry = nodes.new('ShaderNodeNewGeometry')
length = nodes.new('ShaderNodeVectorMath')
length.operation = 'LENGTH'
divide = nodes.new('ShaderNodeMath')
divide.operation = 'DIVIDE'
divide.inputs[1].default_value = 8
halo = nodes.new('ShaderNodeValToRGB')
halo.color_ramp.elements[0].color = (*srgb('243952'),1)
halo.color_ramp.elements[1].position = .85
halo.color_ramp.elements[1].color = (*srgb('070d19'),1)
links.new(geometry.outputs['Position'], length.inputs[0])
links.new(length.outputs['Value'], divide.inputs[0])
links.new(divide.outputs[0], halo.inputs[0])
links.new(halo.outputs[0], p.inputs['Base Color'])
links.new(halo.outputs[0], p.inputs['Emission Color'])
p.inputs['Emission Strength'].default_value = .25
scene.objects['TG_Backdrop'].location.z = -.65

for name, loc, energy, size, color in [
    ('TG_Key', (-3,4,7), 1150, 5, (.91,.96,1)),
    ('TG_Fill', (5,-1,6), 900, 4, (.68,.8,1)),
    ('TG_Top', (0,5,3), 750, 3, (1,.93,.8)),
]:
    obj = scene.objects[name]
    obj.location = loc
    obj.data.energy, obj.data.size, obj.data.color = energy, size, color
    obj.rotation_euler = (Vector((0,0,0))-obj.location).to_track_quat('-Z','Y').to_euler()
world = scene.world.node_tree.nodes['Background']
world.inputs[0].default_value = (.32,.4,.55,1)
world.inputs[1].default_value = .22

# A dedicated strip light will move across the assembled logo during animation.
collection = bpy.data.collections['Thegachi_Opening_v001']
light = bpy.data.lights.new('TG_Sweep', 'AREA')
light.energy = 250
light.shape = 'RECTANGLE'
light.size, light.size_y = 1.2, 5
obj = bpy.data.objects.new('TG_Sweep', light)
collection.objects.link(obj)
obj.location = (-4,0,4)
obj.rotation_euler = (0,0,0)

engines = [e.identifier for e in scene.render.bl_rna.properties['engine'].enum_items]
print('Available render engines:', engines)
engine = next((e for e in ['BLENDER_EEVEE_NEXT','BLENDER_EEVEE'] if e in engines), 'CYCLES')
scene.render.engine = engine
scene.render.resolution_x, scene.render.resolution_y = 1280,720
scene.view_settings.view_transform = 'AgX'
scene.view_settings.exposure = -.15
scene.render.image_settings.color_mode = 'RGBA'
scene.frame_set(120)
report = {'engine': engine, 'available_engines': engines, 'source_paths_preserved': 6,
          'original_scene_preserved': 'Scene' in bpy.data.scenes,
          'objects': [obj.name for obj in scene.objects]}
(OUTPUT_DIR / 'lookdev.json').write_text(json.dumps(report, indent=2), encoding='utf-8')
print(json.dumps(report))
