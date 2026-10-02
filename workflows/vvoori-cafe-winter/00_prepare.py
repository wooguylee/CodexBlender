"""제작 전 원본 보존 해시와 이미지 생성용 도로 배치 가이드. 최종 정적 자산은 AI 두 장만 사용."""
from pathlib import Path
import hashlib, json
from PIL import Image, ImageDraw

root=Path(__file__).resolve().parents[2]
out=root/'outputs/vvoori-cafe-winter/v001'
paths=list((root/'scenes').glob('vvoori-cafe-v*.blend'))
paths+=list((root/'outputs/vvoori-cafe').glob('v*/*.mp4'))
manifest={p.relative_to(root).as_posix():hashlib.sha256(p.read_bytes()).hexdigest() for p in paths}
(out/'preservation-before.json').write_text(json.dumps(manifest,indent=2),encoding='utf-8')
im=Image.new('RGB',(1672,941),'#e4e7e3');d=ImageDraw.Draw(im)
d.rectangle((0,0,1672,310),fill='#b7cedf')
d.polygon([(0,546),(1672,386),(1672,405),(0,715)],fill='#778391')
d.line([(0,631),(1672,396)],fill='#dbc983',width=4)
d.line([(0,540),(1672,380)],fill='#c1bbc0',width=6)
d.line([(0,721),(1672,411)],fill='#c8bfc1',width=6)
d.text((45,250),'SNOWY PARK - trees, benches, lamps, mountains',fill='#53706b')
d.text((45,830),'NEAR SIDEWALK (will be hidden by cafe foreground)',fill='#847e73')
im.save(out/'road-composition-guide.png')
print(json.dumps({'protected_files':len(manifest),'guide':str(out/'road-composition-guide.png')}))
