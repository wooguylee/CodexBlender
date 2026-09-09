"""Full HD 프레임으로 H.264 MP4 생성 및 전체 디코딩/프레임/길이 검증.

로컬 Python/Pillow와 설치된 FFmpeg 사용. 외부 업로드/음원/다운로드 없음.
"""
import argparse
import hashlib
import json
from pathlib import Path
import shutil
import subprocess
from PIL import Image, ImageDraw, ImageFont

parser = argparse.ArgumentParser()
parser.add_argument('--version', choices=['v001','v002','v003','v007'], default='v001')
args = parser.parse_args()
root = Path(__file__).resolve().parents[2]
out = root/'outputs/thegachi-opening'/args.version
frames = out/'frames'
files = sorted(frames.glob('*.png'))
render = json.loads((out/'render-result.json').read_text(encoding='utf-8'))
total = render['frames']
duration = total/24
assert len(files) == total
assert [p.name for p in files] == [f'{i:04d}.png' for i in range(1,total+1)]
for path in files:
    with Image.open(path) as im:
        assert im.size == (1920,1080), path.name
        im.verify()
ffmpeg, ffprobe = shutil.which('ffmpeg'), shutil.which('ffprobe')
assert ffmpeg and ffprobe
video = out/f'thegachi-opening-{args.version}.mp4'
subprocess.run([ffmpeg,'-n','-hide_banner','-loglevel','error','-framerate','24','-start_number','1',
                '-i',str(frames/'%04d.png'),'-frames:v',str(total),'-c:v','libx264','-preset','slow',
                '-crf','17','-pix_fmt','yuv420p','-movflags','+faststart','-an',str(video)],check=True)
probe = json.loads(subprocess.check_output([ffprobe,'-v','error','-count_frames','-show_streams',
                                           '-show_format','-of','json',str(video)],text=True,encoding='utf-8'))
stream = next(s for s in probe['streams'] if s['codec_type']=='video')
assert stream['codec_name']=='h264'
assert (stream['width'],stream['height'])==(1920,1080)
assert stream['avg_frame_rate']=='24/1'
assert int(stream['nb_read_frames']) == total
assert abs(float(probe['format']['duration'])-duration) < .001
subprocess.run([ffmpeg,'-v','error','-xerror','-i',str(video),'-f','null','-'],check=True)
shutil.copy2(frames/f"{render.get('poster_frame',120):04d}.png",out/'final-logo.png')
shutil.copy2(frames/f"{render.get('symbol_frame',34):04d}.png",out/'symbol-3d.png')

# Review sheet is assembled from actual rendered frames, with no generative edits.
sheet = Image.new('RGB',(1440,660),'#09111d')
draw = ImageDraw.Draw(sheet)
font = ImageFont.load_default(size=18)
for index, frame in enumerate(render.get('review_frames',[14,34,60,82,104,120])):
    x,y = (index%3)*480,(index//3)*330
    with Image.open(frames/f'{frame:04d}.png') as im:
        sheet.paste(im.resize((480,270),Image.Resampling.LANCZOS),(x,y))
    draw.text((x+18,y+286),f'{(frame-1)/24:.2f}s  /  FRAME {frame:03d}',font=font,fill='#b9c7d9')
sheet.save(out/'storyboard.png')

# Decode frames from the finished MP4 for visual comparison, independent of the source PNGs.
subprocess.run([ffmpeg,'-n','-v','error','-ss','0.541667','-i',str(video),'-frames:v','1',
                str(out/'decoded-opening.png')],check=True)
subprocess.run([ffmpeg,'-n','-v','error','-ss',str((render.get('symbol_frame',34)-1)/24),'-i',str(video),'-frames:v','1',
                str(out/'decoded-symbol.png')],check=True)
subprocess.run([ffmpeg,'-n','-v','error','-ss',str((render.get('poster_frame',120)-1)/24),'-i',str(video),'-frames:v','1',
                str(out/'decoded-final.png')],check=True)
if args.version=='v003':
    subprocess.run([ffmpeg,'-n','-v','error','-ss',str(17/24),'-i',str(video),'-frames:v','1',
                    str(out/'decoded-consonants.png')],check=True)
    shutil.copy2(frames/'0001.png',out/'intro-house-person.png')
    shutil.copy2(frames/'0018.png',out/'intro-consonants.png')
if args.version=='v007':
    for name, frame in [('wave',72),('expansion',144)]:
        subprocess.run([ffmpeg,'-n','-v','error','-ss',str((frame-1)/24),'-i',str(video),'-frames:v','1',
                        str(out/f'decoded-{name}.png')],check=True)
    assert total == 192
    assert json.loads((out/'continuity-verification.json').read_text(encoding='utf-8'))['separate_video_join'] is False
report = {'ok':True,'video':video.name,'width':1920,'height':1080,'fps':24,'frames':total,
          'duration_seconds':duration,'codec':'H.264','pixel_format':stream['pix_fmt'],
          'audio':'none','all_png_files_verified':True,'full_video_decode':'passed',
          'bytes':video.stat().st_size,'sha256':hashlib.sha256(video.read_bytes()).hexdigest(),
          'ffprobe':probe}
(out/'video-verification.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps({k:v for k,v in report.items() if k!='ffprobe'},ensure_ascii=False,indent=2))
