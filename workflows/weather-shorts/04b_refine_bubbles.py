"""사건별 미리보기에서 옅게 보인 거품 테두리만 보강. 나머지 장면과 애니메이션 보존."""
import json, shutil, sys
sys.path.insert(0,str(PROJECT_ROOT/'workflows/weather-shorts'))
from production import rgb

scene=bpy.data.scenes['Weather_Short_05_v001']
out=PROJECT_ROOT/'outputs/weather-shorts/v001/05-bubble-hats'
backup=out/'source-before-bubble-review.blend'
source=PROJECT_ROOT/'scenes/weather-short-05-v001.blend'
assert not backup.exists()
shutil.copy2(source,backup)

def emission(name,color):
    mat=bpy.data.materials.new('WS5_'+name);mat.use_nodes=True
    mat.diffuse_color=(*rgb(color),1)
    nodes=mat.node_tree.nodes;nodes.clear()
    shader=nodes.new('ShaderNodeEmission');shader.inputs['Color'].default_value=(*rgb(color),1)
    output=nodes.new('ShaderNodeOutputMaterial');mat.node_tree.links.new(shader.outputs[0],output.inputs['Surface'])
    return mat

mats=[emission('bubble_blue','409CBF'),emission('bubble_pink','D391C1'),bpy.data.materials['WS5_white']]
old_radius=[1,.982,1.014];new_radius=[1,.973,1.023];thickness=[.030,.017,.011]
changed=[]
for obj in scene.objects:
    if obj.type!='CURVE' or not any(name in obj.name for name in ('BigBubble_Rim','BubbleHat')) or '_Rim' not in obj.name:continue
    i=int(obj.name.rsplit('_Rim',1)[1]);obj.data.bevel_depth=thickness[i]
    obj.data.materials.clear();obj.data.materials.append(mats[i])
    for spline in obj.data.splines:
        for point in spline.bezier_points:point.co*=new_radius[i]/old_radius[i]
    changed.append(obj.name)
assert len(changed)==18
scene.frame_set(1)
bpy.data.libraries.write(str(source),{scene},path_remap='RELATIVE',fake_user=True,compress=True)
native=out/'native-source.json'
native.replace(out/'native-source-before-bubble-review.json')
(out/'bubble-review.json').write_text(json.dumps({'ok':True,'changed':changed,'reason':'Improve bubble rim visibility in wide framing.'},indent=2),encoding='utf-8')
bpy.context.window.scene=scene
scene.frame_set(577)
print(json.dumps({'ok':True,'bubble_rims_refined':len(changed)}))
