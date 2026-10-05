"""다섯 개의 검증된 단편을 모아보기 MP4와 한 장의 결과표로 정리한다."""
from pathlib import Path
import hashlib, json, os, shutil, subprocess
from PIL import Image, ImageDraw, ImageFont

root=Path(__file__).resolve().parents[2];out=root/'outputs/weather-shorts/v001'
manifest=json.loads((out/'production-manifest.json').read_text(encoding='utf-8'))
verified=json.loads((out/'verification-summary.json').read_text(encoding='utf-8'))
assert verified['ok'] and len(verified['episodes'])==5
ffmpeg=shutil.which('ffmpeg');ffprobe=shutil.which('ffprobe')
movie=out/'weather-fairies-five-stories.mp4'
command=[ffmpeg,'-hide_banner','-y']
for ep in manifest['episodes']:command+=['-i',str(out/ep['slug']/(ep['slug']+'.mp4'))]
chain=''
for i,ep in enumerate(manifest['episodes']):
    duration=ep['duration']
    chain+=f'[{i}:v:0]trim=duration={duration},setpts=PTS-STARTPTS[v{i}];[{i}:a:0]atrim=duration={duration},asetpts=PTS-STARTPTS[a{i}];'
chain+=''.join(f'[v{i}][a{i}]' for i in range(5))+'concat=n=5:v=1:a=1[v][a]'
temporary=movie.with_suffix('.partial.mp4')
command+=['-filter_complex',chain,'-map','[v]','-map','[a]','-c:v','libx264','-preset','fast','-crf','19','-pix_fmt','yuv420p',
          '-r','24','-c:a','aac','-b:a','160k','-ar','48000','-t','140','-movflags','+faststart',str(temporary)]
with (out/'compilation-encode.log').open('w',encoding='utf-8') as log:subprocess.run(command,stdout=log,stderr=subprocess.STDOUT,check=True)
temporary.replace(movie)
probe=json.loads(subprocess.check_output([ffprobe,'-v','error','-count_frames','-show_streams','-show_format','-of','json',str(movie)],text=True,encoding='utf-8'))
video=next(s for s in probe['streams'] if s['codec_type']=='video')
assert int(video['nb_read_frames'])==3360 and abs(float(probe['format']['duration'])-140)<.05
decode=subprocess.run([ffmpeg,'-v','error','-xerror','-i',str(movie),'-f','null','-'],capture_output=True,text=True)
assert not decode.returncode and not decode.stderr.strip(),decode.stderr

font_path=str(Path(os.environ.get('WINDIR','C:/Windows'))/'Fonts/malgun.ttf')
font=ImageFont.truetype(font_path,25);titlefont=ImageFont.truetype(font_path,36);smallfont=ImageFont.truetype(font_path,23)
sheet=Image.new('RGB',(1440,968),'#F5F0F7');draw=ImageDraw.Draw(sheet)
draw.text((30,16),'오늘의 날씨 요정들  ·  다섯 가지 이야기',font=titlefont,fill='#524661')
for i,ep in enumerate(manifest['episodes']):
    x=(i%2)*720;y=85+(i//2)*294
    with Image.open(out/ep['slug']/'poster.png') as im:
        im=im.convert('RGB');im.thumbnail((680,242));sheet.paste(im,(x+(720-im.width)//2,y))
    draw.text((x+28,y+248),f"{i+1:02d}  {ep['title']}  ·  {ep['duration']}초",font=font,fill='#524661')
draw.text((755,728),'몽실 · 해롱 · 또르 · 송송 · 솔솔',font=font,fill='#6F607E')
draw.text((755,775),'5편 / 총 2분 20초',font=titlefont,fill='#524661')
draw.text((755,835),'1080p · 24fps · 음악과 효과음 · 한국어 자막',font=smallfont,fill='#6F607E')
sheet.save(out/'five-stories-contact.png')
report={'ok':True,'compilation':movie.relative_to(root).as_posix(),'frames':3360,'duration_seconds':140,'resolution':[1920,1080],'fps':24,
        'movie_sha256':hashlib.sha256(movie.read_bytes()).hexdigest(),'movie_bytes':movie.stat().st_size,'decode_errors':0,
        'chapters':[{'title':ep['title'],'start_seconds':sum(e['duration'] for e in manifest['episodes'][:i]),'duration':ep['duration']} for i,ep in enumerate(manifest['episodes'])]}
(out/'delivery.json').write_text(json.dumps(report,indent=2,ensure_ascii=False),encoding='utf-8')
print(json.dumps(report,ensure_ascii=False),flush=True)
