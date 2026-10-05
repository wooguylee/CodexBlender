"""직접 합성한 음악/효과음, 한국어 자막, 사진 반전을 더해 실제 렌더를 MP4로 납품한다."""
from pathlib import Path
import argparse, hashlib, json, math, os, shutil, subprocess, wave
import numpy as np
from PIL import Image, ImageDraw, ImageFont

ROOT=Path(__file__).resolve().parents[2]
OUT=ROOT/'outputs/weather-shorts/v001'
SR=48000
FONT=Path(os.environ.get('WINDIR','C:/Windows'))/'Fonts/malgun.ttf'
assert FONT.is_file(), 'Korean rendering requires the installed Malgun Gothic font.'
FFMPEG=shutil.which('ffmpeg');FFPROBE=shutil.which('ffprobe')
assert FFMPEG and FFPROBE


def audio(story,folder):
    duration=story['duration'];n=duration*SR
    left=np.zeros(n,dtype=np.float64);right=np.zeros(n,dtype=np.float64)
    rng=np.random.default_rng(1200+story['id'])
    def add(signal,start,gain=1,pan=0):
        first=max(0,round(start*SR));length=min(len(signal),n-first)
        if length<=0:return
        segment=signal[:length]*gain
        left[first:first+length]+=segment*(1-pan*.55)
        right[first:first+length]+=segment*(1+pan*.55)
    # Original plucked pentatonic motif; no samples, copyrighted songs or voices.
    tempo=104 if story['id'] in (1,2) else 92
    beat=60/tempo
    scale=[261.626,293.665,329.628,391.995,440.0,523.251]
    pattern=[0,2,3,2,1,2,4,3,0,2,5,3,1,4,2,1]
    for k,start in enumerate(np.arange(0,duration,beat/2)):
        freq=scale[pattern[(k+story['id']*2)%len(pattern)]]
        tt=np.arange(int(.44*SR))/SR
        pluck=(np.sin(2*np.pi*freq*tt)+.27*np.sin(2*np.pi*freq*2*tt)+.1*np.sin(2*np.pi*freq*3*tt))*np.exp(-tt*10)
        pluck*=np.minimum(1,tt/.004)
        add(pluck,start,.028 if k%2 else .043,pan=.25*math.sin(k))
        if k%4==0:
            tb=np.arange(int(.75*SR))/SR
            bass=np.sin(2*np.pi*(130.813 if k%16<8 else 146.832)*tb)*np.exp(-tb*5)
            add(bass,start,.027)
        if k%2==1:
            tp=np.arange(int(.075*SR))/SR
            click=rng.normal(0,1,len(tp))*np.exp(-tp*70)
            add(click,start,.006)
    event_records=[]
    for index,(start,kind) in enumerate(story['sfx']):
        length={'ding':.9,'tick':.10,'camera':.22,'pop':.22,'whoosh':1.05,'boing':.55,
                'sneeze':.65,'ice':1.0,'slide':1.1,'rain':1.3,'heat':1.1,'bubble':.6,'snore':1.1}[kind]
        tt=np.arange(int(length*SR))/SR;u=tt/length
        noise=rng.normal(0,1,len(tt))
        if kind=='ding':sig=(np.sin(2*np.pi*880*tt)+.45*np.sin(2*np.pi*1320*tt))*np.exp(-tt*5)
        elif kind=='tick':sig=noise*np.exp(-tt*90)*.3
        elif kind=='camera':sig=noise*(np.exp(-tt*100)+.5*np.exp(-((tt-.09)/.015)**2))*.6
        elif kind=='pop':sig=np.sin(2*np.pi*(490*tt-700*tt*tt))*np.exp(-tt*25)+noise*.13*np.exp(-tt*40)
        elif kind=='whoosh':sig=noise*np.sin(np.pi*u)**2*.22
        elif kind=='sneeze':sig=noise*(.2*np.exp(-((u-.22)/.11)**2)+.8*np.exp(-((u-.65)/.15)**2))*.45
        elif kind in ('boing','slide','bubble'):
            freq=(300+150*np.sin(np.pi*u)) if kind=='boing' else (700-490*u if kind=='slide' else 320+800*u)
            phase=2*np.pi*np.cumsum(freq)/SR
            sig=np.sin(phase)*np.exp(-u*3)*np.minimum(1,tt/.006)
        elif kind=='ice':sig=sum(np.sin(2*np.pi*f*tt)*np.exp(-tt*(5+i)) for i,f in enumerate((1175,1568,2093)))/3
        elif kind=='rain':sig=noise*.15*np.sin(np.pi*u)**.6
        elif kind=='heat':sig=np.sin(2*np.pi*(210*tt+25*tt*tt))*.3*np.sin(np.pi*u)
        else:sig=(np.sin(2*np.pi*85*tt)+.35*np.sin(2*np.pi*170*tt))*np.sin(np.pi*u)**2*.6
        add(sig,start,.12,pan=.35*math.sin(index*2))
        event_records.append({'time':start,'type':kind,'duration':length})
    fade=np.ones(n)
    fade[:int(.15*SR)]=np.linspace(0,1,int(.15*SR))
    fade[-int(1.0*SR):]=np.linspace(1,0,int(1.0*SR))
    data=np.stack((left*fade,right*fade),axis=1)
    peak=float(np.abs(data).max())
    data*=min(1.5,.65/max(peak,1e-9))
    pcm=(np.clip(data,-1,1)*32767).astype('<i2')
    path=folder/'original-score.wav'
    with wave.open(str(path),'wb') as stream:
        stream.setnchannels(2);stream.setsampwidth(2);stream.setframerate(SR);stream.writeframes(pcm.tobytes())
    metadata={'sample_rate':SR,'channels':2,'duration':duration,'peak':float(np.abs(data).max()),
              'rms':float(np.sqrt(np.mean(data*data))),'events':event_records,
              'provenance':'Original mathematical synthesis: pentatonic plucks, sine tones, seeded noise. No external audio.'}
    (folder/'audio-manifest.json').write_text(json.dumps(metadata,indent=2),encoding='utf-8')
    return path


def escape_filter(path):
    return str(path).replace('\\','/').replace(':','\\:').replace("'","\\'")


def package(folder):
    story=json.loads((folder/'story.json').read_text(encoding='utf-8'))
    render=json.loads((folder/'render-result.json').read_text(encoding='utf-8'))
    assert render['ok'] and render['frames']==story['frames']
    movie=folder/(story['slug']+'.mp4')
    if movie.exists():
        print('Already packaged: '+story['slug'],flush=True);return
    score=audio(story,folder)
    text_dir=folder/'captions';text_dir.mkdir(exist_ok=True)
    font=escape_filter(FONT)
    filters=[]
    tag=text_dir/'series.txt';tag.write_text('날씨 요정들  ·  '+str(story['id']).zfill(2),encoding='utf-8')
    tag_path=escape_filter(tag.relative_to(ROOT))
    filters.append(f"drawtext=fontfile='{font}':textfile='{tag_path}':fontsize=28:fontcolor=0x675B72:x=55:y=32")
    for i,(start,end,text) in enumerate(story['captions']):
        path=text_dir/f'line-{i}.txt';path.write_text(text,encoding='utf-8')
        path_filter=escape_filter(path.relative_to(ROOT))
        size=62 if i==0 else 44;y='95' if i==0 else 'h-140'
        filters.append(f"drawtext=fontfile='{font}':textfile='{path_filter}':fontsize={size}:fontcolor=0x4E405A:x=(w-tw)/2:y={y}:box=1:boxcolor=white@0.76:boxborderw=18:enable='between(t,{start},{end-.04})'")
    command=[FFMPEG,'-hide_banner','-y','-framerate','24','-start_number','1','-i',str(folder/'frames/frame-%04d.png'),'-i',str(score)]
    chain=''
    if story['id']==1:
        command+=['-loop','1','-framerate','24','-i',str(folder/'frames/frame-0385.png')]
        chain="[2:v]scale=1200:675,pad=1240:755:20:20:white,format=rgba,rotate=-0.025:ow=rotw(-0.025):oh=roth(-0.025):c=none[photo];[0:v][photo]overlay=(W-w)/2:(H-h)/2:enable='between(t,17,20)':shortest=1[base];"
        filters.insert(0,"drawbox=x=0:y=0:w=iw:h=ih:color=white:t=fill:enable='between(t,16,16.08)'")
        chain+='[base]'
    else:chain='[0:v]'
    chain+=','.join(filters)+'[v]'
    temporary=folder/(story['slug']+'.partial.mp4')
    command+=['-filter_complex',chain,'-map','[v]','-map','1:a','-c:v','libx264','-preset','medium','-crf','19','-pix_fmt','yuv420p',
              '-r','24','-c:a','aac','-b:a','160k','-ar','48000','-t',str(story['duration']),'-movflags','+faststart',
              '-metadata','title='+story['title'],str(temporary)]
    with (folder/'encode.log').open('w',encoding='utf-8') as log:
        subprocess.run(command,cwd=ROOT,stdout=log,stderr=subprocess.STDOUT,check=True)
    temporary.replace(movie)
    poster_time={1:18,2:9,3:29,4:20,5:24}[story['id']]
    subprocess.run([FFMPEG,'-hide_banner','-loglevel','error','-y','-ss',str(poster_time),'-i',str(movie),'-frames:v','1',str(folder/'poster.png')],check=True)
    (folder/'package.json').write_text(json.dumps({'ok':True,'movie':movie.relative_to(ROOT).as_posix(),
        'sha256':hashlib.sha256(movie.read_bytes()).hexdigest(),'bytes':movie.stat().st_size,
        'captions':story['captions'],'font':'Windows installed Malgun Gothic, rasterized by FFmpeg; font file not redistributed.',
        'audio':'original-score.wav','photo_snapshot_frame':385 if story['id']==1 else None},indent=2,ensure_ascii=False),encoding='utf-8')
    print(json.dumps({'packaged':story['slug'],'bytes':movie.stat().st_size},ensure_ascii=False),flush=True)


def contacts(folder,mode='storyboard'):
    story=json.loads((folder/'story.json').read_text(encoding='utf-8'))
    if mode=='storyboard':
        images=[(folder/'storyboard'/f'beat-{t:02d}.png',t) for t in story['beats']]
    else:
        dest=folder/'video-review';dest.mkdir(exist_ok=True)
        movie=folder/(story['slug']+'.mp4');images=[]
        for t in story['beats']:
            path=dest/f'second-{t:02d}.png'
            subprocess.run([FFMPEG,'-hide_banner','-loglevel','error','-y','-ss',str(t),'-i',str(movie),'-frames:v','1','-vf','scale=640:360',str(path)],check=True)
            images.append((path,t))
    w,h=480,270;rows=(len(images)+2)//3
    canvas=Image.new('RGB',(3*w,rows*(h+32)+56),'#F3EDF4')
    draw=ImageDraw.Draw(canvas);font=ImageFont.truetype(str(FONT),22)
    draw.text((18,12),story['title']+'  /  '+mode,fill='#504256',font=font)
    for i,(path,t) in enumerate(images):
        im=Image.open(path).convert('RGB');im.thumbnail((w,h))
        x=(i%3)*w;y=56+(i//3)*(h+32)
        canvas.paste(im,(x,y));draw.text((x+10,y+h+3),str(t)+'초',fill='#504256',font=font)
    path=folder/(mode+'-contact.png');canvas.save(path)
    return path


if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--episode',type=int);parser.add_argument('--contacts',choices=['storyboard','video']);args=parser.parse_args()
    manifest=json.loads((OUT/'production-manifest.json').read_text(encoding='utf-8'))
    for story in manifest['episodes']:
        if args.episode and story['id']!=args.episode:continue
        folder=OUT/story['slug']
        if args.contacts:print(contacts(folder,args.contacts),flush=True)
        else:package(folder)
