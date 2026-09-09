"""사용자가 확인한 기존 더가치 자산을 프로젝트 내부에 보존한다. 다운로드 없음."""
import argparse
import hashlib
import json
from pathlib import Path
import re
import shutil

parser = argparse.ArgumentParser()
parser.add_argument('--wordmark', type=Path, required=True)
parser.add_argument('--icon', type=Path, required=True)
args = parser.parse_args()
root = Path(__file__).resolve().parents[2]
dest = root / 'assets/thegachi'
dest.mkdir(parents=True, exist_ok=True)
source = args.wordmark.read_text(encoding='utf-8-sig')
paths = re.findall(r'<path className="([^"]+)" d="([^"]+)"', source)
assert len(paths) == 6, 'Expected the six original wordmark paths.'
names = ['eo', 'a', 'i', 'person_ch', 'house_d', 'g']
data = [{'name': name, 'class': cls, 'd': d} for name, (cls, d) in zip(names, paths)]
(dest / 'wordmark-paths.json').write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding='utf-8')
svg = '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 368.59 106.02">\n'
svg += '<defs><linearGradient id="blue" x1="0" x2="87.66" gradientUnits="userSpaceOnUse"><stop stop-color="#036eb8"/><stop offset="1" stop-color="#171c61"/></linearGradient></defs>\n'
for cls, d in paths:
    color = {'cls-1': '#b5b5b6', 'cls-2': 'url(#blue)', 'cls-3': '#f9b341'}[cls]
    svg += f'<path fill="{color}" d="{d}"/>\n'
svg += '</svg>\n'
(dest / 'wordmark-original.svg').write_text(svg, encoding='utf-8')
shutil.copy2(args.icon, dest / 'symbol-original.png')
(dest / 'source.json').write_text(json.dumps({
    'wordmark_source': 'WorkTheGachi/Front/src/compo/ThegachiTypo.jsx',
    'icon_source': 'WorkTheGachi/Apply/static/WOORITS/img/logoThegachi.png',
    'wordmark_sha256': hashlib.sha256(args.wordmark.read_bytes()).hexdigest(),
    'icon_sha256': hashlib.sha256(args.icon.read_bytes()).hexdigest(),
    'authorization': 'User identified the existing company logo and requested its 3D opening.',
    'meaning': {'blue_house': '더의 ㄷ', 'yellow_person': '치의 ㅊ'},
    'vector_policy': 'Original filled paths retained; UI-only white 1px outlines omitted for solid 3D geometry.',
    'download': False,
}, ensure_ascii=False, indent=2), encoding='utf-8')
print(json.dumps({'ok': True, 'paths': len(paths), 'assets': str(dest)}, ensure_ascii=False))
