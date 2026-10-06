"""변형한 rest data의 갱신을 명시하고, 전용 Scene override 안에서 FBX 애니메이션을 내보낸다."""
import hashlib,json,shutil
out=PROJECT_ROOT/'outputs/weather-unity/v001';manifest=json.loads((out/'export-manifest.json').read_text(encoding='utf-8'))
backup=out/'fbx-before-refresh';backup.mkdir(exist_ok=True);previous=bpy.context.scene
for record in manifest['characters']:
    scene=bpy.data.scenes['WFUnity_'+record['name']];bpy.context.window.scene=scene
    rig=next(o for o in scene.objects if o.type=='ARMATURE');rig.data.update_tag();rig.update_tag(refresh={'OBJECT','DATA','TIME'})
    scene.frame_set(1);bpy.context.view_layer.update();bpy.ops.object.select_all(action='DESELECT')
    for obj in scene.objects:obj.select_set(True)
    bpy.context.view_layer.objects.active=rig
    path=PROJECT_ROOT/record['fbx'];saved=backup/path.name
    if not saved.exists():shutil.copy2(path,saved)
    with bpy.context.temp_override(scene=scene,view_layer=scene.view_layers[0]):
        assert bpy.context.scene==scene
        bpy.ops.export_scene.fbx(filepath=str(path),use_selection=True,object_types={'ARMATURE','MESH'},global_scale=1.,
            apply_unit_scale=True,apply_scale_options='FBX_SCALE_ALL',axis_forward='-Z',axis_up='Y',use_mesh_modifiers=False,
            mesh_smooth_type='FACE',use_triangles=False,add_leaf_bones=False,use_armature_deform_only=False,bake_space_transform=False,
            bake_anim=True,bake_anim_use_all_bones=True,bake_anim_use_nla_strips=False,bake_anim_use_all_actions=False,
            bake_anim_force_startend_keying=True,bake_anim_step=1.,bake_anim_simplify_factor=0.,use_custom_props=False)
    record['fbx_sha256']=hashlib.sha256(path.read_bytes()).hexdigest();record['fbx_bytes']=path.stat().st_size
bpy.context.window.scene=previous
manifest['refresh_note']='Explicit armature data/object/time tagging and matching Scene/view-layer override. Exporter triangulation disabled to retain live driver-driven shape values. Export meshes have n-gons triangulated in place with identical vertices, shape coordinates and drivers; Unity triangulates remaining quads.'
(out/'export-manifest.json').write_text(json.dumps(manifest,indent=2,ensure_ascii=False),encoding='utf-8')
print(json.dumps({'ok':True,'refined':5}))
