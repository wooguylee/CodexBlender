"""Read-only diagnostic of the corrected puffer's sitting floor bounds."""
import sys,json
from pathlib import Path
import bpy
import numpy as np
ROOT=Path(__file__).resolve().parents[2];sys.path.insert(0,str(ROOT/'workflows/storybook-cast'))
from motions import set_pose
from rigging import world_delta
bpy.ops.wm.open_mainfile(filepath=str(ROOT/'exports/storybook-cast/v002/Sea/blender/BobaPuffer.blend'))
rig=next(o for o in bpy.context.scene.objects if o.type=='ARMATURE');mesh=next(o for o in bpy.context.scene.objects if o.type=='MESH')
rig.animation_data_clear()
rows=[]
for kind in ('Idle','SitIdle'):
    for hand_height in (-.29,-.10,0.,.10):
        set_pose(rig,'BobaPuffer',kind,.25)
        if kind=='SitIdle':
            for side,sign in (('L',-1),('R',1)):
                world_delta(rig.pose.bones['CTRL_Hand.'+side],(-sign*.18,-.28,hand_height))
        bpy.context.view_layer.update()
        data=mesh.evaluated_get(bpy.context.evaluated_depsgraph_get()).data
        coords=np.array([v.co[:] for v in data.vertices]);i=int(coords[:,2].argmin());j=int(coords[:,2].argmax())
        rows.append(dict(kind=kind,hand_height=hand_height,low=coords[i].tolist(),high=coords[j].tolist(),low_index=i,high_index=j,low_weights={mesh.vertex_groups[g.group].name:g.weight for g in mesh.data.vertices[i].groups},corrected_height=float(coords[j,2]+max(0,-coords[i,2]))))
print(json.dumps(rows,indent=2))
