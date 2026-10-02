"""전체 검토 프레임의 정적 국소 영역/끝점/디코딩 확인, MP4와 실제 레이어 확인표 생성."""
from pathlib import Path
import hashlib
import json
import shutil
import subprocess

import numpy as np
from PIL import Image, ImageDraw

root = Path(__file__).resolve().parents[2]
version = globals().get('VERSION', 'v001')
assert version in {'v001', 'v002'}
prefix = '' if version == 'v001' else version + '-'
out = root/'outputs/vvoori-cafe'/version
assets = root/'assets/vvoori-cafe'/version
frames = out/'review-frames'
ffmpeg, ffprobe = shutil.which('ffmpeg'), shutil.which('ffprobe')
assert ffmpeg and ffprobe
files = [frames/f'{n:04d}.png' for n in range(1, 241)]

def read(path):
    with Image.open(path) as im:
        im.load()
        assert im.size == (960, 540), im.size
        return np.array(im.convert('RGB'))

first = read(files[0])
assert np.array_equal(first, read(files[-1]))
roi_path = root/'workflows/autumn-cafe/static-rois.json' if version == 'v001' else Path(__file__).with_name('v002-static-rois.json')
roi_source = json.loads(roi_path.read_text())
rois = {k: [int(v/2) for v in box] for k, box in roi_source.items()}
stats = {k: {'max_channel_delta': 0, 'changed_pixels': 0} for k in rois}
steps = []
previous = first
for path in files:
    with Image.open(path) as im:
        im.verify()
    a = read(path)
    steps.append(float(np.abs(a.astype(np.int16)-previous.astype(np.int16)).mean()))
    for key, (x1, y1, x2, y2) in rois.items():
        delta = np.abs(a[y1:y2, x1:x2].astype(np.int16)-first[y1:y2, x1:x2].astype(np.int16))
        stats[key]['max_channel_delta'] = max(stats[key]['max_channel_delta'], int(delta.max()))
        stats[key]['changed_pixels'] += int(np.any(delta != 0, axis=2).sum())
    previous = a
assert all(s['max_channel_delta'] == 0 for s in stats.values()), stats
assert max(steps) > .05, 'No visible animation detected.'
independent = np.abs(first.astype(np.int16)-read(out/'review-independent-endpoint.png').astype(np.int16))
assert independent.mean() < .1
park_name = 'park-background.png' if version == 'v001' else 'ai-autumn-park.png'
cafe_name = 'cafe-foreground.png' if version == 'v001' else 'ai-cafe-foreground.png'
foreground = np.array(Image.open(assets/cafe_name).convert('RGBA'))
alpha = foreground[:, :, 3]
opaque_threshold = 255 if version == 'v001' else 250
assert (alpha == 0).mean() > .3 and (alpha >= opaque_threshold).mean() > .2

video = out/'vvoori-cafe-review-20s.mp4'
assert not video.exists()
subprocess.run([ffmpeg, '-n', '-v', 'error', '-framerate', '12', '-i', str(frames/'%04d.png'),
                '-frames:v', '240', '-c:v', 'libx264', '-preset', 'medium', '-qp', '8', '-bf', '0',
                '-pix_fmt', 'yuv420p', '-force_key_frames', 'expr:eq(n,239)',
                '-movflags', '+faststart', '-an', str(video)], check=True)
probe = json.loads(subprocess.check_output([ffprobe, '-v', 'error', '-count_frames',
                    '-show_streams', '-show_format', '-of', 'json', str(video)], text=True))
stream = probe['streams'][0]
assert (stream['width'], stream['height'], stream['avg_frame_rate'], int(stream['nb_read_frames'])) == (960, 540, '12/1', 240)
assert float(probe['format']['duration']) == 20
subprocess.run([ffmpeg, '-v', 'error', '-xerror', '-i', str(video), '-f', 'null', '-'], check=True)
decoder = subprocess.Popen([ffmpeg, '-v', 'error', '-i', str(video), '-pix_fmt', 'rgb24', '-f', 'rawvideo', '-'], stdout=subprocess.PIPE)
encoded_stats = {k: 0.0 for k in rois}
encoded_first = None
for i in range(240):
    data = decoder.stdout.read(960*540*3)
    assert len(data) == 960*540*3
    a = np.frombuffer(data, dtype=np.uint8).reshape(540, 960, 3)
    if encoded_first is None:
        encoded_first = a.copy()
    for key, (x1, y1, x2, y2) in rois.items():
        delta = np.abs(a[y1:y2, x1:x2].astype(np.int16)-encoded_first[y1:y2, x1:x2].astype(np.int16))
        encoded_stats[key] = max(encoded_stats[key], float(delta.mean()))
assert decoder.wait() == 0
assert max(encoded_stats.values()) < .5
encoded_endpoint_identical = bool(np.array_equal(a, encoded_first))
assert encoded_endpoint_identical, 'Encoded review endpoints differ.'

# The contact sheet is made from the actual plates and rendered frames.
sheet = Image.new('RGB', (1280, 820), '#24201b')
draw = ImageDraw.Draw(sheet)
checker = Image.new('RGBA', (640, 360), (50, 50, 50, 255))
cd = ImageDraw.Draw(checker)
for y in range(0, 360, 20):
    for x in range(0, 640, 20):
        if (x//20+y//20) % 2:
            cd.rectangle((x, y, x+19, y+19), fill=(80, 80, 80, 255))
fg = Image.open(assets/cafe_name).convert('RGBA').resize((640, 360), Image.Resampling.LANCZOS)
checker.alpha_composite(fg)
sheet.paste(Image.open(assets/park_name).convert('RGB').resize((640, 360)), (0, 35))
sheet.paste(checker.convert('RGB'), (640, 35))
sheet.paste(Image.open(files[0]).resize((640, 360)), (0, 450))
sheet.paste(Image.open(files[120]).resize((640, 360)), (640, 450))
for x, y, label in [(15, 10, '01 | STATIC PARK / ROAD'), (655, 10, '03 | STATIC CAFE / WINDOW - RGBA'),
                    (15, 425, 'COMPOSITE | 0.00 s'), (655, 425, 'COMPOSITE | 10.00 s')]:
    draw.text((x, y), label, fill='#f0d7ad')
sheet.save(out/'layers-review.jpg', quality=94)
sheet.save(Path(__file__).with_name(prefix+'layers-review.jpg'), quality=90)
Image.open(out/'poster-fullhd.png').resize((960, 540)).save(Path(__file__).with_name(prefix+'preview.jpg'), quality=92)
html = '''<!doctype html><html lang="ko"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>vvoori-cafe · 이미지와 3D 합성</title><style>body{margin:0;background:#211e18;color:#eee5d6;font:16px system-ui}main{max-width:1280px;margin:3vh auto;padding:24px}video,img{width:100%;border-radius:8px}p{color:#c9baa1}a{color:#f3d49c}</style>
<main><h1>vvoori-cafe</h1><p>공원 이미지 + 차량·낙엽 3D + 투명 카페 이미지</p>
<video src="vvoori-cafe-review-20s.mp4" controls autoplay loop muted playsinline poster="poster-fullhd.png"></video>
<p>검토본: 20초 · 960×540 · 12fps · 무음. Blender 원본: 1920×1080 · 24fps.</p>
<img src="layers-review.jpg" alt="실제 공원과 투명 카페 레이어, 합성 결과">
<p><a href="vvoori-cafe-review-20s.mp4" download>검토 영상 다운로드</a></p></main></html>'''
(out/'play-loop.html').write_text(html, encoding='utf-8')
report = {'ok': True, 'width': 960, 'height': 540, 'fps': 12, 'frames': 240, 'duration_seconds': 20,
          'full_quality_movie_rendered': False, 'source_png_endpoints_identical': True,
          'decoded_mp4_endpoints_identical': encoded_endpoint_identical,
          'independent_endpoint_mean': float(independent.mean()),
          'static_roi_all_frames': stats, 'encoded_static_roi_max_mean_delta': encoded_stats,
          'foreground_transparent_fraction': float((alpha == 0).mean()),
          'foreground_opaque_fraction': float((alpha >= opaque_threshold).mean()),
          'version': version, 'ai_generated_static_images': version == 'v002',
          'all_frames_verified': True, 'full_decode': True,
          'video_bytes': video.stat().st_size, 'video_sha256': hashlib.sha256(video.read_bytes()).hexdigest()}
(out/'verification.json').write_text(json.dumps(report, indent=2), encoding='utf-8')
Path(__file__).with_name(prefix+'verification-summary.json').write_text(json.dumps(report, indent=2), encoding='utf-8')
print(json.dumps(report, indent=2))
