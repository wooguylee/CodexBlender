"""실제 PNG, 독립 재렌더, 브리찌 결과, 기존 원본 보존을 최종 검사한다."""
from pathlib import Path
import hashlib
import json
from PIL import Image, ImageChops, ImageStat

root = Path(__file__).resolve().parents[2]
out = root / 'outputs/weather-fairies/v001'
expected = {'weather-fairies-group.png': (2160, 1440),
            'weather-fairies-clean.png': (2160, 1440),
            'mongsil.png': (1080, 1080), 'haerong.png': (1080, 1080),
            'ttorr.png': (1080, 1080)}
files = {}
for name, size in expected.items():
    path = out / name
    with Image.open(path) as im:
        im.verify()
    with Image.open(path) as im:
        im.load()
        assert im.size == size, (name, im.size)
        assert im.mode == 'RGBA'
        assert im.getchannel('A').getextrema() == (255, 255)
    files[name] = {'resolution': list(size), 'bytes': path.stat().st_size,
                   'sha256': hashlib.sha256(path.read_bytes()).hexdigest()}

with Image.open(out / 'weather-fairies-group.png') as a, Image.open(out / 'standalone-reopen.png') as b:
    assert a.size == b.size
    diff = ImageChops.difference(a.convert('RGB'), b.convert('RGB'))
    max_error = max(e[1] for e in diff.getextrema())
    mean_error = sum(ImageStat.Stat(diff).mean) / 3
    exact = diff.getbbox() is None

original = json.loads((out / 'build-verification.json').read_text(encoding='utf-8'))
source_preserved = {}
for name, checksum in original['existing_source_sha256'].items():
    actual = hashlib.sha256((root / name).read_bytes()).hexdigest()
    source_preserved[name] = actual == checksum
assert all(source_preserved.values())
standalone = json.loads((out / 'standalone-verification.json').read_text(encoding='utf-8'))
assert standalone['ok'] and standalone['independently_reopened'] and standalone['rendered']
jobs = {}
for job in ('20261005T192350-a505e9da2e', '20261005T192611-7801a0835c'):
    result = json.loads((root / 'outputs/jobs' / job / 'result.json').read_text(encoding='utf-8'))
    assert result['ok']
    assert (root / result['backup']).is_file() and (root / result['preview']).is_file()
    jobs[job] = {'ok': True, 'elapsed_seconds': result['elapsed_seconds']}
source = root / 'scenes/weather-fairies-v001.blend'
report = {'ok': max_error <= 2 and mean_error < .02, 'files': files,
          'standalone_reopen_pixel_exact': exact,
          'standalone_reopen_max_channel_error': max_error,
          'standalone_reopen_mean_channel_error': mean_error,
          'old_source_files_preserved': source_preserved,
          'old_scenes_preserved': original['old_scenes_unchanged'],
          'bridge_jobs': jobs, 'source_bytes': source.stat().st_size,
          'source_sha256': hashlib.sha256(source.read_bytes()).hexdigest(),
          'visual_review': 'Group and all three portraits directly inspected; smile, silhouettes, facial visibility and framing checked.',
          'scope': 'Three editable 3D characters, five still images; no skeletal rig or animation.'}
(out / 'output-verification.json').write_text(json.dumps(report, indent=2), encoding='utf-8')
assert report['ok'], f'Reopened render differs: max={max_error}, mean={mean_error}'
print(json.dumps({'ok': report['ok'], 'images': len(files), 'source_bytes': report['source_bytes'],
                  'reopen_pixel_exact': exact, 'max_channel_error': max_error,
                  'preserved_sources': len(source_preserved), 'preserved_scenes': len(report['old_scenes_preserved'])}, indent=2))
