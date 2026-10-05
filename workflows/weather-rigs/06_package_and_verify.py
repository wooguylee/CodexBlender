"""무음 리깅 시연에 한국어 안내를 붙이고 전체 출력과 원본 보존을 검사한다."""
from pathlib import Path
import hashlib,json,os,shutil,subprocess,time
import numpy as np
from PIL import Image,ImageDraw,ImageFont

ROOT=Path(__file__).resolve().parents[2];OUT=ROOT/'outputs/weather-rigs/v001'
FFMPEG=shutil.which('ffmpeg');FFPROBE=shutil.which('ffprobe');assert FFMPEG and FFPROBE
FONT=Path(os.environ.get('WINDIR','C:/Windows'))/'Fonts/malgun.ttf';assert FONT.is_file()
manifest=json.loads((OUT/'demo-manifest.json').read_text(encoding='utf-8'))
render=json.loads((OUT/'render-result.json').read_text(encoding='utf-8'));assert render['ok'] and render['frames']==384
font=lambda size:ImageFont.truetype(str(FONT),size)
def centered(draw,xy,text,size,fill):draw.text(xy,text,font=font(size),fill=fill,anchor='mt')
details=['5개의 실제 뼈대 · 기본 캐릭터 모습 유지','손·발 목표를 움직이면 두 관절이 함께 따라옵니다',
         '눈 뜨기 · 깜빡임 · 미소 · 놀란 입','몸 눌림과 늘림 · 햇살 · 물방울 꼭지 · 눈 결정',
         '몽실의 안기 · 솔솔의 몸 휘기와 소용돌이 · 스카프']
overlays=[]
for i,(start,end,title) in enumerate(manifest['chapters']):
    im=Image.new('RGBA',(1920,1080),(0,0,0,0));d=ImageDraw.Draw(im)
    centered(d,(960,62),'오늘의 날씨 요정들  |  리깅 시연',40,(62,48,75,255))
    centered(d,(960,120),'실제 Armature + 손발 IK + 표정 컨트롤',24,(102,87,118,255))
    for x,name in zip([327,642,958,1274,1589],['몽실','해롱','또르','송송','솔솔']):
        centered(d,(x,735),name,28,(72,58,88,255))
    d.rounded_rectangle((350,851,1570,1007),radius=28,fill=(249,246,252,238))
    centered(d,(960,870),f'{i+1:02d}  {title}',33,(67,47,91,255))
    centered(d,(960,929),details[i],26,(97,78,116,255))
    d.text((1875,1041),'움직임 확인용 · 무음',font=font(18),fill=(110,95,122,255),anchor='rs')
    path=OUT/f'caption-{i+1}.png';im.save(path);overlays.append(path)
movie=OUT/'weather-rig-demo-16s.mp4'
args=[FFMPEG,'-y','-v','warning','-framerate','24','-start_number','1','-i',str(OUT/'frames/frame_%04d.png')]
for path in overlays:args+=['-loop','1','-i',str(path)]
filters=[];previous='0:v'
for i,(start,end,_) in enumerate(manifest['chapters']):
    current=f'v{i}';filters.append(f"[{previous}][{i+1}:v]overlay=enable='gte(t,{start})*lt(t,{end})':shortest=1[{current}]");previous=current
args+=['-filter_complex',';'.join(filters),'-map',f'[{previous}]','-frames:v','384','-r','24','-c:v','libx264','-preset','medium','-crf','18','-pix_fmt','yuv420p','-an','-movflags','+faststart',str(movie)]
subprocess.run(args,check=True)
regions={'top_left':[10,10,140,130],'top_right':[1780,10,1910,130],
         'bottom_left':[10,930,180,1070],'bottom_right':[1740,930,1910,1070],'bottom_middle':[750,1000,1170,1070]}
reference={};stability={k:0 for k in regions};hashes=set();max_change=0.;previous=None
paths=sorted((OUT/'frames').glob('frame_*.png'));assert [p.name for p in paths]==[f'frame_{i:04d}.png' for i in range(1,385)]
for path in paths:
    with Image.open(path) as im:
        im.load();assert im.size==(1920,1080) and im.mode=='RGBA' and im.getchannel('A').getextrema()==(255,255)
        for name,box in regions.items():
            crop=np.asarray(im.crop(box),dtype=np.int16)
            if name not in reference:reference[name]=crop.copy()
            stability[name]=max(stability[name],int(np.abs(crop-reference[name]).max()))
        small=np.asarray(im.convert('RGB').resize((240,135),Image.Resampling.BOX),dtype=np.int16)
        hashes.add(hashlib.sha256(small.tobytes()).hexdigest())
        if previous is not None:max_change=max(max_change,float(np.abs(small-previous).mean()))
        previous=small
assert max(stability.values())<=1 and len(hashes)>270,(stability,len(hashes))
probe=json.loads(subprocess.check_output([FFPROBE,'-v','error','-count_frames','-show_streams','-show_format','-of','json',str(movie)],text=True,encoding='utf-8'))
assert len(probe['streams'])==1
video=probe['streams'][0]
assert (video['codec_name'],video['width'],video['height'],video['r_frame_rate'],int(video['nb_read_frames']))==('h264',1920,1080,'24/1',384)
assert abs(float(probe['format']['duration'])-16)<.01
decode=subprocess.run([FFMPEG,'-v','error','-xerror','-i',str(movie),'-f','null','-'],capture_output=True,text=True)
assert decode.returncode==0 and not decode.stderr.strip(),decode.stderr
preserved=[]
build=json.loads((OUT/'build-manifest.json').read_text(encoding='utf-8'))
for path,expected in build['preserved_files'].items():
    assert hashlib.sha256((ROOT/path).read_bytes()).hexdigest()==expected,path
    preserved.append(path)
assert hashlib.sha256((ROOT/'scenes/weather-rigs-v001.blend').read_bytes()).hexdigest()==manifest['neutral_source_sha256']
# Corroborate the recovery-time inventory against the earlier, committed project assets.
tracked=subprocess.check_output(['git','ls-files','scenes/weather-fairies-*.blend','scenes/weather-short-*.blend','outputs/weather-shorts'],cwd=ROOT,text=True).splitlines()
assert tracked
for path in tracked:
    expected=subprocess.check_output(['git','rev-parse','HEAD:'+path],cwd=ROOT,text=True).strip()
    actual=subprocess.check_output(['git','hash-object',path],cwd=ROOT,text=True).strip()
    assert actual==expected,path
# Contact sheet is extracted from the delivered MP4, not a separate pose render.
sheet=Image.new('RGB',(1440,1215),(245,240,249));draw=ImageDraw.Draw(sheet)
centered(draw,(720,18),'실제 시연 영상에서 추출한 장면',31,(68,46,84))
times=[.5,3.1,5.6,7.4,10.1,13.3]
for index,seconds in enumerate(times):
    path=OUT/f'demo-check-{index+1}.png'
    subprocess.run([FFMPEG,'-v','error','-y','-ss',str(seconds),'-i',str(movie),'-frames:v','1',str(path)],check=True)
    with Image.open(path) as im:tile=im.convert('RGB').resize((700,394),Image.Resampling.LANCZOS)
    x=10+(index%2)*720;y=66+(index//2)*383
    # Keep the full frame without crop; small overlap is avoided by resizing inside the card.
    tile=tile.resize((650,366),Image.Resampling.LANCZOS);sheet.paste(tile,(x+25,y))
sheet.save(OUT/'rig-demo-contact.png')
report={'ok':True,'frames':384,'duration_seconds':16,'resolution':[1920,1080],'fps':24,'audio':'none',
 'all_pngs_decoded':True,'alpha_min':255,'full_mp4_decode_errors':0,'unique_downsampled_frames':len(hashes),
 'static_regions':regions,'static_max_channel_delta':stability,'adjacent_frame_max_mean_difference':max_change,
 'neutral_source_unchanged':True,'preserved_files':preserved,'unchanged_file_count':len(preserved),
 'prior_committed_assets_checked':len(tracked),'movie_sha256':hashlib.sha256(movie.read_bytes()).hexdigest(),
 'native_source_sha256':manifest['neutral_source_sha256'],'demo_source_sha256':hashlib.sha256((ROOT/manifest['source']).read_bytes()).hexdigest(),
 'visual_review':'See final-delivery.json for the direct review of these outputs.',
 'scope':'Windows / Blender 5.2.1 LTS / RTX 3090. Metrics do not substitute for visual checks.'}
(OUT/'output-verification.json').write_text(json.dumps(report,indent=2,ensure_ascii=False),encoding='utf-8')
print(json.dumps(report,ensure_ascii=False))
