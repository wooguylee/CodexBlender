"""사용자 요청: 현재 MP4 전체를 잘림 없이 90x30px GIF로 변환.

원본 전체 화면 비율을 유지하고 좌우 여백을 넣는다. 외부 업로드 없이 로컬 FFmpeg 사용.
"""
import hashlib
import json
from pathlib import Path
import shutil
import subprocess
from PIL import Image, ImageDraw

root = Path(__file__).resolve().parents[2]
out = root / 'outputs/thegachi-opening/v007'
source = out / 'thegachi-opening-v007.mp4'
dest = out / 'thegachi-opening-v007-90x30.gif'
assert not dest.exists(), 'Preserve existing output; select a new name for revisions.'
before = hashlib.sha256(source.read_bytes()).hexdigest()
ffmpeg = shutil.which('ffmpeg')
assert ffmpeg
filters = (
    'fps=20,scale=90:30:force_original_aspect_ratio=decrease:flags=lanczos,'
    'pad=90:30:(ow-iw)/2:(oh-ih)/2:color=0x070d19,setsar=1,split[a][b];'
    '[a]palettegen=max_colors=256:reserve_transparent=0:stats_mode=full[p];'
    '[b][p]paletteuse=dither=sierra2_4a'
)
subprocess.run([ffmpeg, '-n', '-v', 'error', '-i', str(source), '-filter_complex', filters,
                '-loop', '0', '-final_delay', '5', str(dest)], check=True)
subprocess.run([ffmpeg, '-v', 'error', '-xerror', '-i', str(dest), '-f', 'null', '-'], check=True)
with Image.open(dest) as gif:
    assert gif.size == (90, 30)
    assert gif.info.get('loop') == 0
    count = gif.n_frames
    duration = 0
    samples = []
    for i in range(count):
        gif.seek(i)
        gif.load()
        assert gif.size == (90, 30)
        duration += gif.info.get('duration', 0)
        if i in [20, 60, 80, 110, 145]:
            samples.append((i, gif.convert('RGB').copy()))
assert duration == 8000, duration
assert hashlib.sha256(source.read_bytes()).hexdigest() == before
# QA sheet shows five actual decoded GIF frames, enlarged only for inspection.
sheet = Image.new('RGB', (540, len(samples) * 200), '#070d19')
draw = ImageDraw.Draw(sheet)
for row, (i, sample) in enumerate(samples):
    sheet.paste(sample.resize((540, 180), Image.Resampling.NEAREST), (0, row * 200))
    draw.text((8, row * 200 + 182), f'{i / 20:.2f}s', fill='white')
sheet.save(out / 'gif-90x30-review.png')
report = {'ok': True, 'file': dest.name, 'size': [90, 30], 'duration_ms': duration,
          'frames': count, 'fps': 20, 'infinite_loop': True,
          'placement': 'Full source frame scaled to 53x30; centered with navy side padding; no crop.',
          'full_decode': 'passed', 'source_unchanged': True, 'bytes': dest.stat().st_size,
          'sha256': hashlib.sha256(dest.read_bytes()).hexdigest()}
(out / 'gif-90x30-verification.json').write_text(json.dumps(report, indent=2), encoding='utf-8')
print(json.dumps(report, indent=2))
