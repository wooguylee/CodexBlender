"""Diagnose neutral deformation and topology before producing any animation."""
import json,numpy as np
report=[];previous=bpy.context.scene
for key in ('PipiRabbit','PanBread','TwinkleStar'):
    scene=bpy.data.scenes['SC_'+key+'_v001'];bpy.context.window.scene=scene;scene.frame_set(1);bpy.context.view_layer.update()
    rig=bpy.data.objects[key+'_Rig'];mesh=bpy.data.objects[key+'_Skin'];ev=mesh.evaluated_get(bpy.context.evaluated_depsgraph_get())
    a=np.array([tuple(v.co) for v in mesh.data.vertices]);c=np.array([tuple(v.co) for v in ev.data.vertices]);diff=np.linalg.norm(a-c,axis=1)
    bones={p.name:{'head':list(p.head),'rest_head':list(p.bone.head_local),'matrix_delta':max(abs(x-y) for row,r2 in zip(p.matrix,p.bone.matrix_local) for x,y in zip(row,r2))} for p in rig.pose.bones if p.name in ['DEF_Thigh.L','DEF_Shin.L','DEF_Foot.L','DEF_UpperArm.L','DEF_Forearm.L','DEF_Head']}
    groups={g.index:g.name for g in mesh.vertex_groups};bad=[{'index':int(i),'rest':a[i].tolist(),'pose':c[i].tolist(),'weights':[(groups[g.group],g.weight) for g in mesh.data.vertices[i].groups]} for i in np.argsort(diff)[-4:]]
    report.append({'key':key,'rest_error_max':float(diff.max()),'bones':bones,'worst':bad})
bpy.context.window.scene=previous
(PROJECT_ROOT/'outputs/storybook-cast/v001/rest-probe.json').write_text(json.dumps(report,indent=2),encoding='utf-8');print(json.dumps(report))
