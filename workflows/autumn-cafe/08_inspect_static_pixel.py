"""확장한 아래쪽 실내 ROI에서 발생한 단일 변화 픽셀의 실제 좌표/프레임을 진단."""
from pathlib import Path
from PIL import Image
import numpy as np,json
root=Path(__file__).resolve().parents[2];out=root/'outputs/autumn-cafe/v001';folder=out/'frames'
base=np.array(Image.open(folder/'0001.png').convert('RGB'))[905:]
findings=[]
for i in range(2,481):
    current=np.array(Image.open(folder/f'{i:04d}.png').convert('RGB'))[905:]
    yy,xx=np.nonzero(np.any(current!=base,axis=2))
    for y,x in zip(yy,xx):findings.append({'frame':i,'x':int(x),'y':int(y+905),'first_rgb':base[y,x].tolist(),'frame_rgb':current[y,x].tolist()})
(out/'isolated-pixel-inspection.json').write_text(json.dumps(findings,indent=2),encoding='utf-8')
print(json.dumps(findings,indent=2))
