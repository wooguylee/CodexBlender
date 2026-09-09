"""Rebuild only the named demo collection. Run through bridge/client.py run."""
import math
import bpy
from mathutils import Vector

COLLECTION = 'CodexDemo'
old = bpy.data.collections.get(COLLECTION)
if old:
    for obj in list(old.objects):
        bpy.data.objects.remove(obj, do_unlink=True)
    bpy.data.collections.remove(old)
collection = bpy.data.collections.new(COLLECTION)
bpy.context.scene.collection.children.link(collection)


def own(obj, name):
    obj.name = name
    for parent in list(obj.users_collection):
        parent.objects.unlink(obj)
    collection.objects.link(obj)
    return obj


def material(name, color, metallic=0, roughness=.35):
    mat = bpy.data.materials.get(name) or bpy.data.materials.new(name)
    mat.diffuse_color = (*color, 1)
    mat.use_nodes = True
    shader = mat.node_tree.nodes.get('Principled BSDF')
    shader.inputs['Base Color'].default_value = (*color, 1)
    shader.inputs['Metallic'].default_value = metallic
    shader.inputs['Roughness'].default_value = roughness
    return mat


def aim(obj, target):
    obj.rotation_euler = (Vector(target) - obj.location).to_track_quat('-Z', 'Y').to_euler()


blue = material('DemoColor', (.025, .28, .52), .58, .24)
dark = material('DemoStage', (.028, .036, .055), .15, .34)
gold = material('DemoAccent', (.94, .51, .16), .7, .25)
white = material('DemoText', (.7, .8, .93), .1, .45)

bpy.ops.mesh.primitive_cube_add(size=2, location=(0, 0, 1.65))
hero = own(bpy.context.object, 'Demo_Hero')
hero.scale = (.8, .8, .8)
hero.rotation_euler[2] = math.radians(18)
hero.data.materials.append(blue)
bevel = hero.modifiers.new('Soft edges', 'BEVEL')
bevel.width = .18
bevel.segments = 6
hero.modifiers.new('Weighted normals', 'WEIGHTED_NORMAL')

bpy.ops.mesh.primitive_cylinder_add(vertices=96, radius=1.65, depth=.28, location=(0, 0, .22))
pedestal = own(bpy.context.object, 'Demo_Pedestal')
pedestal.data.materials.append(dark)
bevel = pedestal.modifiers.new('Soft stage edge', 'BEVEL')
bevel.width = .06
bevel.segments = 3

bpy.ops.mesh.primitive_torus_add(major_radius=1.32, minor_radius=.028, major_segments=96,
                                minor_segments=12, location=(0, 0, .39))
own(bpy.context.object, 'Demo_Ring').data.materials.append(gold)

bpy.ops.mesh.primitive_plane_add(size=200, location=(0, 0, .035))
own(bpy.context.object, 'Demo_Floor').data.materials.append(dark)

bpy.ops.object.text_add(location=(0, -.94, .385), rotation=(0, 0, 0))
title = own(bpy.context.object, 'Demo_Label')
title.data.body = 'CODEX / BLENDER'
title.data.align_x = 'CENTER'
title.data.size = .15
title.data.extrude = .001
title.data.materials.append(white)

bpy.ops.object.camera_add(location=(5.7, -8.1, 5.1))
camera = own(bpy.context.object, 'Demo_Camera')
aim(camera, (0, 0, 1.05))
camera.data.type = 'ORTHO'
camera.data.ortho_scale = 5.9
scene = bpy.context.scene
scene.camera = camera

for name, location, energy, color, size in (
    ('Demo_Key', (1, -4, 7), 1100, (1, .85, .68), 5),
    ('Demo_Fill', (-4, -1, 3), 850, (.4, .65, 1), 4),
    ('Demo_Rim', (2, 4, 5), 1400, (.6, .78, 1), 3),
):
    bpy.ops.object.light_add(type='AREA', location=location)
    lamp = own(bpy.context.object, name)
    lamp.data.energy = energy
    lamp.data.color = color
    lamp.data.shape = 'DISK'
    lamp.data.size = size
    aim(lamp, (0, 0, 1))

# Isolate the demo for rendering without deleting other collections/objects.
for child in bpy.context.view_layer.layer_collection.children:
    child.exclude = child.collection != collection
scene.world = scene.world or bpy.data.worlds.new('DemoWorld')
scene.world.use_nodes = True
scene.world.node_tree.nodes['Background'].inputs['Color'].default_value = (.035, .045, .07, 1)
scene.world.node_tree.nodes['Background'].inputs['Strength'].default_value = .35
scene.render.engine = 'CYCLES'
scene.cycles.device = 'CPU'
scene.cycles.samples = 16
scene.cycles.use_denoising = True
scene.render.resolution_x = 960
scene.render.resolution_y = 720
scene.render.resolution_percentage = 100
scene.render.image_settings.file_format = 'PNG'
scene.render.filepath = '//../outputs/render.png'
for screen in bpy.data.screens:
    for area in screen.areas:
        if area.type == 'VIEW_3D':
            area.spaces.active.region_3d.view_perspective = 'CAMERA'
            area.spaces.active.shading.type = 'MATERIAL'
            area.spaces.active.overlay.show_overlays = False
bpy.ops.object.select_all(action='DESELECT')
hero.select_set(True)
bpy.context.view_layer.objects.active = hero
print('Created blue demo object; camera and preview are ready.')
