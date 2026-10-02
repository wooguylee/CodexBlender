import bpy
scene=bpy.data.scenes['Vvoori_Cafe_v003']
for o in scene.objects:
    if o.animation_data and o.animation_data.drivers and 'Traffic' in o.name:
        print(o.name,tuple(o.location),tuple(o.rotation_euler),[(f.data_path,f.array_index,f.driver.expression) for f in o.animation_data.drivers])
for m in bpy.data.materials:
    if m.name.startswith('VC3') and 'shadow' in m.name.lower():print('SHADOW',m.name,[(n.type,n.name) for n in m.node_tree.nodes])
