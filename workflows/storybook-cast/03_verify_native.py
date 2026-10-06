"""20개 개별 .blend를 독립 재개방해 검증·정규화하고 미리보기를 렌더한다.

실행은 제작 완료 후 별도 Blender의 --background --factory-startup 환경에서
수행한다. 모델 파일을 저장한 뒤에만 임시 카메라/조명을 추가하며, 검증에
실패한 캐릭터는 성공으로 처리하거나 수정한 상태로 저장하지 않는다.
"""

import datetime
import hashlib
import json
import math
from pathlib import Path
import struct
import sys
import traceback

import bpy
from mathutils import Vector
import numpy as np


ROOT = Path(__file__).resolve().parents[2]
WORKFLOW = Path(__file__).resolve().parent
if str(WORKFLOW) not in sys.path:
    sys.path.insert(0, str(WORKFLOW))
from catalog import CLIPS, THEMES, SWIMMERS, clip_ranges


OUTPUT = ROOT / "outputs/storybook-cast/v001"
MANIFEST_PATH = OUTPUT / "export-manifest.json"
REPORT_PATH = OUTPUT / "native-verification.json"
FLOOR_TOLERANCE = .002
LOOP_TOLERANCE = .001
MOTION_THRESHOLD = .025
SEATED_DROP = .05


def require(condition, message):
    if not condition:
        raise AssertionError(message)


def write_json(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2), encoding="utf-8")


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def update_scene(scene, rig, mesh):
    rig.data.update_tag()
    rig.update_tag(refresh={"OBJECT", "DATA", "TIME"})
    if mesh.data.shape_keys:
        mesh.data.shape_keys.update_tag()
    mesh.update_tag(refresh={"OBJECT", "DATA", "TIME"})
    bpy.context.view_layer.update()


def vertices_world(mesh):
    depsgraph = bpy.context.evaluated_depsgraph_get()
    evaluated = mesh.evaluated_get(depsgraph)
    data = evaluated.to_mesh(preserve_all_data_layers=False, depsgraph=depsgraph)
    try:
        require(data is not None and len(data.vertices) > 0,
                "Evaluated mesh has no vertices")
        xyz = np.empty(len(data.vertices) * 3, dtype=np.float32)
        data.vertices.foreach_get("co", xyz)
        xyz = xyz.reshape((-1, 3)).astype(np.float64)
        transform = np.asarray(evaluated.matrix_world, dtype=np.float64)
        xyz = xyz @ transform[:3, :3].T + transform[:3, 3]
        require(bool(np.isfinite(xyz).all()), "Evaluated vertices contain NaN/Inf")
        return xyz
    finally:
        evaluated.to_mesh_clear()


def use_action(scene, rig, action, frame=1):
    require(len(action.slots) > 0, action.name + ": no Blender action slot")
    rig.animation_data_create()
    rig.animation_data.action = action
    rig.animation_data.action_slot = action.slots[0]
    require(rig.animation_data.action_slot == action.slots[0],
            action.name + ": action slot assignment failed")
    scene.frame_set(frame)
    bpy.context.view_layer.update()


def action_description(action):
    require(len(action.slots) == 1, action.name + ": expected one armature slot")
    channels = []
    for layer in action.layers:
        for strip in layer.strips:
            if not hasattr(strip, "channelbag"):
                continue
            bag = strip.channelbag(action.slots[0])
            if bag is not None:
                channels.extend(bag.fcurves)
    require(bool(channels), action.name + ": slot has no keyframe channels")
    frames = []
    key_count = 0
    for curve in channels:
        for point in curve.keyframe_points:
            frame, value = float(point.co.x), float(point.co.y)
            require(math.isfinite(frame) and math.isfinite(value),
                    action.name + ": non-finite keyframe")
            frames.append(frame)
            key_count += 1
    require(bool(frames), action.name + ": no keyframes")
    return {
        "action": action.name,
        "slots": len(action.slots),
        "slot_identifier": action.slots[0].identifier,
        "frame_range": [float(value) for value in action.frame_range],
        "keyframe_range": [min(frames), max(frames)],
        "channels": len(channels),
        "keyframes": key_count,
    }


def external_dependencies():
    """수동 경로 수정을 하지 않고 실제 외부 의존성이 없는지 검사한다."""
    external = ["library:" + library.filepath for library in bpy.data.libraries]
    for image in bpy.data.images:
        if image.source in {"FILE", "TILED", "SEQUENCE", "MOVIE"}:
            packed = bool(image.packed_file) or bool(getattr(image, "packed_files", []))
            if not packed:
                external.append("image:" + image.name + ":" + image.filepath)
    for sound in bpy.data.sounds:
        if sound.filepath and not sound.packed_file:
            external.append("sound:" + sound.name + ":" + sound.filepath)
    for font in bpy.data.fonts:
        if font.filepath and font.filepath != "<builtin>" and not font.packed_file:
            external.append("font:" + font.name + ":" + font.filepath)
    for data in list(bpy.data.movieclips) + list(bpy.data.cache_files):
        if data.filepath:
            external.append(data.bl_rna.identifier + ":" + data.filepath)
    for volume in bpy.data.volumes:
        if volume.filepath:
            external.append("volume:" + volume.filepath)
    for mesh in bpy.data.meshes:
        if mesh.library:
            external.append("linked-mesh:" + mesh.name)
    return external


def validate_weights(mesh, rig):
    groups = {group.index: group.name for group in mesh.vertex_groups}
    bone_names = set(rig.data.bones.keys())
    for name in groups.values():
        require(name in bone_names, "Vertex group references absent bone: " + name)
    sums, influences, used = [], [], set()
    for vertex in mesh.data.vertices:
        require(len(vertex.groups) > 0, "Unweighted vertex: " + str(vertex.index))
        total = 0.
        positive = 0
        for group in vertex.groups:
            require(group.group in groups, "Invalid vertex group index")
            weight = float(group.weight)
            require(math.isfinite(weight) and weight >= 0., "Invalid vertex weight")
            total += weight
            positive += int(weight > 0.)
            if weight > 0.:
                used.add(groups[group.group])
        require(abs(total - 1.) < 1e-5,
                "Non-normalized vertex %d: %.9f" % (vertex.index, total))
        sums.append(total)
        influences.append(positive)
    require(bool(sums), "Mesh has no skinned vertices")
    return {
        "vertices_checked": len(sums),
        "weight_sum_min": min(sums),
        "weight_sum_max": max(sums),
        "max_normalization_error": max(abs(value - 1.) for value in sums),
        "max_influences": max(influences),
        "weighted_bones": sorted(used),
    }


def check_drivers(mesh, rig):
    shapes = mesh.data.shape_keys
    require(shapes is not None, "Mesh has no shape keys")
    require(set(shapes.key_blocks.keys()) == {"Basis", "Blink", "Smile", "Surprise"},
            "Expected Basis and three facial shape keys")
    require(shapes.animation_data is not None, "Shape keys have no driver animation data")
    drivers = list(shapes.animation_data.drivers)
    require(len(drivers) == 3, "Expected exactly three face drivers")
    expected_paths = {'key_blocks["%s"].value' % name
                      for name in ("Blink", "Smile", "Surprise")}
    require({curve.data_path for curve in drivers} == expected_paths,
            "Face driver destinations differ from the three expected shape keys")
    result = []
    for curve in drivers:
        driver = curve.driver
        require(driver.is_valid and driver.is_simple_expression,
                "Invalid/non-simple facial driver: " + curve.data_path)
        require(not curve.mute, "Muted face driver: " + curve.data_path)
        for variable in driver.variables:
            require(variable.type == "SINGLE_PROP", "Unexpected face driver variable type")
            for target in variable.targets:
                require(target.id == rig, "Face driver references another object")
                require(target.data_path.startswith('pose.bones["CTRL_Face"]'),
                        "Face driver is not bound to CTRL_Face")
                rig.path_resolve(target.data_path)
        result.append({"path": curve.data_path, "expression": driver.expression,
                       "valid": bool(driver.is_valid),
                       "simple": bool(driver.is_simple_expression)})
    return result


def verify_awake_blink(scene, rig, mesh, idle):
    """스크립트 실행을 막고 재개방한 파일의 드라이버가 정점을 움직이는지 측정한다."""
    use_action(scene, rig, idle, 1)
    face = rig.pose.bones["CTRL_Face"]
    original = {name: float(face[name]) for name in ("blink", "smile", "surprise")}
    rig.animation_data.action = None  # 키프레임이 시험 입력값을 덮어쓰지 않게 한다.
    try:
        for name in original:
            face[name] = 0.
        update_scene(scene, rig, mesh)
        opened = vertices_world(mesh)
        face["blink"] = 1.
        update_scene(scene, rig, mesh)
        closed = vertices_world(mesh)
        require(opened.shape == closed.shape, "Blink changes vertex count")
        distances = np.linalg.norm(closed - opened, axis=1)
        delta = float(distances.max())
        changed = int(np.count_nonzero(distances > 1e-5))
        require(delta > 1e-4 and changed > 0,
                "Face driver is not awake: blink=1 did not deform vertices")
        return {"tested_after_open_with_scripts_disabled": True,
                "input_values": [0., 1.], "max_vertex_distance": delta,
                "changed_vertices": changed}
    finally:
        for name, value in original.items():
            face[name] = value
        use_action(scene, rig, idle, 1)
        update_scene(scene, rig, mesh)


def check_actions(scene, rig, mesh, key, result):
    expected = {key + "_" + name for name, _, _ in CLIPS}
    expected.add(key + "_AllMotions")
    actual = {action.name for action in bpy.data.actions}
    require(len(bpy.data.actions) == 9 and actual == expected,
            "Native actions do not match the expected nine: " + repr(sorted(actual)))
    result["frame_ranges"] = {}
    result["clips"] = {}
    result["loop_errors"] = {}
    result["actions"] = len(actual)
    all_motion = action_description(bpy.data.actions[key + "_AllMotions"])
    require(all_motion["keyframe_range"] == [1., float(clip_ranges()[-1]["last"])],
            "AllMotions frame range differs from catalog")
    result["frame_ranges"]["AllMotions"] = all_motion
    for name, length, loop in CLIPS:
        action = bpy.data.actions[key + "_" + name]
        description = action_description(action)
        require(description["keyframe_range"] == [1., float(length)],
                name + ": native action keyframe range differs from catalog")
        result["frame_ranges"][name] = description
        # 보행 주기의 절반에서 같은 자세가 반복되므로 1/4 지점도 검사한다.
        frames = sorted({1, 1 + (length - 1) // 2, length})
        if name in {"Walk", "Run"}:
            frames = sorted(set(frames) | {1 + (length - 1) // 4,
                                          1 + 3 * (length - 1) // 4})
        use_action(scene, rig, action, frames[0])
        snapshots = []
        measurements = []
        for frame in frames:
            scene.frame_set(frame)
            bpy.context.view_layer.update()
            xyz = vertices_world(mesh)
            require(len(xyz) == len(mesh.data.vertices),
                    name + ": evaluated vertex count differs from base mesh")
            snapshots.append(xyz)
            low, high = xyz.min(axis=0), xyz.max(axis=0)
            penetration = max(0., -float(low[2]))
            measurements.append({"frame": frame, "min": low.tolist(),
                                 "max": high.tolist(), "floor_penetration": penetration})
            if penetration >= FLOOR_TOLERANCE:
                result["errors"].append("%s frame %s: floor penetration %.6f >= %.6f" %
                                        (name, frame, penetration, FLOOR_TOLERANCE))
        max_distance = max(float(np.linalg.norm(xyz - snapshots[0], axis=1).max())
                           for xyz in snapshots)
        clip_report = {"loop": loop, "sample_frames": frames,
                       "samples": measurements, "max_vertex_distance": max_distance,
                       "max_height": max(sample["max"][2] for sample in measurements),
                       "max_floor_penetration": max(sample["floor_penetration"]
                                                    for sample in measurements)}
        if loop:
            error = float(np.abs(snapshots[-1] - snapshots[0]).max())
            result["loop_errors"][name] = error
            clip_report["loop_max_coordinate_difference"] = error
            if error >= LOOP_TOLERANCE:
                result["errors"].append("%s loop error %.6f >= %.6f" %
                                        (name, error, LOOP_TOLERANCE))
        if name in {"Walk", "Run"} and max_distance <= MOTION_THRESHOLD:
            result["errors"].append("%s mesh movement %.6f <= %.6f" %
                                    (name, max_distance, MOTION_THRESHOLD))
        result["clips"][name] = clip_report
    drop = result["clips"]["Idle"]["max_height"] - result["clips"]["SitIdle"]["max_height"]
    result["seated_height_drop"] = drop
    result["seated_height_drop_required"] = SEATED_DROP
    if drop < SEATED_DROP:
        result["errors"].append("SitIdle max-height drop %.6f < %.6f%s" %
                                (drop, SEATED_DROP,
                                 " (swimming character; not exempted)" if key in SWIMMERS else ""))
    result["max_floor_penetration"] = max(clip["max_floor_penetration"]
                                           for clip in result["clips"].values())
    return bpy.data.actions[key + "_Idle"]


def normalize_native(scene, rig, mesh, idle, path, key):
    use_action(scene, rig, idle, 1)
    scene.frame_start, scene.frame_end = 1, dict((name, length) for name, length, _ in CLIPS)["Idle"]
    scene.render.fps, scene.render.fps_base = 24, 1.
    if bpy.context.object and bpy.context.object.mode != "OBJECT":
        bpy.ops.object.mode_set(mode="OBJECT")
    bpy.ops.object.select_all(action="DESELECT")
    rig.select_set(True)
    bpy.context.view_layer.objects.active = rig
    for pose_bone in rig.pose.bones:
        if hasattr(pose_bone, "select"):
            pose_bone.select = False
        else:
            pose_bone.bone.select = False
    body = rig.pose.bones["CTRL_Body"]
    if hasattr(body, "select"):
        body.select = True
    else:
        body.bone.select = True
    rig.data.bones.active = rig.data.bones["CTRL_Body"]
    bpy.ops.object.mode_set(mode="POSE")
    require(rig.mode == "POSE" and rig.data.bones.active.name == "CTRL_Body",
            "Native opening state is not CTRL_Body in Pose Mode")
    xyz = vertices_world(mesh)
    low, high = xyz.min(axis=0), xyz.max(axis=0)
    center = Vector(((low + high) * .5))
    for screen in bpy.data.screens:
        for area in screen.areas:
            if area.type != "VIEW_3D":
                continue
            space = area.spaces.active
            region = space.region_3d
            if region is not None:
                region.view_location = center
                region.view_distance = max(5., float((high - low).max()) * 2.3)
                region.view_rotation = Vector((0, 1, -.15)).to_track_quat("-Z", "Y")
                region.view_perspective = "ORTHO"
            space.shading.type = "MATERIAL"
    scene.render.filepath = "//" + key + "-preview.png"
    require(not external_dependencies(), "External dependencies appeared before native save")
    saved = bpy.ops.wm.save_as_mainfile(filepath=str(path), compress=True, check_existing=False)
    require(saved == {"FINISHED"}, "Normalized native save failed")
    require(path.exists() and path.stat().st_size > 0, "Normalized native file is absent")
    return xyz


def render_preview(scene, rig, xyz, key):
    """여기에서 추가하는 카메라·조명·월드는 .blend에 저장하지 않는다."""
    if rig.mode != "OBJECT":
        bpy.ops.object.mode_set(mode="OBJECT")
    center = Vector((xyz.min(axis=0) + xyz.max(axis=0)) * .5)
    world = bpy.data.worlds.new("NativePreviewWorld")
    world.use_nodes = True
    world.node_tree.nodes["Background"].inputs["Color"].default_value = (.65, .68, .72, 1.)
    world.node_tree.nodes["Background"].inputs["Strength"].default_value = .55
    scene.world = world
    for name, location, energy, size in (
        ("NativeKey", (-3.5, -5, 6), 700, 5),
        ("NativeFill", (4, -2, 4), 420, 4),
        ("NativeRim", (0, 4, 5), 600, 4),
    ):
        data = bpy.data.lights.new(name, "AREA")
        data.energy, data.shape, data.size = energy, "DISK", size
        light = bpy.data.objects.new(name, data)
        scene.collection.objects.link(light)
        light.location = location
        light.rotation_euler = (center - light.location).to_track_quat("-Z", "Y").to_euler()
    data = bpy.data.cameras.new("NativePreviewCamera")
    camera = bpy.data.objects.new("NativePreviewCamera", data)
    scene.collection.objects.link(camera)
    camera.location = center + Vector((2.4, -10, 2.0))
    camera.rotation_euler = (center - camera.location).to_track_quat("-Z", "Y").to_euler()
    data.type = "ORTHO"
    rotation = np.asarray(camera.rotation_euler.to_matrix(), dtype=np.float64)
    projected = (xyz - np.asarray(center)) @ rotation[:, :2]
    data.ortho_scale = float(np.abs(projected).max()) * 2.30
    scene.camera = camera
    scene.render.engine = "BLENDER_EEVEE"
    if hasattr(scene, "eevee") and hasattr(scene.eevee, "taa_render_samples"):
        scene.eevee.taa_render_samples = 16
    scene.render.resolution_x = scene.render.resolution_y = 512
    scene.render.resolution_percentage = 100
    scene.render.film_transparent = True
    scene.render.image_settings.file_format = "PNG"
    scene.render.image_settings.color_mode = "RGBA"
    scene.render.image_settings.color_depth = "8"
    scene.render.use_file_extension = True
    path = OUTPUT / "native" / (key + ".png")
    path.parent.mkdir(parents=True, exist_ok=True)
    scene.render.filepath = str(path)
    rendered = bpy.ops.render.render(write_still=True)
    require(rendered == {"FINISHED"}, "Native preview render failed")
    require(path.exists() and path.stat().st_size > 100, "Native preview PNG is absent")
    with path.open("rb") as handle:
        header = handle.read(33)
    require(header[:8] == b"\x89PNG\r\n\x1a\n" and header[12:16] == b"IHDR",
            "Native preview does not contain a PNG header")
    require(struct.unpack(">II", header[16:24]) == (512, 512) and header[25] == 6,
            "Native preview is not a 512x512 RGBA PNG")
    return {"path": path.relative_to(ROOT).as_posix(), "bytes": path.stat().st_size,
            "sha256": digest(path), "resolution": [512, 512], "rgba": True,
            "saved_into_native": False}


def verify_character(record, manifest):
    key = record["key"]
    result = {"key": key, "theme": record["theme"], "ok": False, "errors": [],
              "motion_style": "swimming" if key in SWIMMERS else "walking",
              "normalized": False, "preview_rendered": False}
    try:
        path = (ROOT / record["native"]).resolve()
        require(path.is_relative_to(ROOT.resolve()), "Native path leaves the project")
        require(path.is_file(), "Native file is absent: " + str(path))
        result["native"] = path.relative_to(ROOT).as_posix()
        result["input_native_sha256"] = digest(path)
        opened = bpy.ops.wm.open_mainfile(filepath=str(path), use_scripts=False)
        require(opened == {"FINISHED"}, "Native file did not open")
        require(len(bpy.data.scenes) == 1, "Native file must contain exactly one Scene")
        scene = bpy.context.scene
        rigs = [obj for obj in bpy.data.objects if obj.type == "ARMATURE"]
        meshes = [obj for obj in bpy.data.objects if obj.type == "MESH"]
        require(len(rigs) == 1 and len(meshes) == 1,
                "Native file must contain exactly one Armature and one Mesh")
        rig, mesh = rigs[0], meshes[0]
        require(rig.name in scene.objects and mesh.name in scene.objects,
                "Native rig or mesh is not linked to its Scene")
        require(mesh.parent == rig, "Mesh parent is not the native rig")
        modifiers = [modifier for modifier in mesh.modifiers if modifier.type == "ARMATURE"]
        require(len(modifiers) == 1 and modifiers[0].object == rig,
                "Native armature modifier does not target the sole rig")
        require(not any(obj.type in {"CAMERA", "LIGHT"} for obj in scene.objects),
                "Native model contains an unexpected camera/light before preview")
        require("CTRL_Body" in rig.pose.bones and "CTRL_Face" in rig.pose.bones,
                "Required body/face controls are absent")
        require(len(rig.data.bones) == record["bones"], "Native bone count differs from export manifest")
        require(len(mesh.data.vertices) == record["vertices"],
                "Native vertex count differs from export manifest")
        result["counts"] = {"scenes": len(bpy.data.scenes), "scene_objects": len(scene.objects),
                            "armatures": len(rigs), "meshes": len(meshes),
                            "bones": len(rig.data.bones), "vertices": len(mesh.data.vertices),
                            "materials": len(mesh.data.materials)}
        result["external_dependencies"] = external_dependencies()
        require(not result["external_dependencies"],
                "Native has external dependencies: " + repr(result["external_dependencies"]))
        result["weights"] = validate_weights(mesh, rig)
        scene.frame_set(1)
        bpy.context.view_layer.update()
        result["drivers"] = check_drivers(mesh, rig)
        result["valid_simple_drivers"] = len(result["drivers"])
        idle = check_actions(scene, rig, mesh, key, result)
        result["awake_blink"] = verify_awake_blink(scene, rig, mesh, idle)
        require(not result["errors"], "Character failed animation measurements; see errors")
        xyz = normalize_native(scene, rig, mesh, idle, path, key)
        result["normalized"] = True
        record["native_sha256"] = result["native_sha256"] = digest(path)
        record["native_bytes"] = result["native_bytes"] = path.stat().st_size
        result["native_opening_state"] = {"action": idle.name, "frame": 1,
                                          "mode": "POSE", "selected_bone": "CTRL_Body"}
        # 파일 저장 성공 직후 해시를 기록한다. 렌더 실패가 저장 사실을 지우지 않는다.
        write_json(MANIFEST_PATH, manifest)
        result["preview"] = render_preview(scene, rig, xyz, key)
        result["preview_rendered"] = True
        result["ok"] = True
    except Exception as error:
        result["errors"].append(type(error).__name__ + ": " + str(error))
        result["traceback"] = traceback.format_exc()
    return result


def main():
    manifest = json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))
    expected = {row[0] for theme in THEMES.values() for row in theme["characters"]}
    records = manifest["characters"]
    require(len(records) == 20 and {record["key"] for record in records} == expected,
            "Run native verification only after all twenty exports are complete")
    only = set(sys.argv[sys.argv.index("--only") + 1].split(',')) if "--only" in sys.argv else None
    previous = json.loads(REPORT_PATH.read_text(encoding="utf-8")) if only else None
    if only:
        require(only <= expected, "Unknown --only character")
        for prior in previous["characters"]:
            if prior["key"] not in only:
                require(prior["ok"] and digest(ROOT / prior["native"]) == prior["native_sha256"], "Unchanged model no longer verified")
    report = {"ok": False, "state": "running", "expected_characters": 20,
              "blender_version": bpy.app.version_string,
              "started_utc": datetime.datetime.now(datetime.timezone.utc).isoformat(),
              "tolerances": {"floor_penetration_lt": FLOOR_TOLERANCE,
                             "loop_max_coordinate_difference_lt": LOOP_TOLERANCE,
                             "walk_run_max_vertex_distance_gt": MOTION_THRESHOLD,
                             "seated_height_drop_gte": SEATED_DROP},
              "characters": [c for c in previous["characters"] if c["key"] not in only] if only else []}
    write_json(REPORT_PATH, report)
    for record in records:
        if only and record["key"] not in only:
            continue
        result = verify_character(record, manifest)
        report["characters"].append(result)
        report["verified_characters"] = sum(item["ok"] for item in report["characters"])
        report["failed_characters"] = sum(not item["ok"] for item in report["characters"])
        write_json(REPORT_PATH, report)
        print(json.dumps({"native_verified": record["key"], "ok": result["ok"],
                          "errors": result["errors"],
                          "completed": len(report["characters"])}, ensure_ascii=False), flush=True)
    report["ok"] = report["verified_characters"] == 20
    report["state"] = "complete" if report["ok"] else "failed"
    report["completed_utc"] = datetime.datetime.now(datetime.timezone.utc).isoformat()
    write_json(REPORT_PATH, report)
    print(json.dumps({"ok": report["ok"], "verified": report["verified_characters"],
                      "failed": report["failed_characters"],
                      "report": REPORT_PATH.relative_to(ROOT).as_posix()}, ensure_ascii=False), flush=True)
    if not report["ok"]:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
