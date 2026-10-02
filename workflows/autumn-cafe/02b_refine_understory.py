"""둥근 임시 관목을 잎 메시로 교체하고 배경을 새 파일에 다시 굽는다."""
import bpy, math, random, json, time
from mathutils import Vector,Euler
scene=bpy.context.scene;assert scene.name=='Autumn_Cafe_v001'
park=bpy.data.collections['AC_Park'];rng=random.Random(2802)
shrubs=[o for o in park.objects if o.name.startswith('AC_Far woodland understory')]
centers=[tuple(o.location) for o in shrubs]
for o in shrubs:bpy.data.objects.remove(o,do_unlink=True)
vs=[];fs=[];ids=[]
for cx,cy,cz in centers:
    for j in range(850):
        a=rng.random()*math.tau;z=rng.uniform(-1,1);r=rng.random()**(1/3);xy=math.sqrt(1-z*z)
        p=Vector((cx+math.cos(a)*xy*r*2.8,cy+math.sin(a)*xy*r*2.0,.72+z*r*.78))
        q=Euler((rng.uniform(-1.1,1.1),rng.uniform(-1.1,1.1),rng.random()*math.tau)).to_matrix();size=rng.uniform(.10,.25)
        k=len(vs)
        for v in [(0,-size,0),(-size*.63,0,.015),(0,size,0),(size*.63,0,.015)]:vs.append(tuple(p+q@Vector(v)))
        fs.append((k,k+1,k+2,k+3));ids.append(rng.choice([0,0,1,2]))
me=bpy.data.meshes.new('Natural understory foliage');me.from_pydata(vs,[],fs)
for n in ['AC_Deep green leaves','AC_Leaf Ochre','AC_Leaf Lime gold']:me.materials.append(bpy.data.materials[n])
for p,i in zip(me.polygons,ids):p.material_index=i
o=bpy.data.objects.new('AC_Natural woodland understory',me);park.objects.link(o)
ng=scene.compositing_node_group;scene.compositing_node_group=None
beauty=scene.view_layers['StaticAfternoon'];fx=scene.view_layers['MovingLeavesAndTraffic'];beauty.use=True;fx.use=False
bpy.context.window.view_layer=beauty
scene.render.film_transparent=False;scene.cycles.samples=160
scene.render.image_settings.file_format='OPEN_EXR';scene.render.image_settings.color_mode='RGBA';scene.render.image_settings.color_depth='16'
plate=PROJECT_ROOT/'assets/autumn-cafe/v001/afternoon-background-final.exr';assert not plate.exists()
scene.render.filepath=str(plate);scene.frame_set(1);t=time.monotonic();bpy.ops.render.render(write_still=True)
im=bpy.data.images.load(str(plate));im.pack();im.filepath='//../assets/autumn-cafe/v001/afternoon-background-final.exr'
next(n for n in ng.nodes if n.type=='IMAGE').image=im
scene.compositing_node_group=ng;beauty.use=False;fx.use=True;bpy.context.window.view_layer=fx
scene.render.film_transparent=True;scene.cycles.samples=32
scene.render.image_settings.file_format='PNG';scene.render.image_settings.color_mode='RGB';scene.render.image_settings.color_depth='8'
scene.render.filepath='//../outputs/autumn-cafe/v001/frames/'
scene['background_plate']='assets/autumn-cafe/v001/afternoon-background-final.exr'
print('Natural understory baked',time.monotonic()-t)
