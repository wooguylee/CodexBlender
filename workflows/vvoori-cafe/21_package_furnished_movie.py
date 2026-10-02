"""480개 Full HD 프레임의 정적 영역·루프·MP4 디코딩 검증과 결과 패키징."""
from pathlib import Path
import json, hashlib, shutil, subprocess
import numpy as np
from PIL import Image, ImageDraw
root=Path(__file__).resolve().parents[2];out=root/'outputs/vvoori-cafe/v004';assets=root/'assets/vvoori-cafe/v004'
frames=out/'master-frames';video=out/'vvoori-cafe-toon-20s.mp4'
rois={'ceiling':[1670,24,1840,65],'floor':[1390,925,1500,1000],'wall':[1250,820,1350,860],
      'near_post':[821,250,835,420],'middle_post':[1208,170,1220,320],'table':[520,810,620,830],
      'book':[610,772,650,790],'cup':[751,710,780,730],'chair_seat':[980,865,1110,896],
      'near_chair':[280,975,350,1000],'far_table':[1600,652,1680,672],'pendant':[1760,88,1800,135]}
def read(path):
    with Image.open(path) as im:
        im.load();assert im.size==(1920,1080);return np.array(im.convert('RGB'))
first=read(frames/'0001.png');previous=first;steps=[];stats={key:0 for key in rois}
for i in range(1,481):
    a=read(frames/f'{i:04d}.png')
    steps.append(float(np.abs(a.astype(np.int16)-previous.astype(np.int16)).mean()))
    for key,(x1,y1,x2,y2) in rois.items():stats[key]=max(stats[key],int(np.abs(a[y1:y2,x1:x2].astype(np.int16)-first[y1:y2,x1:x2].astype(np.int16)).max()))
    previous=a
assert np.array_equal(a,first)
assert max(stats.values())==0,stats
assert max(steps)>.05
independent=float(np.abs(first.astype(np.int16)-read(out/'independent-endpoint.png').astype(np.int16)).mean())
assert independent<.05
ffmpeg=shutil.which('ffmpeg');ffprobe=shutil.which('ffprobe');assert ffmpeg and ffprobe
assert not video.exists()
subprocess.run([ffmpeg,'-n','-v','error','-framerate','24','-i',str(frames/'%04d.png'),'-frames:v','480',
    '-c:v','libx264','-preset','medium','-qp','8','-bf','0','-pix_fmt','yuv420p','-force_key_frames','expr:eq(n,479)',
    '-movflags','+faststart','-an',str(video)],check=True)
probe=json.loads(subprocess.check_output([ffprobe,'-v','error','-count_frames','-show_streams','-show_format','-of','json',str(video)],text=True))
s=probe['streams'][0];assert (s['width'],s['height'],s['avg_frame_rate'],int(s['nb_read_frames']))==(1920,1080,'24/1',480)
assert float(probe['format']['duration'])==20
subprocess.run([ffmpeg,'-v','error','-xerror','-i',str(video),'-f','null','-'],check=True)
decoder=subprocess.Popen([ffmpeg,'-v','error','-i',str(video),'-pix_fmt','rgb24','-f','rawvideo','-'],stdout=subprocess.PIPE)
encoded_stats={key:0.0 for key in rois};encoded_first=None
for i in range(480):
    data=decoder.stdout.read(1920*1080*3);assert len(data)==1920*1080*3
    a=np.frombuffer(data,dtype=np.uint8).reshape(1080,1920,3)
    if encoded_first is None:encoded_first=a.copy()
    for key,(x1,y1,x2,y2) in rois.items():
        encoded_stats[key]=max(encoded_stats[key],float(np.abs(a[y1:y2,x1:x2].astype(np.int16)-encoded_first[y1:y2,x1:x2].astype(np.int16)).mean()))
assert decoder.wait()==0
assert max(encoded_stats.values())<.5,encoded_stats
assert np.array_equal(a,encoded_first)
manifest={'created_date':'2026-10-02','generator':'built-in image_gen','source_kind':'AI edited interior including tables and chairs; v003 park reused',
    'prompts':'../../../workflows/vvoori-cafe/v004-image-prompt.md','files':{}}
for path in assets.glob('*.png'):
    with Image.open(path) as im:manifest['files'][path.name]={'size':list(im.size),'mode':im.mode,'bytes':path.stat().st_size,'sha256':hashlib.sha256(path.read_bytes()).hexdigest()}
(assets/'provenance.json').write_text(json.dumps(manifest,indent=2),encoding='utf-8')
sheet=Image.new('RGB',(1280,810),'#30291f');draw=ImageDraw.Draw(sheet)
checker=Image.new('RGBA',(640,360),(55,55,55,255));cd=ImageDraw.Draw(checker)
for y in range(0,360,20):
    for x in range(0,640,20):
        if (x//20+y//20)%2:cd.rectangle((x,y,x+19,y+19),fill=(85,85,85,255))
checker.alpha_composite(Image.open(assets/'ai-furnished-interior.png').convert('RGBA').resize((640,360)))
sheet.paste(Image.open(root/'assets/vvoori-cafe/v003/ai-oblique-park.png').convert('RGB').resize((640,360)),(0,30))
sheet.paste(checker.convert('RGB'),(640,30))
sheet.paste(Image.open(frames/'0001.png').resize((640,360)),(0,450))
sheet.paste(Image.open(frames/'0241.png').resize((640,360)),(640,450))
for x,y,label in [(12,9,'AI CARTOON PARK'),(652,9,'AI INTERIOR + TABLES + CHAIRS'),(12,425,'3D COMPOSITE | 0 s / 50 degree view'),(652,425,'3D COMPOSITE | 10 s')]:draw.text((x,y),label,fill='#f1d5a4')
sheet.save(out/'layers-review.jpg',quality=93)
sheet.save(Path(__file__).with_name('v004-layers-review.jpg'),quality=90)
Image.open(out/'poster-fullhd.png').resize((960,540)).save(Path(__file__).with_name('v004-preview.jpg'),quality=93)
(out/'play-loop.html').write_text('''<!doctype html><html lang="ko"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>vvoori-cafe · 만화풍 사선 카페</title>
<style>body{margin:0;background:#282018;color:#f5e6cf;font:16px system-ui}main{max-width:1400px;margin:auto;padding:24px}video,img{width:100%;border-radius:8px}p{color:#d4c0a6}a{color:#eebc70}</style>
<main><h1>vvoori-cafe · 가을 오후</h1><p>50도 사선 통창 · 새로 생성한 만화풍 공원과 실내 · 그림으로 생성한 테이블과 의자 · 3D 창틀, 차량과 낙엽</p>
<video src="vvoori-cafe-toon-20s.mp4" poster="poster-fullhd.png" controls autoplay muted loop playsinline></video>
<p>1920×1080 · 24fps · 20초 반복 · 무음</p><img src="layers-review.jpg" alt="생성 이미지와 실제 3D 합성 확인표">
<p><a href="vvoori-cafe-toon-20s.mp4" download>영상 다운로드</a></p></main></html>''',encoding='utf-8')
report={'ok':True,'width':1920,'height':1080,'fps':24,'frames':480,'duration_seconds':20,
    'full_quality_movie_rendered':True,'furniture_is_generated_image':True,'all_frames_verified':True,'source_png_endpoints_identical':True,
    'decoded_mp4_endpoints_identical':True,'independent_endpoint_mean':independent,'static_roi_bounds':rois,
    'static_roi_all_frames_max_delta':stats,'encoded_static_roi_max_mean_delta':encoded_stats,
    'max_interframe_mean_delta':max(steps),'full_decode':True,'camera_angle_degrees':50,
    'video_bytes':video.stat().st_size,'video_sha256':hashlib.sha256(video.read_bytes()).hexdigest()}
(out/'verification.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
Path(__file__).with_name('v004-verification-summary.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
print(json.dumps(report,indent=2))
