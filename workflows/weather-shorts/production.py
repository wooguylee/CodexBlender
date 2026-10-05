"""날씨 요정 단편 공통 제작 도구. 기존 v002를 독립 복제하고 실제 3D 컨트롤을 만든다."""
import bpy
import math
from mathutils import Vector, Matrix

KEYS = ('Mongsil', 'Haerong', 'Ttorr', 'Songsong', 'Solsol')
FPS = 24


def rgb(h):
    values = [int(h[i:i+2], 16)/255 for i in (0, 2, 4)]
    return tuple(v/12.92 if v <= .04045 else ((v+.055)/1.055)**2.4 for v in values)


class Production:
    def __init__(self, root, number, title, duration):
        self.root, self.number, self.title, self.duration = root, number, title, duration
        self.prefix = f'WS{number}_'
        self.name = f'Weather_Short_{number:02d}_v001'
        assert self.name not in bpy.data.scenes
        self.scene = bpy.data.scenes.new(self.name)
        bpy.context.window.scene = self.scene
        self.characters, self.controls, self.base, self.objects = {}, {}, {}, {}
        self.materials = {}
        self.collection = bpy.data.collections.new(self.prefix + 'Stage')
        self.scene.collection.children.link(self.collection)
        copied_mats = {}
        for key in KEYS:
            col = bpy.data.collections.new(self.prefix + key)
            self.scene.collection.children.link(col)
            mapping = {}
            for old in bpy.data.collections['WF2_' + key].objects:
                obj = old.copy()
                obj.name = self.prefix + old.name.removeprefix('WF2_')
                if old.data:
                    obj.data = old.data.copy()
                    if hasattr(obj.data, 'materials'):
                        obj.data.materials.clear()
                        for old_mat in old.data.materials:
                            if old_mat not in copied_mats:
                                m = old_mat.copy()
                                m.name = self.prefix + old_mat.name.removeprefix('WF2_')
                                copied_mats[old_mat] = m
                            obj.data.materials.append(copied_mats[old_mat])
                col.objects.link(obj)
                mapping[old] = obj
                self.objects[obj.name.removeprefix(self.prefix)] = obj
            for old, obj in mapping.items():
                obj.parent = mapping.get(old.parent)
            root_obj = self.objects[key + '_Root']
            root_obj.location = (0, 0, 0)
            root_obj.rotation_euler = (0, 0, 0)
            self.characters[key] = col
            self.controls[key] = {'root': root_obj}
            self.make_limbs(key)
        self.collection = bpy.data.collections[self.prefix + 'Stage']
        self.material('floor', 'E9E3ED', emission=True)
        self.material('shadow', 'D1C8D7', emission=True)
        self.material('white', 'FFF9EF')
        self.material('gold', 'FFD36C')
        self.material('pink', 'E6A1B5')
        self.material('mint', '8BD5B1')
        self.material('blue', '79BEDF')
        self.material('purple', 'A79BD4')
        self.material('dark', '4B4059')
        self.material('leaf', '75B57D')
        self.material('soil', 'B47D67')
        self.material('ice', 'C5E5F5')
        self.material('pollen', 'FFDC63')
        self.ball('Floor', (0, 0, -.30), (200, 200, .58), 'floor')
        self.shadows = {key: self.ball(key + '_GroundShadow', (0, 0, .286), (.72, .42, .004), 'shadow', segments=32) for key in KEYS}
        self.setup_camera()
        self.setup_lighting()
        self.dynamic = set()
        self.events = []
        self.bind_rest()

    def material(self, name, color, emission=False, rough=.45):
        m = bpy.data.materials.new(self.prefix + name)
        m.diffuse_color = (*rgb(color), 1)
        m.use_nodes = True
        if emission:
            nodes = m.node_tree.nodes
            nodes.clear()
            p = nodes.new('ShaderNodeEmission')
            p.inputs['Color'].default_value = (*rgb(color), 1)
            o = nodes.new('ShaderNodeOutputMaterial')
            m.node_tree.links.new(p.outputs[0], o.inputs['Surface'])
        else:
            p = m.node_tree.nodes['Principled BSDF']
            p.inputs['Base Color'].default_value = (*rgb(color), 1)
            p.inputs['Roughness'].default_value = rough
            p.inputs['Coat Weight'].default_value = .1
        self.materials[name] = m
        return m

    def own(self, obj, name, mat):
        obj.name = self.prefix + name
        for col in list(obj.users_collection):
            col.objects.unlink(obj)
        self.collection.objects.link(obj)
        obj.data.materials.append(self.materials[mat] if isinstance(mat, str) else mat)
        if obj.type == 'MESH':
            for p in obj.data.polygons:
                p.use_smooth = True
        self.objects[name] = obj
        return obj

    def ball(self, name, pos, scale, mat, segments=32):
        bpy.ops.mesh.primitive_uv_sphere_add(segments=segments, ring_count=20, location=pos)
        obj = self.own(bpy.context.object, name, mat)
        obj.scale = scale
        return obj

    def cube(self, name, pos, scale, mat, bevel=.10):
        bpy.ops.mesh.primitive_cube_add(size=1, location=pos)
        obj = self.own(bpy.context.object, name, mat)
        obj.dimensions = scale
        bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
        if bevel:
            mod = obj.modifiers.new('Soft_edges', 'BEVEL')
            mod.width, mod.segments = bevel, 3
            obj.modifiers.new('Face_normals', 'WEIGHTED_NORMAL')
        return obj

    def curve(self, name, points, radius, mat):
        data = bpy.data.curves.new(self.prefix + name, 'CURVE')
        data.dimensions = '3D'
        data.bevel_depth, data.bevel_resolution, data.resolution_u = radius, 3, 12
        data.use_fill_caps = True
        spline = data.splines.new('BEZIER')
        spline.bezier_points.add(len(points)-1)
        for p, co in zip(spline.bezier_points, points):
            p.co = co
            p.handle_left_type = p.handle_right_type = 'AUTO'
        obj = bpy.data.objects.new(self.prefix + name, data)
        self.collection.objects.link(obj)
        data.materials.append(self.materials[mat])
        self.objects[name] = obj
        return obj

    def text(self, name, body, pos, size=.5, mat='dark'):
        data = bpy.data.curves.new(self.prefix + name, 'FONT')
        data.body, data.align_x, data.align_y, data.size = body, 'CENTER', 'CENTER', size
        obj = bpy.data.objects.new(self.prefix + name, data)
        self.collection.objects.link(obj)
        obj.location = pos
        obj.rotation_euler = self.scene.camera.rotation_euler
        data.materials.append(self.materials[mat])
        self.objects[name] = obj
        return obj

    def empty(self, name, pos=(0,0,0)):
        obj = bpy.data.objects.new(self.prefix + name, None)
        self.collection.objects.link(obj)
        obj.location = pos
        self.objects[name] = obj
        return obj

    def parent_local(self, obj, parent):
        matrix = obj.matrix_basis.copy()
        obj.parent = parent
        obj.matrix_parent_inverse = Matrix.Identity(4)
        obj.matrix_basis = parent.matrix_basis.inverted() @ matrix

    def make_limbs(self, key):
        root = self.controls[key]['root']
        col = self.characters[key]
        groups = {'armL': [], 'armR': [], 'legL': [], 'legR': []}
        for obj in list(col.objects):
            name = obj.name.removeprefix(self.prefix + key + '_')
            if any(part in name for part in ('Leg', 'Shoe', 'Slipper', 'Boot')):
                groups['legL' if obj.location.x < 0 else 'legR'].append(obj)
            elif any(part in name for part in ('Arm', 'Hug', 'Mitten', 'Hand', 'Thumb', 'Palm', 'Crease')) and 'HuggedStar' not in name:
                side = 'armL' if any(s in name for s in ('Left', 'Resting')) else 'armR'
                groups[side].append(obj)
        for name, objects in groups.items():
            pivot = Vector(((-.55 if name.endswith('L') else .55) if name.startswith('arm') else (-.27 if name.endswith('L') else .27), 0, 1.68 if name.startswith('arm') else 1.13))
            control = bpy.data.objects.new(self.prefix + key + '_' + name, None)
            col.objects.link(control)
            control.parent, control.location = root, pivot
            for obj in objects:
                matrix = obj.matrix_basis.copy()
                obj.parent = control
                obj.matrix_parent_inverse = Matrix.Identity(4)
                obj.matrix_basis = Matrix.Translation(-pivot) @ matrix
            self.controls[key][name] = control

    def setup_camera(self):
        data = bpy.data.cameras.new(self.prefix + 'Camera')
        camera = bpy.data.objects.new(self.prefix + 'Camera', data)
        self.collection.objects.link(camera)
        camera.location = (0, -25, 8.8)
        camera.rotation_euler = (Vector((0, 0, 1.65)) - camera.location).to_track_quat('-Z','Y').to_euler()
        data.type, data.ortho_scale = 'ORTHO', 17.4
        self.scene.camera = camera

    def setup_lighting(self):
        for name, pos, energy, size, color in [('Key',(-6,-8,10),2100,9,'FFF0DC'),('Fill',(7,-4,7),1550,8,'DBEDFF'),('Rim',(1,5,9),2300,8,'FFF1E5')]:
            data = bpy.data.lights.new(self.prefix + name, 'AREA')
            data.energy, data.size, data.color = energy, size, rgb(color)
            data.use_shadow = False
            obj = bpy.data.objects.new(self.prefix + name, data)
            self.collection.objects.link(obj)
            obj.location = pos
            obj.rotation_euler = (Vector((0,0,1.8))-obj.location).to_track_quat('-Z','Y').to_euler()
        world = bpy.data.worlds.new(self.prefix + 'World')
        world.use_nodes = True
        world.node_tree.nodes['Background'].inputs['Color'].default_value = (*rgb('E3DEF0'),1)
        world.node_tree.nodes['Background'].inputs['Strength'].default_value = .45
        self.scene.world = world
        self.scene.render.engine = 'BLENDER_EEVEE'
        self.scene.eevee.taa_render_samples = 16
        self.scene.eevee.use_raytracing = False
        self.scene.render.resolution_x, self.scene.render.resolution_y = 1920, 1080
        self.scene.render.resolution_percentage = 100
        self.scene.render.image_settings.file_format = 'PNG'
        self.scene.render.image_settings.color_mode = 'RGBA'
        self.scene.render.image_settings.color_depth = '8'
        self.scene.render.image_settings.compression = 15
        self.scene.render.fps = FPS
        self.scene.render.use_file_extension = True
        self.scene.view_settings.view_transform = 'AgX'
        self.scene.view_settings.look = 'AgX - Medium High Contrast'
        self.scene.view_settings.exposure = 0
        self.scene.frame_start, self.scene.frame_end = 1, self.duration * FPS
        self.scene['story_title'] = self.title
        self.scene['render_note'] = 'Actual 3D animation. Fixed studio background and deterministic keyframes.'

    def bind_rest(self):
        for obj in self.scene.objects:
            self.base[obj.name] = (obj.location.copy(), obj.rotation_euler.copy(), obj.scale.copy())

    def reset(self):
        for obj in self.scene.objects:
            if obj.name in self.base:
                obj.location, obj.rotation_euler, obj.scale = self.base[obj.name]

    def move(self, obj, pos=None, rotation=None, scale=None):
        if isinstance(obj, str):
            obj = self.objects[obj]
        if pos is not None:
            obj.location = pos
        if rotation is not None:
            obj.rotation_euler = rotation
        if scale is not None:
            obj.scale = (scale,)*3 if isinstance(scale,(int,float)) else scale
        self.dynamic.add(obj)
        return obj

    def pose(self, key, x, y=0, z=0, lean=0, turn=0, squash=1, arms=(0,0), legs=(0,0)):
        ctl = self.controls[key]
        self.move(ctl['root'], (x,y,z), (0,lean,turn), (1/math.sqrt(squash), 1/math.sqrt(squash), squash))
        self.move(ctl['armL'], rotation=(0,arms[0],0))
        self.move(ctl['armR'], rotation=(0,arms[1],0))
        self.move(ctl['legL'], rotation=(0,legs[0],0))
        self.move(ctl['legR'], rotation=(0,legs[1],0))
        self.move(self.shadows[key], (x,y,.287), scale=(.72/(1+max(0,z)*.45),.42/(1+max(0,z)*.45),.004))

    def blink(self, key, value):
        for obj in self.characters[key].objects:
            if any(s in obj.name for s in ('BrightEye','ShyEye','OpenEye','EyeGlint')):
                scale = self.base[obj.name][2].copy()
                scale.z *= max(.08,value)
                self.move(obj, scale=scale)

    def keyframe(self, frame):
        for obj in self.dynamic:
            for channel in ('location','rotation_euler','scale'):
                obj.keyframe_insert(channel, frame=frame, group='Baked performance')


def smooth(a,b,t):
    u = max(0,min(1,(t-a)/(b-a)))
    return u*u*(3-2*u)


def pulse(t, center, width=.35):
    return math.exp(-((t-center)/width)**2)


def lerp(a,b,u):
    return a+(b-a)*u
