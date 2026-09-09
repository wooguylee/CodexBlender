"""1단계: 실제 더가치 SVG 윤곽을 입체화. 파란 집=ㄷ, 노란 사람=ㅊ.

새 전용 Scene을 만들며 이전 시연 Scene과 객체는 보존한다.
Blender의 SVG 가져오기 애드온/폰트/외부 서비스에 의존하지 않는다.
"""
import json
import math
import re
from mathutils import Vector

NAME = 'Thegachi_Opening_v001'
assert NAME not in bpy.data.scenes, 'Scene already exists; inspect it instead of overwriting.'
scene = bpy.data.scenes.new(NAME)
bpy.context.window.scene = scene
collection = bpy.data.collections.new(NAME)
scene.collection.children.link(collection)


def own(obj):
    collection.objects.link(obj)
    return obj


def linear(value):
    return value / 12.92 if value <= .04045 else ((value + .055) / 1.055) ** 2.4


def rgb(code):
    return tuple(linear(int(code[i:i+2], 16) / 255) for i in (0, 2, 4))


def material(name, code, metal=.0, rough=.3):
    mat = bpy.data.materials.new(name)
    mat.use_nodes = True
    p = mat.node_tree.nodes.get('Principled BSDF')
    p.inputs['Base Color'].default_value = (*rgb(code), 1)
    p.inputs['Metallic'].default_value = metal
    p.inputs['Roughness'].default_value = rough
    mat.diffuse_color = (*rgb(code), 1)
    return mat


def svg_segments(text):
    """Read the original paths' M/L/H/V/C/S/Z, including relative coordinates."""
    tokens = re.findall(r'[a-zA-Z]|[-+]?(?:\d*\.\d+|\d+\.?\d*)(?:[eE][-+]?\d+)?', text)
    i, command, cur, start, previous_control = 0, None, (0., 0.), None, None
    segments = []
    previous_cmd = None
    while i < len(tokens):
        if tokens[i].isalpha():
            command = tokens[i]
            i += 1
        upper, relative = command.upper(), command.islower()
        if upper == 'Z':
            if cur != start:
                segments.append((cur, cur, start, start))
            cur, previous_control, previous_cmd = start, None, upper
            command = None
            continue
        n = {'M': 2, 'L': 2, 'H': 1, 'V': 1, 'C': 6, 'S': 4}[upper]
        values = list(map(float, tokens[i:i+n]))
        assert len(values) == n
        i += n
        def point(x, y):
            return (x + cur[0], y + cur[1]) if relative else (x, y)
        if upper in ('M', 'L'):
            end = point(*values)
            if upper == 'M':
                assert start is None, 'Unexpected compound SVG path.'
                start = end
                command = 'l' if relative else 'L'
            else:
                segments.append((cur, cur, end, end))
            previous_control = None
        elif upper in ('H', 'V'):
            end = ((values[0] + cur[0] if relative else values[0]), cur[1]) if upper == 'H' else (cur[0], (values[0] + cur[1] if relative else values[0]))
            if end != cur:
                segments.append((cur, cur, end, end))
            previous_control = None
        else:
            if upper == 'C':
                c1, c2, end = point(*values[:2]), point(*values[2:4]), point(*values[4:6])
            else:
                c1 = (2*cur[0]-previous_control[0], 2*cur[1]-previous_control[1]) if previous_cmd in ('C', 'S') and previous_control else cur
                c2, end = point(*values[:2]), point(*values[2:4])
            segments.append((cur, c1, c2, end))
            previous_control = c2
        cur, previous_cmd = end, upper
    return segments


blue = material('TG_Blue_Gradient', '036eb8')
nodes, links = blue.node_tree.nodes, blue.node_tree.links
tex = nodes.new('ShaderNodeTexCoord')
sep = nodes.new('ShaderNodeSeparateXYZ')
ramp = nodes.new('ShaderNodeValToRGB')
ramp.color_ramp.elements[0].color = (*rgb('036eb8'), 1)
ramp.color_ramp.elements[1].color = (*rgb('171c61'), 1)
links.new(tex.outputs['Generated'], sep.inputs[0])
links.new(sep.outputs['X'], ramp.inputs[0])
links.new(ramp.outputs[0], nodes.get('Principled BSDF').inputs['Base Color'])
yellow = material('TG_Yellow_Person', 'f9b341')
silver = material('TG_Silver_Letters', 'b5b5b6')
SCALE = .025
source = json.loads((PROJECT_ROOT / 'assets/thegachi/wordmark-paths.json').read_text(encoding='utf-8'))
metadata = []
for part in source:
    segments = svg_segments(part['d'])
    # Remove only zero-length segments; preserve every original cubic curve.
    segments = [s for s in segments if not (s[0] == s[1] == s[2] == s[3])]
    xs = [p[0] for s in segments for p in s]
    ys = [p[1] for s in segments for p in s]
    cx, cy = (min(xs)+max(xs))/2, (min(ys)+max(ys))/2
    curve = bpy.data.curves.new('TG_Path_' + part['name'], 'CURVE')
    curve.dimensions = '2D'
    curve.resolution_u = 16
    curve.fill_mode = 'BOTH'
    curve.extrude = .13
    curve.bevel_depth = .018
    curve.bevel_resolution = 4
    spline = curve.splines.new('BEZIER')
    spline.bezier_points.add(len(segments)-1)
    spline.use_cyclic_u = True
    def co(p):
        return ((p[0]-cx)*SCALE, (cy-p[1])*SCALE, 0)
    for j, seg in enumerate(segments):
        bp = spline.bezier_points[j]
        bp.handle_left_type = bp.handle_right_type = 'FREE'
        bp.co = co(seg[0])
        bp.handle_right = co(seg[1])
        bp.handle_left = co(segments[j-1][2])
    obj = own(bpy.data.objects.new('TG_' + part['name'], curve))
    obj.location = ((cx-368.59/2)*SCALE, (106.02/2-cy)*SCALE, 0)
    curve.materials.append({'cls-1': silver, 'cls-2': blue, 'cls-3': yellow}[part['class']])
    obj['svg_center'] = [cx, cy]
    obj['final_location'] = list(obj.location)
    obj['brand_meaning'] = {'house_d': '더의 ㄷ을 형상화한 파란 집', 'person_ch': '치의 ㅊ을 형상화한 노란 사람'}.get(part['name'], '원본 더가치 글자')
    metadata.append({'object': obj.name, 'cubic_segments': len(segments), 'source_center': [cx, cy]})

back = material('TG_Backdrop', 'e7e9ee', rough=.65)
mesh = bpy.data.meshes.new('TG_BackdropMesh')
mesh.from_pydata([(-100,-100,0),(100,-100,0),(100,100,0),(-100,100,0)], [], [(0,1,2,3)])
plane = own(bpy.data.objects.new('TG_Backdrop', mesh))
plane.location.z = -.45
mesh.materials.append(back)


def aim(obj, target):
    obj.rotation_euler = (Vector(target)-obj.location).to_track_quat('-Z', 'Y').to_euler()


cam = own(bpy.data.objects.new('TG_Camera', bpy.data.cameras.new('TG_Camera')))
cam.location = (0, 0, 22)
cam.data.type = 'ORTHO'
cam.data.ortho_scale = 12.7
aim(cam, (0,0,0))
scene.camera = cam
for name, loc, energy, size, color in [
    ('TG_Key', (-4,5,7), 1200, 7, (1,.94,.87)),
    ('TG_Fill', (5,1,6), 850, 5, (.75,.85,1)),
    ('TG_Top', (0,-4,5), 600, 4, (1,1,1)),
]:
    light = own(bpy.data.objects.new(name, bpy.data.lights.new(name, 'AREA')))
    light.location, light.data.energy, light.data.size, light.data.color = loc, energy, size, color
    aim(light, (0,0,0))
scene.world = bpy.data.worlds.new('TG_World')
scene.world.use_nodes = True
scene.world.node_tree.nodes['Background'].inputs[0].default_value = (.5,.5,.5,1)
scene.world.node_tree.nodes['Background'].inputs[1].default_value = .3
scene.render.engine = 'CYCLES'
scene.cycles.samples = 24
scene.cycles.use_denoising = True
scene.cycles.device = 'CPU'
scene.render.resolution_x, scene.render.resolution_y = 1280, 720
scene.render.resolution_percentage = 100
scene.render.image_settings.file_format = 'PNG'
scene.view_settings.view_transform = 'AgX'
scene.render.fps = 24
scene.frame_end = 144
scene['brand_meaning'] = '파란 집=더의 ㄷ, 노란 사람=치의 ㅊ'
scene['source'] = '//../assets/thegachi/wordmark-original.svg'
scene.frame_set(120)
for screen in bpy.data.screens:
    for area in screen.areas:
        if area.type == 'VIEW_3D':
            area.spaces.active.region_3d.view_perspective = 'CAMERA'
            area.spaces.active.overlay.show_overlays = False
(OUTPUT_DIR / 'geometry.json').write_text(json.dumps(metadata, ensure_ascii=False, indent=2), encoding='utf-8')
print('Created exact vector 3D wordmark in a separate scene; original Scene preserved.')
