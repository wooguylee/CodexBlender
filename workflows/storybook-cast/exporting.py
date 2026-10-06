"""Separate native rigs and bake a single FBX take with eight documented clip ranges."""
import bpy,sys,json,hashlib,runpy,time
from mathutils import Matrix
from catalog import THEMES,clip_ranges,SWIMMERS
from motions import create_actions,mesh_bounds

def export_theme(root,theme):
    out=root/'outputs/storybook-cast/v001';delivery=root/'exports/storybook-cast/v001'
    source=json.loads((out/'model-manifest.json').read_text(encoding='utf-8'))
    report_path=out/'export-manifest.json'
    report=json.loads(report_path.read_text(encoding='utf-8')) if report_path.exists() else {'characters':[],'preserved_sources':source['preserved_sources'],'clips':clip_ranges()}
    completed={r['key'] for r in report['characters']};started=time.monotonic()
    triangulate=runpy.run_path(str(root/'workflows/weather-unity/triangulate.py'))['triangulate_ngons']
    for record in source['characters']:
        if record['theme']!=theme or record['key'] in completed:continue
        key=record['key'];scene=bpy.data.scenes[record['scene']];bpy.context.window.scene=scene
        rig=bpy.data.objects[record['rig']];mesh=bpy.data.objects[record['mesh']]
        if bpy.context.object and bpy.context.object.mode!='OBJECT':bpy.ops.object.mode_set(mode='OBJECT')
        floor=min(v.co.z for v in mesh.data.vertices)
        if not rig.get('ground_aligned'):
            shift=Matrix.Translation((0,0,-floor));mesh.data.transform(shift,shape_keys=True);rig.data.transform(shift)
            rig.data.update_tag();rig.update_tag(refresh={'OBJECT','DATA','TIME'});rig['ground_aligned']=True;rig['pivot_shift']=-floor
        triangulate(mesh.data);scene.frame_set(1);bpy.context.view_layer.update()
        all_motion,actions,motion_report=create_actions(scene,rig,mesh,key)
        for driver in mesh.data.shape_keys.animation_data.drivers:assert driver.driver.is_valid and driver.driver.is_simple_expression
        for v in mesh.data.vertices:assert abs(sum(g.weight for g in v.groups)-1)<1e-5
        native=delivery/theme/'blender'/(key+'.blend');fbx=delivery/'unity/Assets/StorybookCast/Themes'/theme/'Models'/(key+'.fbx')
        native.parent.mkdir(parents=True,exist_ok=True);fbx.parent.mkdir(parents=True,exist_ok=True)
        assert not native.exists() and not fbx.exists(),key+' was already saved without a checkpoint; inspect before recovery.'
        rig.animation_data.action=actions['Idle'];rig.animation_data.action_slot=actions['Idle'].slots[0];scene.frame_start=1;scene.frame_end=49;scene.frame_set(1)
        bpy.context.view_layer.update();bpy.ops.object.select_all(action='DESELECT');rig.select_set(True);bpy.context.view_layer.objects.active=rig
        scene['native_actions']=json.dumps({name:action.name for name,action in actions.items()});scene['front']='-Y in Blender, -Z in Unity';scene['fps']=24
        bpy.data.libraries.write(str(native),{scene,all_motion,*actions.values()},path_remap='RELATIVE',fake_user=True,compress=True)
        rig.animation_data.action=all_motion;rig.animation_data.action_slot=all_motion.slots[0];scene.frame_end=motion_report['frames'];scene.frame_set(1)
        rig.data.update_tag();rig.update_tag(refresh={'OBJECT','DATA','TIME'});bpy.context.view_layer.update()
        mesh.select_set(True)
        with bpy.context.temp_override(scene=scene,view_layer=scene.view_layers[0]):
            result=bpy.ops.export_scene.fbx(filepath=str(fbx),use_selection=True,object_types={'ARMATURE','MESH'},
              apply_unit_scale=True,apply_scale_options='FBX_SCALE_ALL',axis_forward='-Z',axis_up='Y',global_scale=1.,
              use_mesh_modifiers=False,mesh_smooth_type='FACE',use_triangles=False,add_leaf_bones=False,
              use_armature_deform_only=False,bake_space_transform=False,bake_anim=True,bake_anim_use_all_bones=True,
              bake_anim_use_nla_strips=False,bake_anim_use_all_actions=False,bake_anim_force_startend_keying=True,
              bake_anim_step=1.,bake_anim_simplify_factor=0.,use_custom_props=False,path_mode='AUTO')
        assert result=={'FINISHED'}
        rig.animation_data.action=actions['Idle'];rig.animation_data.action_slot=actions['Idle'].slots[0];scene.frame_end=49;scene.frame_set(1);bpy.context.view_layer.update()
        lo,hi=mesh_bounds(mesh)
        data={**record,'native':native.relative_to(root).as_posix(),'fbx':fbx.relative_to(root).as_posix(),
          'native_sha256':hashlib.sha256(native.read_bytes()).hexdigest(),'fbx_sha256':hashlib.sha256(fbx.read_bytes()).hexdigest(),
          'fbx_bytes':fbx.stat().st_size,'native_bytes':native.stat().st_size,'shapes':3,'native_actions':len(actions)+1,
          'pivot_shift_z':rig['pivot_shift'],'rest_bounds':{'min':lo.tolist(),'max':hi.tolist()},'motion_style':'swimming' if key in SWIMMERS else 'walking',
          'motion':motion_report}
        report['characters'].append(data);report['ok']=len(report['characters'])==20
        report_path.write_text(json.dumps(report,indent=2,ensure_ascii=False),encoding='utf-8')
        print(json.dumps({'exported':key,'seconds':time.monotonic()-started,'native_bytes':native.stat().st_size,'fbx_bytes':fbx.stat().st_size}),flush=True)
    catalog={'themes':[{'key':k,'ko':v['ko'],'color':v['color']} for k,v in THEMES.items()],
       'characters':[{k:c[k] for k in ('key','ko','role','theme','bones','vertices','shapes','materials','motion_style')} for c in report['characters']], 'clips':clip_ranges()}
    catalog_path=delivery/'unity/Assets/StorybookCast/catalog.json';catalog_path.parent.mkdir(parents=True,exist_ok=True)
    catalog_path.write_text(json.dumps(catalog,indent=2,ensure_ascii=False),encoding='utf-8')
    scene=bpy.data.scenes['SC_'+theme+'_v001'];bpy.context.window.scene=scene;scene.frame_set(1);scene.render.filepath=str(out/(theme+'-rigged.png'));bpy.ops.render.render(write_still=True)
    print(json.dumps({'ok':True,'theme':theme,'total_exported':len(report['characters'])}),flush=True)
