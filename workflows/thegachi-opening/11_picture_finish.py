"""기준 그림 QA: 겹친 계단 블록의 공면을 단일 계단 메시로 정리한다."""
import json
import bmesh

scene=bpy.context.scene
assert scene.name=='Thegachi_HousePerson_v004'
collection=bpy.data.collections['Thegachi_HousePerson_v004']
for i in range(5):
    obj=scene.objects.get('HP_Entry_step_'+str(i))
    assert obj is not None
    bpy.data.objects.remove(obj,do_unlink=True)
base=-2.52
profile=[(base,2.4)]
for i in range(5):
    y=base+.22*(i+1)
    profile.append((y,2.4-.28*i))
    profile.append((y,2.4-.28*(i+1)))
profile += [(base+.22*5,.80),(base,.80)]
n=len(profile)
vertices=[(x,y,z) for x in [-1.31,-.07] for y,z in profile]
faces=[tuple(range(n-1,-1,-1)),tuple(range(n,2*n))]
faces += [(i,(i+1)%n,(i+1)%n+n,i+n) for i in range(n)]
mesh=bpy.data.meshes.new('HP_EntryStairSolid')
mesh.from_pydata(vertices,[],faces)
bm=bmesh.new()
bm.from_mesh(mesh)
bmesh.ops.recalc_face_normals(bm,faces=bm.faces)
bm.to_mesh(mesh)
bm.free()
obj=bpy.data.objects.new('HP_EntryStairSolid',mesh)
collection.objects.link(obj)
mesh.materials.append(bpy.data.materials['HP_Warm_plaster'])
bevel=obj.modifiers.new('Soft_stone_edges','BEVEL')
bevel.width=.028
bevel.segments=3
obj.modifiers.new('Normals','WEIGHTED_NORMAL')
scene.render.filepath='//../outputs/thegachi-opening/v004/house-person-picture-final.png'
dest=PROJECT_ROOT/'scenes/thegachi-house-person-v004-final.blend'
assert not dest.exists()
bpy.ops.wm.save_as_mainfile(filepath=str(dest),copy=True,relative_remap=True,compress=True)
report={'ok':True,'scene':scene.name,'source':'scenes/thegachi-house-person-v004-final.blend',
        'stage':'reference_picture_only','stairs':'single closed mesh; overlapping blocks removed'}
(OUTPUT_DIR/'picture-final.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
print(json.dumps(report))
