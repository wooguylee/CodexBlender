"""v002의 실제 PNG 무결성/독립 재렌더/기존 파일 보존을 검증한다."""
from pathlib import Path
import hashlib
import json
from PIL import Image, ImageChops, ImageStat

root = Path(__file__).resolve().parents[2]
out = root / 'outputs/weather-fairies/v002'
manifest = json.loads((out / 'render-manifest.json').read_text(encoding='utf-8'))
files = {}
for name, size in manifest['files'].items():
    path = out / name
    with Image.open(path) as im:
        im.verify()
    with Image.open(path) as im:
        im.load()
        assert list(im.size) == size
        assert im.mode == 'RGBA'
        assert im.getchannel('A').getextrema() == (255, 255)
    files[name] = {'resolution': size, 'bytes': path.stat().st_size,
                   'sha256': hashlib.sha256(path.read_bytes()).hexdigest()}
with Image.open(out / 'weather-fairies-five.png') as a, Image.open(out / 'standalone-reopen.png') as b:
    assert a.size == b.size
    difference = ImageChops.difference(a.convert('RGB'), b.convert('RGB'))
    max_error = max(e[1] for e in difference.getextrema())
    mean_error = sum(ImageStat.Stat(difference).mean) / 3
    exact = difference.getbbox() is None
build = json.loads((out / 'build-verification.json').read_text(encoding='utf-8'))
preserved = {}
for name, checksum in build['preserved_files_sha256'].items():
    preserved[name] = hashlib.sha256((root / name).read_bytes()).hexdigest() == checksum
assert all(preserved.values())
standalone = json.loads((out / 'standalone-verification.json').read_text(encoding='utf-8'))
assert standalone['ok'] and standalone['rendered'] and standalone['character_count'] == 5
jobs = {}
for request_path in (root / 'outputs/jobs').glob('*/request.json'):
    request = json.loads(request_path.read_text(encoding='utf-8-sig'))
    if request.get('label') not in {'눈송이 송송과 바람 솔솔 추가', '날씨 요정 5인조와 눈송이·바람 최종 이미지'}:
        continue
    result_path = request_path.parent / 'result.json'
    if not result_path.exists():
        continue
    result = json.loads(result_path.read_text(encoding='utf-8'))
    assert result['ok']
    assert (root / result['backup']).is_file() and (root / result['preview']).is_file()
    jobs[result['id']] = {'ok': True, 'elapsed_seconds': result['elapsed_seconds']}
assert len(jobs) == 2, jobs
source = root / manifest['source']
report = {'ok': max_error <= 2 and mean_error < .02, 'files': files,
          'reopen_pixel_exact': exact, 'max_channel_error': max_error, 'mean_channel_error': mean_error,
          'preserved_files': preserved, 'preserved_scenes': build['preserved_scenes'],
          'bridge_jobs': jobs, 'source_bytes': source.stat().st_size,
          'source_sha256': hashlib.sha256(source.read_bytes()).hexdigest(),
          'visual_review': 'Five-character group, snow-and-wind duo and both new portraits inspected.',
          'scope': 'Five editable 3D characters; two newly created. Still images; no skeletal rig or animation.'}
(out / 'output-verification.json').write_text(json.dumps(report, indent=2), encoding='utf-8')
assert report['ok'], (max_error, mean_error)
print(json.dumps({'ok': True, 'images': len(files), 'reopen_pixel_exact': exact,
                  'max_channel_error': max_error, 'preserved_files': len(preserved),
                  'preserved_scenes': len(build['preserved_scenes']), 'source_bytes': report['source_bytes']}, indent=2))
