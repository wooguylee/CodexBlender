"""Second visible step: change the demo to orange and make it taller."""
import bpy

hero = bpy.data.objects.get('Demo_Hero')
if hero is None:
    raise RuntimeError('Run workflows/demo_scene.py first.')
hero.scale.z = 1.12
hero.location.z = 1.8
mat = bpy.data.materials['DemoColor']
mat.diffuse_color = (.8, .19, .035, 1)
mat.node_tree.nodes['Principled BSDF'].inputs['Base Color'].default_value = (.8, .19, .035, 1)
print('Changed the hero to orange and increased height.')
