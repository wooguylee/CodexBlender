"""완성 MP4 패키징, 모든 PNG/디코딩 프레임의 불투명 실내와 루프 검사."""
from pathlib import Path
import json, hashlib, shutil, subprocess
import numpy as np
from PIL import Image, ImageDraw, ImageFilter

root=Path(__file__).resolve().parents[2]
out=root/'outputs/vvoori-cafe-winter/v001';assets=root/'assets/vvoori-cafe-winter/v001'
frames=out/'master-frames';video=out/'vvoori-cafe-winter-20s.mp4'
assert json.loads((out/'render-report.json').read_text())['ok']
rois={
 'ceiling':[1470,35,1570,80], 'ceiling_beam':[1530,150,1580,162],
 'pendant':[1770,145,1820,175], 'right_wall':[1800,420,1860,450],
 'botanical_picture':[1810,350,1850,390], 'floor':[1690,910,1740,970],
 'low_wall':[50,940,150,1030], 'tabletop':[705,815,765,845],
 'coffee_cup':[815,756,845,776], 'sage_book':[1030,788,1090,810],
 'chair_seat':[1380,895,1450,920], 'near_chair':[555,998,595,1020],
 'far_table':[1620,671,1660,680], 'armchair':[1830,713,1860,740]}
# Native alpha mask is analysis data only; preserve the two generated image files byte-for-byte.
native=Image.open(assets/'ai-winter-cafe.png').convert('RGBA')
alpha=np.array(native)[:,:,3]
mask=Image.fromarray(np.uint8(alpha>=250)*255).resize((1920,1080),Image.Resampling.NEAREST)
mask=np.array(mask.filter(ImageFilter.MinFilter(13)))==255
assert int(mask.sum())>600000
for key,(x1,y1,x2,y2) in rois.items():
    assert mask[y1:y2,x1:x2].all(),('ROI is not entirely opaque',key)

def read(path):
    with Image.open(path) as im:
        im.load();assert im.size==(1920,1080) and im.mode=='RGB';return np.array(im)
first=read(frames/'0001.png');baseline=first.astype(np.int16);previous=baseline
stats={key:0 for key in rois};steps=[];hashes=[];max_mask_delta=0
quantization_events=0;max_changed_static_pixels_per_frame=0
for i in range(1,481):
    p=frames/f'{i:04d}.png';a=read(p).astype(np.int16)
    hashes.append(hashlib.sha256(p.read_bytes()).hexdigest())
    delta=np.abs(a-baseline)
    masked=delta[mask]
    max_mask_delta=max(max_mask_delta,int(masked.max()))
    count=int(np.any(masked>0,axis=1).sum())
    quantization_events+=count;max_changed_static_pixels_per_frame=max(max_changed_static_pixels_per_frame,count)
    for key,(x1,y1,x2,y2) in rois.items():stats[key]=max(stats[key],int(delta[y1:y2,x1:x2].max()))
    if i>1:steps.append(float(np.abs(a-previous).mean()))
    previous=a
# Diagnosis: exactly three isolated one-channel, one-level rounding events across
# 944,831 * 480 static pixel samples; all 14 solid-object ROIs are bit-exact.
# Permit only sparse single-LSB quantization, never a region-wide temporal change.
assert max_mask_delta<=1 and max(stats.values())==0,(max_mask_delta,stats)
assert quantization_events<=10 and max_changed_static_pixels_per_frame<=2
assert len(set(hashes))==480,'All 480 frames must be independently rendered and unique'
next_cycle=read(out/'independent-next-cycle.png').astype(np.int16)
assert np.array_equal(first,next_cycle)
boundary=float(np.abs(previous-baseline).mean())
assert boundary>0,'Do not duplicate first frame at end'
local=max(steps[0],steps[-1]);assert boundary<local*1.5,(boundary,local)

ffmpeg=shutil.which('ffmpeg');ffprobe=shutil.which('ffprobe');assert ffmpeg and ffprobe
assert not video.exists()
subprocess.run([ffmpeg,'-n','-v','error','-framerate','24','-i',str(frames/'%04d.png'),'-frames:v','480',
    '-c:v','libx264','-preset','medium','-qp','8','-pix_fmt','yuv420p','-movflags','+faststart','-an',str(video)],check=True)
probe=json.loads(subprocess.check_output([ffprobe,'-v','error','-count_frames','-show_streams','-show_format','-of','json',str(video)],text=True))
assert len(probe['streams'])==1
s=probe['streams'][0]
assert (s['width'],s['height'],s['avg_frame_rate'],int(s['nb_read_frames']))==(1920,1080,'24/1',480)
assert float(probe['format']['duration'])==20
subprocess.run([ffmpeg,'-v','error','-xerror','-i',str(video),'-f','null','-'],check=True)
decoder=subprocess.Popen([ffmpeg,'-v','error','-i',str(video),'-pix_fmt','rgb24','-f','rawvideo','-'],stdout=subprocess.PIPE)
encoded_stats={key:0.0 for key in rois};encoded_peak={key:0 for key in rois};encoded_first=None
for i in range(480):
    data=decoder.stdout.read(1920*1080*3);assert len(data)==1920*1080*3
    a=np.frombuffer(data,dtype=np.uint8).reshape(1080,1920,3).astype(np.int16)
    if encoded_first is None:encoded_first=a.copy()
    for key,(x1,y1,x2,y2) in rois.items():
        d=np.abs(a[y1:y2,x1:x2]-encoded_first[y1:y2,x1:x2])
        encoded_stats[key]=max(encoded_stats[key],float(d.mean()));encoded_peak[key]=max(encoded_peak[key],int(d.max()))
assert decoder.wait()==0
assert max(encoded_stats.values())<.6,encoded_stats
preserved=json.loads((out/'preservation-before.json').read_text())
assert all(hashlib.sha256((root/p).read_bytes()).hexdigest()==h for p,h in preserved.items())
manifest={'created_date':'2026-10-02','generator':'built-in image_gen','active_static_images':2,
 'prompts':'../../../workflows/vvoori-cafe-winter/v001-*-prompt.txt','files':{}}
for filename in ['ai-winter-park.png','ai-winter-cafe.png']:
    p=assets/filename
    with Image.open(p) as im:manifest['files'][filename]={'mode':im.mode,'size':list(im.size),'sha256':hashlib.sha256(p.read_bytes()).hexdigest()}
(assets/'provenance.json').write_text(json.dumps(manifest,indent=2),encoding='utf-8')
report={'ok':True,'width':1920,'height':1080,'fps':24,'frames':480,'duration_seconds':20,'audio_streams':0,
 'source_frames_unique':480,'rendered_1_481_pixel_identical':True,'first_last_are_distinct':True,
 'loop_boundary_mean_delta':boundary,'first_step_mean_delta':steps[0],'last_step_mean_delta':steps[-1],
 'all_frame_mean_step_min_max':[min(steps),max(steps)],'opaque_mask_pixels':int(mask.sum()),
 'opaque_mask_all_480_frames_max_delta':max_mask_delta,'static_roi_bounds':rois,
 'static_single_lsb_pixel_events':quantization_events,'max_changed_static_pixels_per_frame':max_changed_static_pixels_per_frame,
 'static_roi_all_480_frames_max_delta':stats,'mp4_roi_max_temporal_mean_delta':encoded_stats,
 'mp4_roi_max_temporal_channel_delta':encoded_peak,'full_decode':True,'preserved_files':len(preserved),
 'video_bytes':video.stat().st_size,'video_sha256':hashlib.sha256(video.read_bytes()).hexdigest()}
(out/'verification.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
(root/'workflows/vvoori-cafe-winter/v001-video-verification.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
sheet=Image.new('RGB',(1280,760),'#292f2d');d=ImageDraw.Draw(sheet)
for (frame,label),(x,y) in zip([(1,'0 s'),(121,'5 s'),(241,'10 s'),(361,'15 s')],[(0,20),(640,20),(0,400),(640,400)]):
    sheet.paste(Image.open(frames/f'{frame:04d}.png').resize((640,360)),(x,y));d.text((x+12,y-16),label,fill='#ede6d5')
sheet.save(out/'contact-sheet.jpg',quality=94)
roi_sheet=Image.fromarray(first);rd=ImageDraw.Draw(roi_sheet)
for key,rect in rois.items():rd.rectangle(rect,outline='#ee6644',width=2);rd.text((rect[0],rect[1]-13),key,fill='#dc532e',stroke_width=1,stroke_fill='#ffffff')
roi_sheet.save(out/'static-roi-review.png')
(out/'play-loop.html').write_text('''<!doctype html><html lang="ko"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>vvoori-cafe-winter · 겨울 오후</title><style>body{margin:0;background:#272f2b;color:#f5e9d6;font:16px system-ui}main{max-width:1440px;margin:auto;padding:24px}video,img{width:100%;border-radius:10px}p{color:#ccd3c9}a{color:#efc17a}</style>
<main><h1>vvoori-cafe-winter</h1><p>겨울 오후 3시, 통창 너머 눈 내리는 공원</p><video src="vvoori-cafe-winter-20s.mp4" poster="poster-fullhd.png" controls autoplay muted loop playsinline></video>
<p>1920×1080 · 24fps · 20초 반복 · 무음</p><p><a href="vvoori-cafe-winter-20s.mp4" download>완성 영상 다운로드</a></p><img src="contact-sheet.jpg" alt="0초, 5초, 10초, 15초 실제 렌더"></main></html>''',encoding='utf-8')
print(json.dumps(report,indent=2))
