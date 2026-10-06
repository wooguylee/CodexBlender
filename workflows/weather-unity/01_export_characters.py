"""브리찌로 승인된 다섯 리그를 개별 .blend와 Unity용 FBX로 분리한다."""
import hashlib,json,math,re,time,runpy
from mathutils import Matrix,Vector

root=PROJECT_ROOT;delivery=root/'exports/weather-fairies/v001';out=root/'outputs/weather-unity/v001'
native=delivery/'blender';models=delivery/'unity/Assets/WeatherFairies/Models'
for path in (out,native,models):path.mkdir(parents=True,exist_ok=True)
keys=['Mongsil','Haerong','Ttorr','Songsong','Solsol'];names=['몽실','해롱','또르','송송','솔솔']
neutral=root/'scenes/weather-rigs-v001.blend';demo=root/'scenes/weather-rig-demo-v001.blend'
preserved={str(p.relative_to(root)).replace('\\','/'):hashlib.sha256(p.read_bytes()).hexdigest() for p in [neutral,demo]}
original_scene=bpy.context.scene
if bpy.context.object and bpy.context.object.mode!='OBJECT':bpy.ops.object.mode_set(mode='OBJECT')
records=[];materials=[];started=time.monotonic()
triangulate_ngons=runpy.run_path(str(root/'workflows/weather-unity/triangulate.py'))['triangulate_ngons']

def load_character(path,key,tag):
    with bpy.data.libraries.load(str(path),link=False) as (available,loaded):
        wanted=[n for n in available.collections if n=='WR1_'+key or re.fullmatch('WR1_'+key+r'\.\d+',n)]
        assert len(wanted)==1,(key,wanted);loaded.collections=wanted
    collection=loaded.collections[0];collection.name=tag+'_'+key
    scene=bpy.data.scenes.new(tag+'_'+key);scene.collection.children.link(collection);bpy.context.window.scene=scene
    scene.unit_settings.system='METRIC';scene.unit_settings.scale_length=1.;scene.render.fps=24
    rigs=[o for o in collection.all_objects if o.type=='ARMATURE'];assert len(rigs)==1
    rig=rigs[0];rig.name=key+('_Rig' if tag=='WFNative' else '_ExportRig');rig.location=(0,0,0)
    meshes=sorted([o for o in collection.all_objects if o.type=='MESH'],key=lambda o:o.name)
    for i,obj in enumerate(meshes):obj.name=key+'_'+str(i).zfill(2)+'_'+obj.name.split(key+'_',1)[-1].split('.')[0]
    scene.frame_set(1);bpy.context.view_layer.update()
    floor=min(v.co.z for obj in meshes for v in obj.data.vertices)
    translation=Matrix.Translation((0,0,-floor));rig.data.transform(translation)
    for obj in meshes:obj.data.transform(translation,shape_keys=True)
    rig.data.update_tag();rig.update_tag(refresh={'OBJECT','DATA','TIME'})
    scene.frame_set(1);bpy.context.view_layer.update()
    return scene,rig,meshes,floor

def bounds(meshes):
    deps=bpy.context.evaluated_depsgraph_get();points=[]
    for obj in meshes:
        evaluated=obj.evaluated_get(deps)
        points.extend(obj.matrix_world@v.co for v in evaluated.data.vertices)
    return {'min':[min(v[i] for v in points) for i in range(3)],'max':[max(v[i] for v in points) for i in range(3)]}

for key,ko in zip(keys,names):
    destination=native/(key+'.blend');fbx=models/(key+'.fbx');assert not destination.exists() and not fbx.exists()
    scene,rig,meshes,floor=load_character(neutral,key,'WFNative')
    assert not rig.animation_data or not rig.animation_data.action
    bpy.ops.object.select_all(action='DESELECT');rig.select_set(True);bpy.context.view_layer.objects.active=rig
    scene['character_ko']=ko;scene['usage']='Native controls and drivers retained. Unity export is a separate FBX.'
    bpy.data.libraries.write(str(destination),{scene},path_remap='RELATIVE',fake_user=True,compress=True)
    native_counts={'objects':len(scene.objects),'bones':len(rig.data.bones),'meshes':len(meshes),'shape_keys':sum(len(o.data.shape_keys.key_blocks)-1 for o in meshes if o.data.shape_keys)}
    scene,rig,meshes,floor2=load_character(demo,key,'WFUnity')
    assert abs(floor-floor2)<1e-5
    scene.frame_start=1;scene.frame_end=384
    # FBX and Unity use linear skinning. Keep the editable native file's volume preservation.
    for obj in meshes:
        triangulate_ngons(obj.data)
        for mod in obj.modifiers:
            if mod.type=='ARMATURE':mod.use_deform_preserve_volume=False
    mats=sorted({m for o in meshes for m in o.data.materials},key=lambda m:m.name)
    for index,mat in enumerate(mats):
        mat.name='WFM_'+key+'_'+str(index).zfill(2)
        bsdf=next(n for n in mat.node_tree.nodes if n.type=='BSDF_PRINCIPLED')
        color=list(bsdf.inputs['Base Color'].default_value);mat.diffuse_color=color
        materials.append({'name':mat.name,'character':key,'linear_rgba':color,
                         'roughness':bsdf.inputs['Roughness'].default_value,'metallic':bsdf.inputs['Metallic'].default_value})
    poses=[]
    for frame in (1,76,136,180,244,320):
        scene.frame_set(frame);bpy.context.view_layer.update();poses.append({'frame':frame,'bounds':bounds(meshes)})
    scene.frame_set(1);bpy.context.view_layer.update();bpy.ops.object.select_all(action='DESELECT')
    for obj in [rig]+meshes:obj.select_set(True)
    bpy.context.view_layer.objects.active=rig
    with bpy.context.temp_override(scene=scene,view_layer=scene.view_layers[0]):
        result=bpy.ops.export_scene.fbx(filepath=str(fbx),use_selection=True,object_types={'ARMATURE','MESH'},
            global_scale=1.,apply_unit_scale=True,apply_scale_options='FBX_SCALE_ALL',axis_forward='-Z',axis_up='Y',
            use_mesh_modifiers=False,mesh_smooth_type='FACE',use_triangles=False,add_leaf_bones=False,
            use_armature_deform_only=False,bake_space_transform=False,bake_anim=True,bake_anim_use_all_bones=True,
            bake_anim_use_nla_strips=False,bake_anim_use_all_actions=False,bake_anim_force_startend_keying=True,
            bake_anim_step=1.,bake_anim_simplify_factor=0.,path_mode='AUTO',embed_textures=False,use_custom_props=False)
    assert result=={'FINISHED'} and fbx.stat().st_size>10000
    records.append({'name':key,'ko':ko,'blender':destination.relative_to(root).as_posix(),'fbx':fbx.relative_to(root).as_posix(),
      **native_counts,'pivot_shift_z':-floor,'sample_poses':poses,'fbx_bytes':fbx.stat().st_size,
      'fbx_sha256':hashlib.sha256(fbx.read_bytes()).hexdigest(),'blender_sha256':hashlib.sha256(destination.read_bytes()).hexdigest(),
      'fbx_frames':384,'fps':24,'unity_skinning':'linear','native_skinning':'preserve volume',
      'mesh_names':[o.name for o in meshes],'expected_materials':[m.name for m in mats]})
    print(json.dumps({'exported':key,'bones':native_counts['bones'],'shapes':native_counts['shape_keys'],'seconds':time.monotonic()-started}))
for path,digest in preserved.items():assert hashlib.sha256((root/path).read_bytes()).hexdigest()==digest
bpy.context.window.scene=original_scene
report={'ok':True,'characters':records,'materials':materials,'preserved_sources':preserved,'seconds':time.monotonic()-started,
        'export_settings':{'axis_forward':'-Z','axis_up':'Y','unit_meters':1,'leaf_bones':False,'apply_mesh_modifiers':False,'baked_frames':384}}
(out/'export-manifest.json').write_text(json.dumps(report,indent=2,ensure_ascii=False),encoding='utf-8')
(delivery/'unity/Assets/WeatherFairies/material-manifest.json').write_text(json.dumps({'materials':materials},indent=2),encoding='utf-8')
print(json.dumps({'ok':True,'characters':5,'seconds':report['seconds']}))
