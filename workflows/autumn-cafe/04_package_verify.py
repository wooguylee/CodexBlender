"""480장 무결성, 첫/끝 일치, 정적 국소 ROI, MP4 전체 디코딩 확인 후 납품."""
from pathlib import Path
import json, subprocess, shutil, hashlib
import numpy as np
from PIL import Image, ImageDraw

root=Path(__file__).resolve().parents[2];out=root/'outputs/autumn-cafe/v001';folder=out/'frames'
files=[folder/f'{f:04d}.png' for f in range(1,481)]
def read(p):
    with Image.open(p) as im:
        im.load();assert im.size==(1920,1080);return np.array(im.convert('RGB'))
first=read(files[0]);last=read(files[-1]);assert np.array_equal(first,last)
endpoint=read(out/'endpoint-render-check.png')
ed=np.abs(first.astype(np.int16)-endpoint.astype(np.int16))
assert ed.mean()<.15, {'endpoint_mean':float(ed.mean()),'endpoint_max':int(ed.max())}
# Fully interior areas are not touched by exterior vehicles/leaves.
# Coordinates are set after visual inspection of the final composition.
roi_path=Path(__file__).with_name('static-rois.json');rois=json.loads(roi_path.read_text())
stats={k:{'max_channel_delta':0,'changed_pixels':0,'observations':0} for k in rois}
steps=[];previous=first
for f,p in enumerate(files,1):
    with Image.open(p) as im:im.verify()
    a=read(p)
    if f>1:steps.append(float(np.abs(a.astype(np.int16)-previous.astype(np.int16)).mean()))
    for k,(x1,y1,x2,y2) in rois.items():
        d=np.abs(a[y1:y2,x1:x2].astype(np.int16)-first[y1:y2,x1:x2].astype(np.int16))
        stats[k]['max_channel_delta']=max(stats[k]['max_channel_delta'],int(d.max()))
        stats[k]['changed_pixels']+=int(np.any(d!=0,axis=2).sum());stats[k]['observations']+=int(d.shape[0]*d.shape[1])
    previous=a
assert all(s['max_channel_delta']==0 for s in stats.values()),stats
ffmpeg=shutil.which('ffmpeg');ffprobe=shutil.which('ffprobe');assert ffmpeg and ffprobe
def run(args):subprocess.run(args,check=True)
video=out/'autumn-cafe-20s-loop.mp4';assert not video.exists()
# High quality fixed QP keeps lossy reconstruction changes below the strict
# static-region threshold. The endpoint is forced to an I-frame and tested.
run([ffmpeg,'-n','-v','error','-framerate','24','-start_number','1','-i',str(folder/'%04d.png'),
     '-frames:v','480','-c:v','libx264','-preset','slow','-qp','6','-pix_fmt','yuv420p','-g','240','-bf','0',
     '-force_key_frames','expr:eq(n,479)','-movflags','+faststart','-an','-metadata','title=Autumn cafe - a slow afternoon, 20 second loop',str(video)])
probe=json.loads(subprocess.check_output([ffprobe,'-v','error','-count_frames','-show_streams','-show_format','-of','json',str(video)],text=True))
s=next(x for x in probe['streams'] if x['codec_type']=='video')
assert (s['width'],s['height'],s['avg_frame_rate'],int(s['nb_read_frames']))==(1920,1080,'24/1',480)
assert float(probe['format']['duration'])==20
run([ffmpeg,'-v','error','-xerror','-i',str(video),'-f','null','-'])
raw=subprocess.check_output([ffmpeg,'-v','error','-i',str(video),'-vf',r'select=eq(n\,0)+eq(n\,479)','-fps_mode','passthrough','-pix_fmt','rgb24','-f','rawvideo','-'])
arr=np.frombuffer(raw,dtype=np.uint8).reshape(2,1080,1920,3)
identical=bool(np.array_equal(arr[0],arr[1]));assert identical,'Encoded endpoints are not identical'
Image.fromarray(arr[0]).save(out/'poster.png')
encoded_stats={k:{'worst_frame_mean_delta':0.0,'max_channel_delta':0} for k in rois}
decoder=subprocess.Popen([ffmpeg,'-v','error','-i',str(video),'-pix_fmt','rgb24','-f','rawvideo','-'],stdout=subprocess.PIPE)
for f in range(480):
    data=decoder.stdout.read(1920*1080*3);assert len(data)==1920*1080*3
    a=np.frombuffer(data,dtype=np.uint8).reshape(1080,1920,3)
    for k,(x1,y1,x2,y2) in rois.items():
        d=np.abs(a[y1:y2,x1:x2].astype(np.int16)-arr[0,y1:y2,x1:x2].astype(np.int16))
        encoded_stats[k]['worst_frame_mean_delta']=max(encoded_stats[k]['worst_frame_mean_delta'],float(d.mean()))
        encoded_stats[k]['max_channel_delta']=max(encoded_stats[k]['max_channel_delta'],int(d.max()))
assert decoder.wait()==0
assert all(s['worst_frame_mean_delta']<.5 for s in encoded_stats.values()),encoded_stats
sheet=Image.new('RGB',(1440,850),'#251f16');draw=ImageDraw.Draw(sheet)
for i,f in enumerate([1,81,161,241,321,401]):
    a=Image.open(files[f-1]);x=i%3*480;y=i//3*425
    sheet.paste(a.resize((480,270),Image.Resampling.LANCZOS),(x,y))
    sheet.paste(a.crop((260,300,1660,760)).resize((480,150),Image.Resampling.LANCZOS),(x,y+273))
    draw.text((x+10,y+10),f'{(f-1)/24:.2f} s',fill='white')
sheet.save(out/'motion-review.jpg',quality=94)
gif=out/'autumn-cafe-preview.gif'
run([ffmpeg,'-n','-v','error','-i',str(video),'-filter_complex','fps=10,scale=640:-1:flags=lanczos,split[a][b];[a]palettegen=stats_mode=full[p];[b][p]paletteuse=dither=bayer:bayer_scale=4','-loop','0',str(gif)])
report={'ok':True,'width':1920,'height':1080,'frames':480,'fps':24,'duration_seconds':20,'audio':False,'png_endpoints_identical':True,'mp4_decoded_endpoints_identical':identical,
        'independent_endpoint_render':{'mean_delta':float(ed.mean()),'max_delta':int(ed.max())},'static_regions':stats,'static_roi_coordinates':rois,
        'adjacent_step_mean':float(np.mean(steps)),'adjacent_step_max':max(steps),'video_bytes':video.stat().st_size,'video_sha256':hashlib.sha256(video.read_bytes()).hexdigest(),
        'all_frames_verified':True,'full_mp4_decode':True,'mp4_static_regions':encoded_stats,'encoding':'H264 fixed QP 6, yuv420p, forced endpoint I-frame'}
(out/'verification.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
(Path(__file__).parent/'verification-summary.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
Image.fromarray(arr[0]).resize((960,540),Image.Resampling.LANCZOS).save(Path(__file__).parent/'preview.jpg',quality=92)
html='''<!doctype html><html lang="ko"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>가을, 느린 오후</title><style>body{margin:0;background:#211e18;color:#eee5d6;font:16px system-ui}main{max-width:1500px;margin:4vh auto;padding:0 24px}h1{font-weight:400}video{width:100%;border-radius:8px}p{color:#b9ae97}a{color:#e3c687}</style>
<main><h1>가을, 느린 오후</h1><video src="autumn-cafe-20s-loop.mp4" controls autoplay muted loop playsinline poster="poster.png"></video><p>카페 통창 너머의 가을 공원 · 맑은 오후 3시 · 20초 무한반복 · 1920 × 1080 · 무음</p><a href="autumn-cafe-20s-loop.mp4" download>영상 저장</a></main></html>'''
(out/'play-loop.html').write_text(html,encoding='utf-8')
print(json.dumps(report,indent=2))
