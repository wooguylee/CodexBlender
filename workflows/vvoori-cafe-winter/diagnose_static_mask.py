"""불투명 ROI는 통과하지만 넓은 alpha 마스크에서 검출된 차이의 위치를 진단한다."""
from pathlib import Path
from PIL import Image,ImageFilter
import numpy as np,json
root=Path(__file__).resolve().parents[2];out=root/'outputs/vvoori-cafe-winter/v001'
native=np.array(Image.open(root/'assets/vvoori-cafe-winter/v001/ai-winter-cafe.png'))
mask=np.array(Image.fromarray(np.uint8(native[:,:,3]>=250)*255).resize((1920,1080),Image.Resampling.NEAREST).filter(ImageFilter.MinFilter(13)))==255
first=np.array(Image.open(out/'master-frames/0001.png')).astype(np.int16)
record=[]
for frame in [61,121,241,361,480]:
    a=np.array(Image.open(out/f'master-frames/{frame:04d}.png')).astype(np.int16)
    d=np.abs(a-first).max(axis=2);yy,xx=np.where((d>0)&mask)
    record.append({'frame':frame,'pixels':len(xx),'bbox':[int(xx.min()),int(yy.min()),int(xx.max()),int(yy.max())] if len(xx) else [],
        'samples':[[int(x),int(y),int(d[y,x]),first[y,x].tolist(),a[y,x].tolist()] for x,y in zip(xx[::max(1,len(xx)//20)],yy[::max(1,len(yy)//20)])]})
(out/'mask-diagnosis.json').write_text(json.dumps(record,indent=2),encoding='utf-8')
print(json.dumps(record,indent=2))
