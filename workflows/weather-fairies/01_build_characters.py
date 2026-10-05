"""사용자 승인: '오늘의 날씨 요정들' 추천안의 대표 3명과 첫 단체 시안 제작.

브리찌 run으로 실행한다. 기존 Scene/객체는 보존하며 새 WF1 Scene만 추가한다.
몽실(졸린 구름), 해롱(씩씩한 햇살), 또르(수줍은 빗방울).
모든 형태/재질은 실제 Blender 기하로 제작한다. 외부 이미지/폰트/모델 없음.
"""
import hashlib
import json
import math
from mathutils import Vector

NAME = 'Weather_Fairies_v001'
PREFIX = 'WF1_'
assert NAME not in bpy.data.scenes, '이미 존재하는 제작본이다. 재실행 대신 후속 수정 스크립트를 사용한다.'
out = PROJECT_ROOT / 'outputs/weather-fairies/v001'
out.mkdir(parents=True, exist_ok=True)


def scene_signature(s):
    return {
        'camera': s.camera.name if s.camera else None,
        'objects': {
            o.name: {'type': o.type, 'data': o.data.name if o.data else None,
                     'matrix': [float(v) for row in o.matrix_world for v in row],
                     'hide_render': o.hide_render}
            for o in s.objects
        },
    }


prior_scenes = {s.name: scene_signature(s) for s in bpy.data.scenes}
prior_files = {}
for path in sorted((PROJECT_ROOT / 'scenes').glob('*.blend')):
    if path.name != 'current.blend':
        prior_files[path.relative_to(PROJECT_ROOT).as_posix()] = hashlib.sha256(path.read_bytes()).hexdigest()

scene = bpy.data.scenes.new(NAME)
bpy.context.window.scene = scene
collections = {}
for name in ('Mongsil', 'Haerong', 'Ttorr', 'Studio'):
    c = bpy.data.collections.new(PREFIX + name)
    scene.collection.children.link(c)
    collections[name] = c
current = collections['Studio']


def rgb(h):
    values = [int(h[i:i + 2], 16) / 255 for i in (0, 2, 4)]
    return tuple(v / 12.92 if v <= .04045 else ((v + .055) / 1.055) ** 2.4 for v in values)


def material(name, color, rough=.4, coat=.12, sss=.025):
    m = bpy.data.materials.new(PREFIX + name)
    m.diffuse_color = (*rgb(color), 1)
    m.use_nodes = True
    p = m.node_tree.nodes['Principled BSDF']
    p.inputs['Base Color'].default_value = (*rgb(color), 1)
    p.inputs['Roughness'].default_value = rough
    p.inputs['Coat Weight'].default_value = coat
    p.inputs['Coat Roughness'].default_value = .27
    p.inputs['Subsurface Weight'].default_value = sss
    return m


cream = material('Cloud_marshmallow', 'FFF5EC', .48, .08, .06)
white = material('Warm_white', 'FFFBF2', .32)
ink = material('Expression_cocoa', '493C50', .32, .1, 0)
blush = material('Cheek_apricot', 'F3A2A8', .57, .05)
yellow = material('Sun_butter', 'FFD46B', .37, .17, .045)
gold = material('Sun_mango', 'F9AC4C', .43, .1)
peach = material('Sun_cheeks', 'F89B79', .5)
lavender = material('Sleep_lilac', 'BBB2E7', .53, .06)
lavender_dark = material('Sleep_seams', '958ABF', .52)
blue = material('Raindrop_blue', '70C9E9', .27, .3, .04)
blue_dark = material('Rain_boots', '51A9CD', .38, .18)
blue_pale = material('Rain_reflection', 'DAF4F5', .34, .2)
star_mat = material('Star_cushion', 'F8D893', .55, .08)
tongue = material('Smile_tongue', 'E99591', .4)
floor_mat = material('Studio_background', 'ECE3E1', .74, 0, 0)
podium_colors = [material('Cloud_plinth', 'DBD1EA', .65, .02),
                 material('Sun_plinth', 'F4D9B0', .65, .02),
                 material('Rain_plinth', 'C4DEE3', .65, .02)]


def own(o, name, mat=None):
    o.name = PREFIX + name
    for c in list(o.users_collection):
        c.objects.unlink(o)
    current.objects.link(o)
    if mat is not None:
        o.data.materials.append(mat)
    if o.type == 'MESH':
        for p in o.data.polygons:
            p.use_smooth = True
    return o


def ball(name, pos, scale, mat, segments=48, rings=32):
    bpy.ops.mesh.primitive_uv_sphere_add(segments=segments, ring_count=rings, location=pos)
    o = own(bpy.context.object, name, mat)
    o.scale = scale
    return o


def curve(name, pts, radius, mat):
    data = bpy.data.curves.new(PREFIX + name, 'CURVE')
    data.dimensions = '3D'
    data.resolution_u = 16
    data.bevel_depth = radius
    data.bevel_resolution = 5
    data.use_fill_caps = True
    spline = data.splines.new('BEZIER')
    spline.bezier_points.add(len(pts) - 1)
    for point, pos in zip(spline.bezier_points, pts):
        point.co = pos
        point.handle_left_type = point.handle_right_type = 'AUTO'
    o = bpy.data.objects.new(PREFIX + name, data)
    current.objects.link(o)
    data.materials.append(mat)
    return o


def capsule(name, a, b, r, mat, squash=1):
    a, b = Vector(a), Vector(b)
    o = ball(name, (a + b) / 2, (r, r * squash, (b - a).length / 2 + r), mat)
    o.rotation_euler = (b - a).to_track_quat('Z', 'Y').to_euler()
    return o


def star(name, pos, size, mat, angle=0):
    # Rounded, inflated star mesh with front/back centers; subdivision gives a cushion.
    points = []
    n = 10
    for i in range(n):
        t = math.pi / 2 + i * math.tau / n + angle
        r = size * (1 if i % 2 == 0 else .54)
        points.append((r * math.cos(t), r * math.sin(t)))
    vertices = []
    for depth in (-.12 * size, .12 * size):
        vertices += [(x, depth, z) for x, z in points]
    vertices += [(0, -.42 * size, 0), (0, .42 * size, 0)]
    faces = []
    for i in range(n):
        j = (i + 1) % n
        faces.extend([(20, i, j), (21, j + n, i + n), (i, i + n, j + n, j)])
    mesh = bpy.data.meshes.new(PREFIX + name)
    mesh.from_pydata(vertices, [], faces)
    mesh.update()
    o = bpy.data.objects.new(PREFIX + name, mesh)
    current.objects.link(o)
    o.location = pos
    mesh.materials.append(mat)
    for p in mesh.polygons:
        p.use_smooth = True
    bevel = o.modifiers.new('Soft_sewn_corners', 'BEVEL')
    bevel.width = .075 * size
    bevel.segments = 3
    sub = o.modifiers.new('Inflated_cushion', 'SUBSURF')
    sub.levels = sub.render_levels = 2
    return o


def root_character(key, origin, rotation=0):
    root = bpy.data.objects.new(PREFIX + key + '_Root', None)
    collections[key].objects.link(root)
    root.empty_display_type = 'PLAIN_AXES'
    root.location = origin
    root.rotation_euler.z = rotation
    for o in list(collections[key].objects):
        if o != root:
            o.parent = root
    root['character_ko'] = {'Mongsil': '몽실 — 졸린 구름', 'Haerong': '해롱 — 씩씩한 햇살',
                            'Ttorr': '또르 — 소심한 빗방울'}[key]
    return root


# 몽실: 구름의 돌출부를 실제 하나의 매끈한 메시로 융합한다.
current = collections['Mongsil']
parts = []
for name, pos, scale in [
    ('Core', (0, 0, 1.92), (1.01, .58, .66)),
    ('Lobe_L', (-.81, .025, 1.99), (.59, .51, .56)),
    ('Lobe_R', (.80, .055, 2.03), (.59, .50, .57)),
    ('Crown_L', (-.46, .055, 2.44), (.59, .50, .59)),
    ('Crown_R', (.23, .085, 2.55), (.66, .52, .68)),
]:
    parts.append(ball('Mongsil_' + name, pos, scale, cream))
bpy.ops.object.select_all(action='DESELECT')
for o in parts:
    o.select_set(True)
bpy.context.view_layer.objects.active = parts[0]
bpy.ops.object.join()
cloud = bpy.context.object
cloud.name = PREFIX + 'Mongsil_CloudBody'
bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
remesh = cloud.modifiers.new('Fused_marshmallow', 'REMESH')
remesh.mode = 'VOXEL'
remesh.voxel_size = .045
remesh.use_smooth_shade = True
bpy.ops.object.modifier_apply(modifier=remesh.name)
smooth = cloud.modifiers.new('Soft_cloud_transitions', 'SMOOTH')
smooth.factor = 1.35
smooth.iterations = 6
sub = cloud.modifiers.new('Silky_surface', 'SUBSURF')
sub.levels = sub.render_levels = 1
for x in (-.37, .36):
    curve('Mongsil_SleepingEye', [(x - .14, -.594, 2.04), (x, -.614, 1.977),
                                (x + .14, -.586, 2.04)], .027, ink)
    ball('Mongsil_Blush', (x * 1.53, -.536, 1.88), (.17, .047, .085), blush)
curve('Mongsil_TinyMouth', [(-.055, -.600, 1.84), (0, -.617, 1.818),
                          (.055, -.600, 1.84)], .021, ink)
for x in (-.38, .38):
    capsule('Mongsil_DanglingLeg', (x, -.02, 1.19), (x, -.11, .84), .125, cream)
    ball('Mongsil_LilacSlipper', (x, -.24, .77), (.25, .35, .16), lavender)
    curve('Mongsil_SlipperSeam', [(x - .17, -.39, .86), (x, -.51, .885),
                                (x + .17, -.39, .86)], .012, lavender_dark)
star('Mongsil_HuggedStar', (0, -.69, 1.38), .55, star_mat, -.15)
capsule('Mongsil_LeftHug', (-.87, -.22, 1.62), (-.42, -.72, 1.30), .155, cream)
capsule('Mongsil_RightHug', (.90, -.19, 1.66), (.43, -.71, 1.31), .155, cream)
ball('Mongsil_LeftMitten', (-.39, -.82, 1.30), (.18, .14, .17), cream)
ball('Mongsil_RightMitten', (.40, -.82, 1.30), (.18, .14, .17), cream)
# A three-piece lilac sleeping tuft, with a small soft pompom.
capsule('Mongsil_SleepTuftBase', (-.67, .02, 2.80), (-.48, .03, 3.10), .22, lavender)
capsule('Mongsil_SleepTuftTip', (-.49, .035, 3.09), (-.21, .02, 3.07), .135, lavender)
ball('Mongsil_Pompom', (-.16, -.005, 3.01), (.15, .15, .15), white)
root_character('Mongsil', (-3.20, .03, 0), -.055)

# 해롱: 얼굴 뒤로 둥글게 마감한 12개 햇살과 힘찬 손인사.
current = collections['Haerong']
for i in range(12):
    angle = i * math.tau / 12
    a = (1.005 * math.sin(angle), .035, 2.12 + 1.005 * math.cos(angle))
    b = (1.28 * math.sin(angle + .035), .04, 2.12 + 1.28 * math.cos(angle + .035))
    capsule('Haerong_Ray_%02d' % i, a, b, .145, gold if i % 2 else yellow)
ball('Haerong_SunBody', (0, -.01, 2.12), (.94, .51, .94), yellow, 64, 40)
for x in (-.27, .27):
    ball('Haerong_BrightEye', (x, -.498, 2.20), (.069, .040, .105), ink)
    ball('Haerong_EyeGlint', (x - .015, -.534, 2.233), (.019, .014, .024), white, 24, 16)
    curve('Haerong_Brow', [(x - .072, -.448, 2.43), (x, -.458, 2.448),
                          (x + .071, -.443, 2.43)], .016, gold)
    ball('Haerong_Blush', (x * 1.75, -.438, 2.02), (.145, .030, .079), peach)
ball('Haerong_OpenSmile', (0, -.498, 1.94), (.155, .033, .123), ink)
ball('Haerong_Tongue', (0, -.530, 1.902), (.094, .017, .039), tongue)
for x in (-.33, .33):
    capsule('Haerong_Leg', (x, 0, 1.13), (x * 1.18, -.06, .66), .13, yellow)
    ball('Haerong_LittleShoe', (x * 1.18, -.18, .50), (.265, .36, .18), gold)
capsule('Haerong_RestingArm', (-.88, -.025, 1.87), (-1.05, -.24, 1.46), .14, yellow)
ball('Haerong_RestingHand', (-1.05, -.25, 1.39), (.18, .16, .21), yellow)
curve('Haerong_WavingArm', [(.84, -.015, 1.90), (1.23, -.05, 2.07),
                           (1.49, -.07, 2.52)], .13, yellow)
ball('Haerong_WavingPalm', (1.48, -.07, 2.68), (.20, .15, .24), yellow)
ball('Haerong_WavingThumb', (1.29, -.10, 2.65), (.12, .14, .14), yellow)
curve('Haerong_PalmCrease', [(1.43, -.214, 2.72), (1.49, -.225, 2.73),
                           (1.56, -.208, 2.71)], .010, gold)
root_character('Haerong', (0, .38, 0), .08)

# 또르: 매끄러운 비대칭 물방울 형상. 위쪽 꼭지가 살짝 휜다.
current = collections['Ttorr']
profile = [(0, 0), (.07, .36), (.18, .58), (.37, .75), (.62, .80),
           (.88, .75), (1.10, .63), (1.31, .47), (1.51, .29),
           (1.71, .14), (1.88, .055), (2.03, 0)]
verts = []
segments = 64
for z, r in profile:
    bend = .25 * max(0, (z - 1.20) / .83) ** 2
    for i in range(segments):
        a = math.tau * i / segments
        verts.append((bend + r * math.cos(a), .79 * r * math.sin(a), .80 + z))
faces = []
for j in range(len(profile) - 1):
    for i in range(segments):
        k = (i + 1) % segments
        faces.append((j * segments + i, j * segments + k,
                      (j + 1) * segments + k, (j + 1) * segments + i))
mesh = bpy.data.meshes.new(PREFIX + 'Ttorr_DropMesh')
mesh.from_pydata(verts, [], faces)
mesh.update()
drop = bpy.data.objects.new(PREFIX + 'Ttorr_DropBody', mesh)
current.objects.link(drop)
mesh.materials.append(blue)
for p in mesh.polygons:
    p.use_smooth = True
sub = drop.modifiers.new('Round_water_silhouette', 'SUBSURF')
sub.levels = sub.render_levels = 2
for x in (-.225, .225):
    ball('Ttorr_ShyEye', (x, -.544, 1.79), (.058, .038, .087), ink)
    ball('Ttorr_EyeGlint', (x - .012, -.579, 1.815), (.016, .011, .020), white, 24, 16)
    ball('Ttorr_Blush', (x * 1.78, -.498, 1.61), (.13, .026, .066), blush)
    curve('Ttorr_WorriedBrow', [(x - .065, -.480, 1.996 + (.02 if x < 0 else 0)),
                              (x + .065, -.480, 1.996 + (.02 if x > 0 else 0))], .014, blue_dark)
curve('Ttorr_SmallSmile', [(-.050, -.607, 1.57), (0, -.621, 1.548),
                        (.050, -.607, 1.57)], .017, ink)
reflection = ball('Ttorr_SoftPaintHighlight', (-.25, -.364, 2.15), (.062, .028, .19), blue_pale)
reflection.rotation_euler.y = -.36
ball('Ttorr_SecondHighlight', (-.37, -.429, 1.99), (.034, .018, .04), blue_pale)
for x in (-.26, .26):
    capsule('Ttorr_Leg', (x, .025, .94), (x, -.025, .64), .10, blue)
    ball('Ttorr_RainBoot', (x, -.16, .48), (.22, .31, .21), blue_dark)
    ball('Ttorr_BootCuff', (x, -.01, .67), (.16, .17, .055), blue_pale)
curve('Ttorr_LeftArm', [(-.66, -.06, 1.35), (-.63, -.46, 1.21),
                      (-.16, -.666, 1.22)], .106, blue)
curve('Ttorr_RightArm', [(.67, -.07, 1.37), (.59, -.47, 1.22),
                       (.12, -.679, 1.23)], .106, blue)
ball('Ttorr_LeftClaspedHand', (-.105, -.723, 1.22), (.145, .115, .13), blue)
ball('Ttorr_RightClaspedHand', (.112, -.714, 1.22), (.145, .115, .13), blue)
root_character('Ttorr', (3.20, -.02, 0), .13)

# 파스텔 전시대와 부드러운 무한 배경. 장식은 캐릭터보다 작게 제한한다.
current = collections['Studio']
for i, (x, y, radius) in enumerate([(-3.2, .03, 1.55), (0, .38, 1.57), (3.2, -.02, 1.43)]):
    bpy.ops.mesh.primitive_cylinder_add(vertices=128, radius=radius, depth=.27, location=(x, y, .135))
    o = own(bpy.context.object, ['Mongsil', 'Haerong', 'Ttorr'][i] + '_Plinth', podium_colors[i])
    mod = o.modifiers.new('Rolled_plinth_rim', 'BEVEL')
    mod.width = .09
    mod.segments = 5
    o.modifiers.new('Weighted_normals', 'WEIGHTED_NORMAL')
    # A small secondary ring makes the plinth read as a finished collectible stand.
    bpy.ops.mesh.primitive_torus_add(major_segments=96, minor_segments=16, location=(x, y, .105),
                                    major_radius=radius - .027, minor_radius=.027)
    own(bpy.context.object, 'Plinth_trim_%s' % i, white)
bpy.ops.mesh.primitive_plane_add(size=200, location=(0, 0, -.025))
own(bpy.context.object, 'Studio_Floor', floor_mat)
star('FloatingStar_L', (-4.56, .08, 3.44), .22, star_mat, .16)
star('FloatingStar_R', (4.40, .16, 3.28), .16, white, -.1)
ball('Cloud_DreamBubble_1', (-4.57, .12, 2.76), (.10, .10, .10), lavender)
ball('Cloud_DreamBubble_2', (-4.77, .20, 3.05), (.067, .067, .067), cream)
ball('Rain_FloatingBubble', (4.32, .20, 2.78), (.092, .092, .12), blue_pale)


def area(name, pos, energy, size, color, target):
    data = bpy.data.lights.new(PREFIX + name, 'AREA')
    data.energy = energy
    data.shape = 'DISK'
    data.size = size
    data.color = rgb(color)
    o = bpy.data.objects.new(PREFIX + name, data)
    current.objects.link(o)
    o.location = pos
    o.rotation_euler = (Vector(target) - o.location).to_track_quat('-Z', 'Y').to_euler()
    return o


area('Key_Softbox', (-5, -7, 10), 1650, 7.0, 'FFF0DD', (0, 0, 1.7))
area('Fill_Softbox', (6, -3, 6), 1150, 6.0, 'DCEFFF', (0, 0, 1.8))
area('Rim_Softbox', (1, 5, 8), 1950, 5.0, 'FFF3E8', (0, 0, 1.8))
world = bpy.data.worlds.new(PREFIX + 'StudioWorld')
world.use_nodes = True
world.node_tree.nodes['Background'].inputs['Color'].default_value = (*rgb('E6E6F5'), 1)
world.node_tree.nodes['Background'].inputs['Strength'].default_value = .32
scene.world = world
camera_data = bpy.data.cameras.new(PREFIX + 'Camera')
camera = bpy.data.objects.new(PREFIX + 'Camera', camera_data)
current.objects.link(camera)
camera.location = (3.7, -23, 8.6)
target = Vector((0, 0, 1.70))
camera.rotation_euler = (target - camera.location).to_track_quat('-Z', 'Y').to_euler()
camera_data.type = 'ORTHO'
camera_data.ortho_scale = 12.2
camera_data.lens = 52
scene.camera = camera
scene.render.engine = 'CYCLES'
scene.cycles.samples = 48
scene.cycles.use_denoising = True
scene.cycles.seed = 21
scene.cycles.use_animated_seed = False
scene.cycles.max_bounces = 7
scene.cycles.diffuse_bounces = 4
scene.cycles.glossy_bounces = 4
prefs = bpy.context.preferences.addons['cycles'].preferences
prefs.compute_device_type = 'OPTIX'
prefs.get_devices()
gpu_names = []
for device in prefs.devices:
    device.use = device.type == 'OPTIX'
    if device.use:
        gpu_names.append(device.name)
scene.cycles.device = 'GPU' if gpu_names else 'CPU'
scene.render.resolution_x = 1440
scene.render.resolution_y = 960
scene.render.resolution_percentage = 100
scene.render.image_settings.file_format = 'PNG'
scene.render.image_settings.color_mode = 'RGBA'
scene.render.image_settings.color_depth = '8'
scene.render.film_transparent = False
scene.render.filepath = '//../outputs/weather-fairies/v001/weather-fairies-preview.png'
scene.view_settings.view_transform = 'AgX'
scene.view_settings.look = 'AgX - Medium High Contrast'
scene.view_settings.exposure = .55
scene.render.fps = 24
scene.frame_start = scene.frame_end = 1
scene['brief_ko'] = '오늘의 날씨 요정들: 몽실·해롱·또르 / 파스텔 말랑한 피규어 / 첫 단체 시안'
scene['version'] = 'v001'
scene['animation_status'] = 'Still character design; not rigged or animated yet'
for screen in bpy.data.screens:
    for area_ui in screen.areas:
        if area_ui.type == 'VIEW_3D':
            area_ui.spaces.active.region_3d.view_perspective = 'CAMERA'
            area_ui.spaces.active.overlay.show_overlays = False
            area_ui.spaces.active.shading.type = 'MATERIAL'
bpy.context.view_layer.update()
assert all(scene_signature(bpy.data.scenes[n]) == sig for n, sig in prior_scenes.items())
report = {'ok': True, 'scene': NAME, 'camera': camera.name, 'objects': len(scene.objects),
          'characters': ['몽실', '해롱', '또르'], 'old_scenes_unchanged': list(prior_scenes),
          'existing_source_sha256': prior_files, 'gpu': gpu_names, 'external_assets': [],
          'stage': 'first_model_and_lighting_preview'}
(out / 'build-verification.json').write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding='utf-8')
print(json.dumps(report, ensure_ascii=False, indent=2))
