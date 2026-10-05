"""사용자 추가 요청: 눈송이와 바람 캐릭터도 필요하다.

v001을 독립 복제한 v002에 송송(눈송이), 솔솔(산들바람)을 추가한다.
기존 Scene/원본/PNG는 보존한다. 브리찌 run 전용.
"""
import ast
import hashlib
import json
import math
from mathutils import Vector

NAME = 'Weather_Fairies_v002'
PREFIX = 'WF2_'
assert NAME not in bpy.data.scenes
assert bpy.context.scene.name == 'Weather_Fairies_v001'
out = PROJECT_ROOT / 'outputs/weather-fairies/v002'
out.mkdir(parents=True, exist_ok=True)


def signature(s):
    return {'camera': s.camera.name if s.camera else None,
            'objects': {o.name: {'data': o.data.name if o.data else None,
                                'matrix': [float(v) for row in o.matrix_world for v in row],
                                'hide_render': o.hide_render}
                        for o in s.objects}}


before = {s.name: signature(s) for s in bpy.data.scenes}
preserved = {}
paths = list((PROJECT_ROOT / 'scenes').glob('*.blend'))
paths += list((PROJECT_ROOT / 'outputs/weather-fairies/v001').glob('*.png'))
for p in paths:
    if p.name != 'current.blend':
        preserved[p.relative_to(PROJECT_ROOT).as_posix()] = hashlib.sha256(p.read_bytes()).hexdigest()

# Copy data as well as objects: changes to the new camera/materials cannot alter v001.
source = bpy.context.scene
scene = bpy.data.scenes.new(NAME)
bpy.context.window.scene = scene
collections = {}
object_map, material_map = {}, {}
for old_collection in source.collection.children:
    if old_collection.name == 'WF1_Typography':
        continue
    key = old_collection.name.removeprefix('WF1_')
    new_collection = bpy.data.collections.new(PREFIX + key)
    scene.collection.children.link(new_collection)
    collections[key] = new_collection
    for old in old_collection.objects:
        obj = old.copy()
        obj.name = old.name.replace('WF1_', PREFIX, 1)
        if old.data:
            obj.data = old.data.copy()
            obj.data.name = PREFIX + old.data.name
            if hasattr(obj.data, 'materials'):
                obj.data.materials.clear()
                for old_mat in old.data.materials:
                    if old_mat not in material_map:
                        new_mat = old_mat.copy()
                        new_mat.name = old_mat.name.replace('WF1_', PREFIX, 1)
                        material_map[old_mat] = new_mat
                    obj.data.materials.append(material_map[old_mat])
        new_collection.objects.link(obj)
        object_map[old] = obj
for old, obj in object_map.items():
    obj.parent = object_map.get(old.parent)
scene.camera = object_map[source.camera]
scene.world = source.world.copy()
scene.world.name = PREFIX + 'StudioWorld'

# Reuse only the pure modelling helpers from v001; never execute its creation body.
helper_names = {'rgb', 'material', 'own', 'ball', 'curve', 'capsule', 'star'}
tree = ast.parse((PROJECT_ROOT / 'workflows/weather-fairies/01_build_characters.py').read_text(encoding='utf-8'))
helpers = ast.Module(body=[n for n in tree.body if isinstance(n, ast.FunctionDef) and n.name in helper_names], type_ignores=[])
exec(compile(ast.fix_missing_locations(helpers), '<weather-modelling-helpers>', 'exec'))

for key in ('Songsong', 'Solsol'):
    c = bpy.data.collections.new(PREFIX + key)
    scene.collection.children.link(c)
    collections[key] = c
current = collections['Studio']
white = bpy.data.materials['WF2_Warm_white']
ink = bpy.data.materials['WF2_Expression_cocoa']
blush = bpy.data.materials['WF2_Cheek_apricot']
lavender = material('Snow_lilac', 'B4A4DC', .44, .17, .03)
ice = material('Snow_pearl', 'DCEAF9', .34, .24, .05)
frost = material('Snow_branches', 'AFCFEA', .35, .24, .025)
ice_white = material('Snow_frost_tips', 'F0F8FF', .38, .15, .025)
mint = material('Wind_mint', '95DCC7', .36, .22, .045)
mint_dark = material('Wind_seafoam', '58BBA5', .43, .13, .02)
scarf_mat = material('Wind_coral_scarf', 'EDAB95', .57, .04, .025)
scarf_edge = material('Wind_scarf_stitch', 'F9DBB9', .6, .04)
gold = bpy.data.materials['WF2_Star_cushion']


def root_character(key, origin, angle=0):
    root = bpy.data.objects.new(PREFIX + key + '_Root', None)
    collections[key].objects.link(root)
    root.location = origin
    root.rotation_euler.z = angle
    root.empty_display_type = 'PLAIN_AXES'
    for o in list(collections[key].objects):
        if o != root:
            o.parent = root
    return root


def smile(name, center, width=.14, height=.105):
    cx, y, cz = center
    pts = [(-width, 0), (0, -.014), (width, 0)]
    pts += [(width * math.cos(math.pi * i / 24), -height * math.sin(math.pi * i / 24))
            for i in range(1, 25)]
    mesh = bpy.data.meshes.new(PREFIX + name)
    mesh.from_pydata([(cx + x, y, cz + z) for x, z in pts], [], [tuple(range(len(pts)))])
    mesh.update()
    obj = bpy.data.objects.new(PREFIX + name, mesh)
    current.objects.link(obj)
    mesh.materials.append(ink)
    mod = obj.modifiers.new('Inlaid_smile', 'SOLIDIFY')
    mod.thickness = .012
    return obj


# 송송: sixfold snow crystal, forked arms, a wink and soft lavender mittens.
current = collections['Songsong']
cz = 2.13
for i in range(6):
    theta = i * math.tau / 6
    direction = Vector((math.sin(theta), 0, math.cos(theta)))
    side = Vector((math.cos(theta), 0, -math.sin(theta)))
    center = Vector((0, .055, cz))
    capsule('Songsong_CrystalSpoke_%02d' % i, center + direction * .57,
            center + direction * 1.27, .092, frost)
    ball('Songsong_CrystalTip_%02d' % i, center + direction * 1.31, (.105, .095, .105), ice_white)
    for side_sign in (-1, 1):
        branch_a = center + direction * .94
        branch_b = center + direction * 1.15 + side * (.23 * side_sign)
        capsule('Songsong_CrystalFork_%02d_%s' % (i, side_sign), branch_a, branch_b, .066, ice_white)
bpy.ops.mesh.primitive_cylinder_add(vertices=6, radius=.77, depth=.60,
                                   rotation=(math.pi / 2, 0, 0), location=(0, -.02, cz))
head = own(bpy.context.object, 'Songsong_SoftHexagon', ice)
bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
bevel = head.modifiers.new('Round_ice_corners', 'BEVEL')
bevel.width = .145
bevel.segments = 6
head.modifiers.new('Soft_ice_normals', 'WEIGHTED_NORMAL')
curve('Songsong_WinkingEye', [(-.365, -.342, 2.24), (-.245, -.352, 2.185),
                            (-.125, -.342, 2.24)], .026, ink)
ball('Songsong_OpenEye', (.245, -.344, 2.22), (.064, .035, .098), ink)
ball('Songsong_EyeGlint', (.231, -.378, 2.254), (.018, .014, .023), white, 24, 16)
for x in (-.40, .40):
    ball('Songsong_Blush', (x, -.324, 2.04), (.13, .025, .064), blush)
smile('Songsong_PlayfulSmile', (0, -.345, 2.056), .126, .111)
ball('Songsong_Tongue', (.025, -.360, 1.974), (.066, .014, .025), blush)
for x in (-.26, .26):
    capsule('Songsong_Leg', (x, 0, 1.41), (x * 1.18, -.04, .69), .104, ice)
    ball('Songsong_LilacBoot', (x * 1.18, -.17, .48), (.235, .31, .19), lavender)
    ball('Songsong_BootFur', (x * 1.18, -.015, .66), (.17, .17, .065), ice_white)
curve('Songsong_LeftArm', [(-.55, -.02, 1.72), (-.87, -.11, 1.54), (-1.03, -.18, 1.76)], .105, ice)
ball('Songsong_LeftMitten', (-1.04, -.18, 1.88), (.17, .145, .20), lavender)
ball('Songsong_LeftThumb', (-.91, -.23, 1.84), (.09, .10, .12), lavender)
curve('Songsong_RightArm', [(.56, -.015, 1.70), (.86, -.16, 1.40), (1.00, -.22, 1.50)], .105, ice)
ball('Songsong_RightMitten', (1.08, -.23, 1.53), (.19, .145, .17), lavender)
ball('Songsong_RightThumb', (1.01, -.25, 1.66), (.09, .105, .11), lavender)
root_character('Songsong', (3.25, .10, 0), .06)['character_ko'] = '송송 — 장난꾸러기 눈송이'


# A tapered tube gives the wind a real spiral silhouette, rather than a flat decal.
def tapered_curve(name, points, radii, mat):
    obj = curve(name, points, 1, mat)
    for point, radius in zip(obj.data.splines[0].bezier_points, radii):
        point.radius = radius
    obj.data.resolution_u = 24
    obj.data.bevel_resolution = 6
    return obj


current = collections['Solsol']
body = ball('Solsol_BreezeBody', (0, .035, 1.88), (.69, .47, .83), mint, 64, 40)
body.rotation_euler.y = -.12
ball('Solsol_HeadSweep', (-.04, .055, 2.33), (.68, .415, .38), mint)
tapered_curve('Solsol_SpiralCrest',
    [(-.48, .05, 2.33), (-.57, .07, 2.94), (-.28, .08, 3.37),
     (.21, .08, 3.47), (.65, .08, 3.23), (.71, .075, 2.86),
     (.51, .06, 2.71), (.32, .04, 2.82), (.40, .025, 3.00)],
    [.33, .29, .245, .215, .18, .145, .113, .083, .025], mint)
for x in (-.245, .245):
    curve('Solsol_HappyEye', [(x - .10, -.426, 2.13), (x, -.451, 2.19),
                            (x + .10, -.428, 2.13)], .025, ink)
    ball('Solsol_Blush', (x * 1.65, -.37, 1.99), (.125, .036, .066), blush)
ball('Solsol_PursedMouth', (.04, -.459, 1.969), (.061, .032, .069), ink)
ball('Solsol_SoftLip', (.057, -.478, 1.943), (.032, .014, .019), blush)

# A coral scarf wraps around the lower face; broad cloth ribbons flow to the right.
bpy.ops.mesh.primitive_torus_add(major_segments=80, minor_segments=24, major_radius=.47,
                                minor_radius=.10, location=(0, 0, 1.25))
o = own(bpy.context.object, 'Solsol_ScarfWrap', scarf_mat)
o.scale = (1.20, .82, 1)
ball('Solsol_ScarfKnot', (.46, -.20, 1.26), (.16, .13, .14), scarf_mat)


def ribbon(name, points, widths, mat):
    # Sample a smooth Bezier-like Catmull-Rom centerline into a soft textile ribbon.
    points = [Vector(p) for p in points]
    verts = []
    steps = 10
    for i in range(len(points) - 1):
        p0, p1 = points[max(0, i - 1)], points[i]
        p2, p3 = points[i + 1], points[min(len(points) - 1, i + 2)]
        for j in range(steps + (1 if i == len(points) - 2 else 0)):
            t = j / steps
            p = .5 * ((2 * p1) + (-p0 + p2) * t + (2 * p0 - 5 * p1 + 4 * p2 - p3) * t*t + (-p0 + 3*p1 - 3*p2 + p3)*t*t*t)
            width = widths[i] * (1 - t) + widths[i + 1] * t
            verts.extend([tuple(p + Vector((0, -.026, -width / 2))),
                          tuple(p + Vector((0, .026, width / 2)))])
    faces = [(i, i + 1, i + 3, i + 2) for i in range(0, len(verts) - 2, 2)]
    mesh = bpy.data.meshes.new(PREFIX + name)
    mesh.from_pydata(verts, [], faces)
    mesh.update()
    obj = bpy.data.objects.new(PREFIX + name, mesh)
    current.objects.link(obj)
    mesh.materials.append(mat)
    for p in mesh.polygons:
        p.use_smooth = True
    sub = obj.modifiers.new('Flowing_cloth', 'SUBSURF')
    sub.levels = sub.render_levels = 2
    mod = obj.modifiers.new('Plush_cloth_thickness', 'SOLIDIFY')
    mod.thickness = .055
    bevel = obj.modifiers.new('Rounded_scarf_edges', 'BEVEL')
    bevel.width = .025
    bevel.segments = 3
    return obj


ribbon('Solsol_UpperScarfTail', [(.46, -.10, 1.25), (.86, .08, 1.47),
       (1.20, .16, 1.41), (1.55, .16, 1.57)], [.17, .24, .25, .21], scarf_mat)
ribbon('Solsol_LowerScarfTail', [(.47, -.08, 1.22), (.88, .18, 1.11),
       (1.18, .23, 1.18), (1.42, .24, 1.05)], [.12, .18, .19, .15], scarf_mat)
curve('Solsol_ScarfStitch', [(.83, .035, 1.43), (1.18, .113, 1.37), (1.50, .11, 1.52)], .012, scarf_edge)
curve('Solsol_LeftArm', [(-.54, -.02, 1.64), (-.88, -.17, 1.54), (-1.04, -.23, 1.78)], .102, mint)
ball('Solsol_LeftHand', (-1.09, -.24, 1.88), (.17, .14, .18), mint)
curve('Solsol_RightArm', [(.53, -.04, 1.65), (.75, -.25, 1.50), (.86, -.30, 1.75)], .102, mint)
ball('Solsol_RightHand', (.89, -.31, 1.87), (.17, .14, .18), mint)
capsule('Solsol_LeftLeg', (-.22, .04, 1.12), (-.34, -.05, .65), .10, mint)
ball('Solsol_LeftShoe', (-.36, -.17, .49), (.24, .31, .17), mint_dark)
curve('Solsol_LiftedLeg', [(.23, .04, 1.09), (.47, .045, .88), (.61, -.015, 1.06)], .10, mint)
ball('Solsol_LiftedShoe', (.65, -.10, 1.13), (.22, .27, .16), mint_dark)
root_character('Solsol', (6.50, .0, 0), .09)['character_ko'] = '솔솔 — 산들바람'

# Shift the intact original trio left and give each newcomer its own matching stand.
current = collections['Studio']
for index, key in enumerate(('Mongsil', 'Haerong', 'Ttorr')):
    bpy.data.objects[PREFIX + key + '_Root'].location.x -= 3.2
    bpy.data.objects[PREFIX + key + '_Plinth'].location.x -= 3.2
    bpy.data.objects[PREFIX + 'Plinth_trim_' + str(index)].location.x -= 3.2
for key in ('FloatingStar_L', 'Cloud_DreamBubble_1', 'Cloud_DreamBubble_2'):
    bpy.data.objects[PREFIX + key].location.x -= 3.2
for key in ('FloatingStar_R', 'Rain_FloatingBubble'):
    bpy.data.objects[PREFIX + key].location.x -= 3.2
for index, (key, x, y, color) in enumerate([('Songsong', 3.25, .10, 'D4DCEF'),
                                         ('Solsol', 6.50, 0, 'CBE4DA')], 3):
    mat = material(key + '_PlinthMaterial', color, .65, .02, 0)
    bpy.ops.mesh.primitive_cylinder_add(vertices=128, radius=1.43, depth=.27, location=(x, y, .135))
    o = own(bpy.context.object, key + '_Plinth', mat)
    mod = o.modifiers.new('Rolled_plinth_rim', 'BEVEL')
    mod.width = .09
    mod.segments = 5
    o.modifiers.new('Weighted_normals', 'WEIGHTED_NORMAL')
    bpy.ops.mesh.primitive_torus_add(major_segments=96, minor_segments=16,
                                   location=(x, y, .105), major_radius=1.403, minor_radius=.027)
    own(bpy.context.object, 'Plinth_trim_' + str(index), white)
star('Snow_Sparkle', (4.38, .18, 3.20), .17, ice_white, .12)
tapered_curve('Wind_FloatingGust', [(7.61, .23, 2.30), (8.10, .24, 2.35),
              (8.25, .24, 2.56), (8.13, .24, 2.70), (7.99, .24, 2.60)],
              [.025, .036, .037, .033, .006], mint_dark)

camera = scene.camera
target = Vector((.15, 0, 1.75))
camera.location = target + Vector((1.8, -26, 7.1))
camera.rotation_euler = (target - camera.location).to_track_quat('-Z', 'Y').to_euler()
camera.data.ortho_scale = 19.1
for name, x, energy, size in [('Key_Softbox', -6, 2350, 9), ('Fill_Softbox', 7, 1900, 9), ('Rim_Softbox', 1, 2800, 8)]:
    light = bpy.data.objects[PREFIX + name]
    light.location.x = x
    light.data.energy = energy
    light.data.size = size
    light.rotation_euler = (Vector((0, 0, 1.8)) - light.location).to_track_quat('-Z', 'Y').to_euler()
scene.render.engine = 'CYCLES'
scene.cycles.samples = 48
scene.cycles.use_denoising = True
scene.cycles.seed = 21
scene.cycles.max_bounces = 7
scene.cycles.diffuse_bounces = scene.cycles.glossy_bounces = 4
scene.cycles.device = source.cycles.device
scene.render.resolution_x = 1920
scene.render.resolution_y = 960
scene.render.resolution_percentage = 100
scene.render.image_settings.file_format = 'PNG'
scene.render.image_settings.color_mode = 'RGBA'
scene.render.image_settings.color_depth = '8'
scene.render.film_transparent = False
scene.view_settings.view_transform = 'AgX'
scene.view_settings.look = 'AgX - Medium High Contrast'
scene.view_settings.exposure = 0
scene.render.fps = 24
scene.frame_start = scene.frame_end = 1
scene.render.filepath = '//../outputs/weather-fairies/v002/weather-fairies-preview.png'
scene['brief_ko'] = '눈송이 송송과 바람 솔솔 추가 / 기존 3명 포함 5인조 / 파스텔 3D 피규어'
scene['version'] = 'v002'
scene['animation_status'] = 'Still character design; not rigged or animated yet'
for screen in bpy.data.screens:
    for ui in screen.areas:
        if ui.type == 'VIEW_3D':
            ui.spaces.active.region_3d.view_perspective = 'CAMERA'
            ui.spaces.active.overlay.show_overlays = False
bpy.context.view_layer.update()
assert all(signature(bpy.data.scenes[name]) == sig for name, sig in before.items())
report = {'ok': True, 'scene': scene.name, 'objects': len(scene.objects),
          'new_characters': ['송송', '솔솔'], 'all_characters': ['Mongsil', 'Haerong', 'Ttorr', 'Songsong', 'Solsol'],
          'preserved_scenes': list(before), 'preserved_files_sha256': preserved,
          'v001_scene_unchanged': True, 'old_trio_copied_with_independent_data': True,
          'external_assets': []}
(out / 'build-verification.json').write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding='utf-8')
print(json.dumps({'ok': True, 'scene': scene.name, 'objects': len(scene.objects)}, indent=2))
