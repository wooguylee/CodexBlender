"""Arrange actual Blender/Unity renders for shoulder comparison and visual QA."""
from pathlib import Path
from PIL import Image,ImageDraw
import importlib.util
ROOT=Path(__file__).resolve().parents[2];OUT=ROOT/'outputs/storybook-cast/v002';DEST=ROOT/'exports/storybook-cast/v002/previews'
spec=importlib.util.spec_from_file_location('pack',Path(__file__).with_name('04_package.py'));pack=importlib.util.module_from_spec(spec);spec.loader.exec_module(pack)
sheet=Image.new('RGB',(840,1320),'#eef0f5');draw=ImageDraw.Draw(sheet)
draw.text((28,20),'어깨 연결 보완 · 실제 모델 렌더 비교',font=pack.font(27),fill='#25354b')
draw.text((155,65),'이전 v001',font=pack.font(23),fill='#9f5360');draw.text((570,65),'수정 v002',font=pack.font(23),fill='#277c70')
for row,(key,label) in enumerate([('PipiRabbit','삐삐 토끼'),('TutuTurtle','투투 거북이'),('HaniSeahorse','하니 해마')]):
    for col,version in enumerate(('v001','v002')):
        img=Image.open(ROOT/'outputs/storybook-cast'/version/'native'/(key+'.png')).convert('RGBA').resize((384,384),Image.Resampling.LANCZOS)
        sheet.paste(img,(col*420+18,row*400+108),img)
    draw.text((30,row*400+110),label,font=pack.font(20),fill='#25354b')
sheet.save(DEST/'shoulders-before-after.png')
for theme in ('Forest','Dessert','Space','Sea'):
    proof=Image.new('RGB',(1600,1450),'#eef0f5');d=ImageDraw.Draw(proof)
    for row,(frame,name) in enumerate([(0,'Idle'),(62,'Walk'),(121,'Run'),(199,'SitIdle'),(294,'Wave'),(344,'Celebrate')]):
        for col,yaw in enumerate((45,90)):
            img=Image.open(OUT/'angles'/(theme+'-'+str(yaw))/(f'{frame:04}.png')).crop((60,290,1860,760)).resize((800,209),Image.Resampling.LANCZOS)
            proof.paste(img,(col*800,row*240+30));d.text((col*800+12,row*240+5),f'{theme} / {name} / {yaw} deg',font=pack.font(19),fill='#25354b')
    proof.save(OUT/(theme+'-angle-review.png'))
