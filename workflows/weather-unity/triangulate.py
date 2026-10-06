"""Triangulate export-only n-gons in place, preserving every shape-key coordinate and driver."""
import bmesh

def triangulate_ngons(mesh):
    faces_before = sum(len(p.vertices) > 4 for p in mesh.polygons)
    if not faces_before:
        return 0
    coords = [tuple(v.co) for v in mesh.vertices]
    keys = mesh.shape_keys
    shapes = {k.name: [tuple(v.co) for v in k.data] for k in keys.key_blocks} if keys else {}
    drivers = len(keys.animation_data.drivers) if keys and keys.animation_data else 0
    bm = bmesh.new()
    try:
        bm.from_mesh(mesh)
        bmesh.ops.triangulate(bm, faces=[f for f in bm.faces if len(f.verts) > 4], ngon_method='BEAUTY')
        bm.to_mesh(mesh)
    finally:
        bm.free()
    mesh.update()
    assert [tuple(v.co) for v in mesh.vertices] == coords, mesh.name
    assert ({k.name: [tuple(v.co) for v in k.data] for k in mesh.shape_keys.key_blocks} if mesh.shape_keys else {}) == shapes, mesh.name
    assert (len(mesh.shape_keys.animation_data.drivers) if mesh.shape_keys and mesh.shape_keys.animation_data else 0) == drivers
    assert not any(len(p.vertices) > 4 for p in mesh.polygons)
    return faces_before
