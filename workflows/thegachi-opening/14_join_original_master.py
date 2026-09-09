"""5초 신규 도입부 + 기존 6초 MP4 스트림 복사 연결 및 원본 구간 검증.

원본의 144프레임을 잘라내거나 재타이밍/재인코딩하지 않는다. 최종 11초/264프레임.
"""
from pathlib import Path
import argparse
import subprocess
import hashlib
import json
import shutil
from PIL import Image,ImageDraw,ImageFont

parser=argparse.ArgumentParser()
parser.add_argument('--version',choices=['v005','v006'],default='v005')
args=parser.parse_args()
version=args.version
root=Path(__file__).resolve().parents[2]
out=root/'outputs/thegachi-opening'/version
frames=out/'frames'
legacy=root/'outputs/thegachi-opening/v002/thegachi-opening-v002.mp4'
expected='88f565048f0e29ae0ab3d4246d29f93a0d8c78ab47260cf657e421c3d105b41a'
assert hashlib.sha256(legacy.read_bytes()).hexdigest()==expected
render=json.loads((out/'render-result.json').read_text(encoding='utf-8'))
assert render['frames']==120
assert [p.name for p in sorted(frames.glob('*.png'))]==[f'{i:04d}.png' for i in range(1,121)]
for p in frames.glob('*.png'):
    with Image.open(p) as im:
        assert im.size==(1920,1080)
        im.verify()

# Use the original opening's first frame at the seam for identical backgrounds at the cut.
# Keep the Blender-rendered last frame as a separate artifact before making the join sequence.
seam=out/'seam'
seam.mkdir(exist_ok=True)
shutil.copy2(frames/'0120.png',seam/'intro-rendered-last.png')
sequence=out/'join-frames'
sequence.mkdir(exist_ok=True)
assert not list(sequence.glob('*.png'))
for f in range(1,120):
    shutil.copy2(frames/f'{f:04d}.png',sequence/f'{f:04d}.png')
shutil.copy2(root/'outputs/thegachi-opening/v002/frames/0001.png',sequence/'0120.png')
ffmpeg,ffprobe=shutil.which('ffmpeg'),shutil.which('ffprobe')
assert ffmpeg and ffprobe
intro=out/f'intro-walk-wave-extract-{version}.mp4'
final=out/f'thegachi-opening-{version}.mp4'
subprocess.run([ffmpeg,'-n','-v','error','-framerate','24','-start_number','1','-i',str(sequence/'%04d.png'),
                '-frames:v','120','-c:v','libx264','-preset','slow','-crf','17','-pix_fmt','yuv420p',
                '-movflags','+faststart','-an',str(intro)],check=True)
listing=out/'concat.txt'
# Project-relative entries keep the concatenation recipe portable.
listing.write_text(f"file 'intro-walk-wave-extract-{version}.mp4'\nfile '../v002/thegachi-opening-v002.mp4'\n",encoding='utf-8')
subprocess.run([ffmpeg,'-n','-v','error','-f','concat','-safe','0','-i',str(listing),
                '-map','0:v:0','-c','copy','-movflags','+faststart',str(final)],check=True)
probe=json.loads(subprocess.check_output([ffprobe,'-v','error','-count_frames','-show_streams','-show_format','-of','json',str(final)],text=True))
stream=next(s for s in probe['streams'] if s['codec_type']=='video')
assert stream['codec_name']=='h264'
assert (stream['width'],stream['height'])==(1920,1080)
assert stream['avg_frame_rate']=='24/1'
assert int(stream['nb_read_frames'])==264
assert abs(float(probe['format']['duration'])-11.)<.002
subprocess.run([ffmpeg,'-v','error','-xerror','-i',str(final),'-f','null','-'],check=True)


def decoded_hashes(path,trim=None):
    cmd=[ffmpeg,'-v','error','-i',str(path)]
    if trim:
        cmd+=['-vf',trim]
    cmd+=['-pix_fmt','yuv420p','-f','framemd5','-']
    result=subprocess.check_output(cmd,text=True)
    return [line.rsplit(',',1)[1].strip() for line in result.splitlines() if line and not line.startswith('#')]


original_hashes=decoded_hashes(legacy)
joined_tail_hashes=decoded_hashes(final,'trim=start_frame=120,setpts=PTS-STARTPTS')
assert len(original_hashes)==len(joined_tail_hashes)==144
assert original_hashes==joined_tail_hashes, 'The appended original video must be pixel-identical.'
assert hashlib.sha256(legacy.read_bytes()).hexdigest()==expected
for name,seconds in [('walking',1.),('overhead-wave',3.),('extraction',4.),('joined-original',5.5),('final',10.)]:
    subprocess.run([ffmpeg,'-n','-v','error','-ss',str(seconds),'-i',str(final),'-frames:v','1',str(out/f'decoded-{name}.png')],check=True)
shutil.copy2(frames/'0072.png',out/'wave.png')
shutil.copy2(frames/'0108.png',out/'extracted-logo.png')
shutil.copy2(root/'outputs/thegachi-opening/v002/final-logo.png',out/'final-logo.png')
sheet=Image.new('RGB',(1440,660),'#09111d')
draw=ImageDraw.Draw(sheet)
font=ImageFont.load_default(size=18)
panels=[(frames/'0025.png','1.00s / WALK'),(frames/'0072.png','2.96s / WAVE'),
        (frames/'0096.png','3.96s / EXTRACT'),(frames/'0108.png','4.46s / SYMBOL'),
        (root/'outputs/thegachi-opening/v002/frames/0034.png','6.38s / ORIGINAL'),
        (root/'outputs/thegachi-opening/v002/frames/0120.png','9.96s / ORIGINAL')]
for i,(p,label) in enumerate(panels):
    x,y=(i%3)*480,(i//3)*330
    with Image.open(p) as im:
        sheet.paste(im.resize((480,270),Image.Resampling.LANCZOS),(x,y))
    draw.text((x+18,y+286),label,font=font,fill='#c5d3e1')
sheet.save(out/'storyboard.png')
report={'ok':True,'video':final.name,'intro_seconds':5,'legacy_seconds':6,'total_seconds':11,
        'frames':264,'fps':24,'width':1920,'height':1080,'codec':'H.264','audio':'none',
        'join_method':'FFmpeg concat demuxer, -c copy; no re-encoding of original master.',
        'original_file_sha256':expected,'original_144_decoded_frames_identical':True,
        'full_decode':'passed','bytes':final.stat().st_size,
        'sha256':hashlib.sha256(final.read_bytes()).hexdigest(),'ffprobe':probe}
(out/'video-verification.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
print(json.dumps({k:v for k,v in report.items() if k!='ffprobe'},indent=2))
