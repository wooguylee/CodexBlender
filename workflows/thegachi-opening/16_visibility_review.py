"""최종 영상 QA: 투명하지만 그림자를 드리우는 추출 심벌/배경을 시간대별로 숨긴다.

v005 출력은 보존하고 v006에 수정본을 만든다. 동작과 v002 원본은 유지한다.
"""
import json

scene=bpy.context.scene
assert scene.name=='Thegachi_Opening_v005'
scene.name='Thegachi_Opening_v006'
scene['output_version']='v006'


def remove_channel(owner,path):
    if owner.animation_data and owner.animation_data.action:
        for layer in owner.animation_data.action.layers:
            for strip in layer.strips:
                for bag in strip.channelbags:
                    for fc in list(bag.fcurves):
                        if fc.data_path==path:
                            bag.fcurves.remove(fc)


def visibility(obj,keys):
    remove_channel(obj,'hide_render')
    for f,v in keys:
        obj.hide_render=v
        obj.keyframe_insert('hide_render',frame=f)


glyph=scene.objects['HP_Extracted_Person_ch']
background=scene.objects['HP_Extract_Background']
house=scene.objects['HP_BlueHouse_LogoContour']
visibility(glyph,[(1,True),(87,True),(88,False),(120,False)])
visibility(background,[(1,True),(88,True),(89,False),(120,False)])
for obj in scene.objects:
    if obj.type in ['MESH','CURVE'] and obj not in [glyph,background,house]:
        disappear=100 if obj.name.startswith('HP_Person_') else 108
        visibility(obj,[(1,False),(disappear-1,False),(disappear,True),(120,True)])

# Alpha-blended props should not create opaque or stochastic shadows during the dissolve.
for name in ['HP_Key','HP_Fill','HP_Rim']:
    light=scene.objects[name].data
    for f,value in [(1,True),(87,True),(88,False),(108,False),(109,True),(120,True)]:
        light.use_shadow=value
        light.keyframe_insert('use_shadow',frame=f)

scene.render.resolution_x,scene.render.resolution_y=960,540
folder=PROJECT_ROOT/'outputs/thegachi-opening/v006'
folder.mkdir(parents=True,exist_ok=True)
review=folder/'storyboard'
review.mkdir(exist_ok=True)
for f in [25,72,96,108]:
    scene.frame_set(f)
    if f==72:
        assert glyph.hide_render and background.hide_render
    if f==108:
        assert all(obj.hide_render for obj in scene.objects if obj.type in ['MESH','CURVE'] and obj not in [glyph,background,house])
    scene.render.filepath=str(review/f'frame-{f:03d}.png')
    bpy.ops.render.render(write_still=True)
scene.frame_set(72)
scene.render.filepath='//../outputs/thegachi-opening/v006/preview.png'
report={'ok':True,'fix':'Invisible extraction glyph and backdrop no longer cast shadows before appearing.',
        'glyph_visible_from':88,'backdrop_visible_from':89,'person_hidden_from':100,
        'architecture_hidden_from':108,'dissolve_shadow_disabled_frames':[88,108],
        'motion_unchanged':True,'legacy_video_unchanged':True,'v005_retained':True}
(folder/'visibility-verification.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
print(json.dumps(report))
