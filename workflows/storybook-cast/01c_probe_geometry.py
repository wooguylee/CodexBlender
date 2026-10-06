import bmesh,json,math
from mathutils import Vector
samples={}
for kind in ('default','round'):
    bm=bmesh.new();bmesh.ops.create_cube(bm,size=1.)
    kw={'profile':.5} if kind=='round' else {}
    bmesh.ops.bevel(bm,geom=list(bm.edges),offset=.2,segments=3,affect='EDGES',**kw)
    samples[kind]=sorted([list(v.co) for v in bm.verts]);bm.free()
vectors=[Vector((0,-.16,-.48)),Vector((0,0,-.5)),Vector((0,.16,-.52))]
frames=[v.to_track_quat('Z','Y')@Vector((1,0,0)) for v in vectors]
report={'bevel_default_equals_round':samples['default']==samples['round'],'tube_ring_axes':[list(v) for v in frames],'adjacent_axis_dot':[frames[i].dot(frames[i+1]) for i in range(2)],'bevel_doc':bmesh.ops.bevel.__doc__}
(PROJECT_ROOT/'outputs/storybook-cast/v001/geometry-probe.json').write_text(json.dumps(report,indent=2),encoding='utf-8');print(json.dumps(report))
