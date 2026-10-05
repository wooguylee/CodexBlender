"""완성 영상 전체 디코딩, 모든 원본 프레임, 국소 고정 영역과 오디오를 실제 출력에서 검사."""
from pathlib import Path
import argparse, hashlib, json, math, shutil, subprocess, time
import numpy as np
from PIL import Image

ROOT=Path(__file__).resolve().parents[2]
OUT=ROOT/'outputs/weather-shorts/v001'
FFMPEG=shutil.which('ffmpeg');FFPROBE=shutil.which('ffprobe')


def verify(story):
    start=time.monotonic();folder=OUT/story['slug'];movie=folder/(story['slug']+'.mp4')
    assert movie.exists()
    source=json.loads((folder/'render-source.json').read_text(encoding='utf-8'))
    assert hashlib.sha256((ROOT/source['source']).read_bytes()).hexdigest()==source['sha256']
    paths=sorted((folder/'frames').glob('frame-*.png'))
    assert [p.name for p in paths]==[f'frame-{i:04d}.png' for i in range(1,story['frames']+1)]
    # These floor areas remain outside the actors, shadows, and props.
    regions={'top_left':[10,10,130,100],'top_right':[1790,10,1910,100],
             'bottom_left':[10,945,190,1070],'bottom_right':[1730,945,1910,1070],
             'bottom_middle':[710,1000,1210,1070]}
    references={};stability={k:{'max_channel_delta':0,'changed_samples':0,'frames_checked':0} for k in regions}
    previous=None;changes=[];hashes=set();alpha_min=255
    for i,path in enumerate(paths,1):
        with Image.open(path) as im:
            im.load();assert im.size==(1920,1080) and im.mode=='RGBA',(path,im.size,im.mode)
            alpha_min=min(alpha_min,im.getchannel('A').getextrema()[0])
            # Episode 4 intentionally changes the entire frame for the final cloud closeup.
            if story['id']!=4 or i<=23*24:
                for key,(x1,y1,x2,y2) in regions.items():
                    crop=np.asarray(im.crop((x1,y1,x2,y2)),dtype=np.int16)
                    if key not in references:references[key]=crop.copy()
                    delta=np.abs(crop-references[key]);r=stability[key]
                    r['max_channel_delta']=max(r['max_channel_delta'],int(delta.max()))
                    r['changed_samples']+=int(np.count_nonzero(delta));r['frames_checked']+=1
            small=np.asarray(im.convert('RGB').resize((240,135),Image.Resampling.BOX),dtype=np.int16)
            hashes.add(hashlib.sha256(small.tobytes()).hexdigest())
            if previous is not None:changes.append(float(np.abs(small-previous).mean()))
            previous=small
    assert alpha_min==255
    assert all(r['max_channel_delta']<=1 for r in stability.values()),stability
    assert len(hashes)>story['frames']*.70,(len(hashes),story['frames'])
    probe=json.loads(subprocess.check_output([FFPROBE,'-v','error','-count_frames','-show_streams','-show_format','-of','json',str(movie)],text=True,encoding='utf-8'))
    video=next(s for s in probe['streams'] if s['codec_type']=='video')
    audio=next(s for s in probe['streams'] if s['codec_type']=='audio')
    assert (video['codec_name'],video['width'],video['height'],video['r_frame_rate'],int(video['nb_read_frames']))==('h264',1920,1080,'24/1',story['frames'])
    assert abs(float(probe['format']['duration'])-story['duration'])<.05
    assert audio['codec_name']=='aac' and int(audio['sample_rate'])==48000 and audio['channels']==2
    decode=subprocess.run([FFMPEG,'-v','error','-xerror','-i',str(movie),'-f','null','-'],capture_output=True,text=True)
    assert decode.returncode==0 and not decode.stderr.strip(),decode.stderr
    pcm=subprocess.check_output([FFMPEG,'-v','error','-i',str(movie),'-map','0:a:0','-f','f32le','-c:a','pcm_f32le','-'])
    samples=np.frombuffer(pcm,dtype='<f4');assert np.isfinite(samples).all()
    peak=float(np.abs(samples).max());rms=float(np.sqrt(np.mean(samples.astype(np.float64)**2)))
    assert peak<.99 and rms>.003,(peak,rms)
    peakframe=int(np.argmax(changes))+2
    report={'ok':True,'episode':story['slug'],'title':story['title'],'frames':len(paths),'duration_seconds':float(probe['format']['duration']),
            'resolution':[1920,1080],'fps':24,'codec':'H.264 / AAC','full_decode_errors':0,'all_pngs_decoded':True,'alpha_min':alpha_min,
            'unique_downsampled_frames':len(hashes),'static_regions':regions,'static_stability':stability,
            'static_exclusion':'Episode 4 after 23 s intentionally becomes a cloud closeup.' if story['id']==4 else None,
            'adjacent_frame_mean_difference':{'median':float(np.median(changes)),'p95':float(np.percentile(changes,95)),'maximum':float(max(changes)),'maximum_at_frame':peakframe},
            'audio':{'decoded_samples':len(samples),'channels':2,'sample_rate':48000,'peak':peak,'rms':rms,'clipping':False},
            'source':source,'movie_sha256':hashlib.sha256(movie.read_bytes()).hexdigest(),'movie_bytes':movie.stat().st_size,
            'verification_seconds':round(time.monotonic()-start,2),
            'limits':'Metrics verify files, movement and stable regions; visual beat/contact review is recorded separately. Other GPUs/OS not tested.'}
    (folder/'output-verification.json').write_text(json.dumps(report,indent=2,ensure_ascii=False),encoding='utf-8')
    print(json.dumps({'verified':story['slug'],'frames':len(paths),'seconds':report['verification_seconds'],'audio_peak':round(peak,3),'static_max':max(r['max_channel_delta'] for r in stability.values())},ensure_ascii=False),flush=True)
    return report


if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--episode',type=int);parser.add_argument('--available',action='store_true');args=parser.parse_args()
    manifest=json.loads((OUT/'production-manifest.json').read_text(encoding='utf-8'))
    reports=[]
    for story in manifest['episodes']:
        if args.episode and story['id']!=args.episode:continue
        folder=OUT/story['slug']
        if args.available and not (folder/(story['slug']+'.mp4')).exists():continue
        report_path=folder/'output-verification.json'
        if report_path.exists():
            report=json.loads(report_path.read_text(encoding='utf-8'))
            assert report['ok'] and report['movie_sha256']==hashlib.sha256((folder/(story['slug']+'.mp4')).read_bytes()).hexdigest()
            assert report['source']['sha256']==hashlib.sha256((ROOT/story['source']).read_bytes()).hexdigest()
            reports.append(report)
        else:reports.append(verify(story))
    preserved=[]
    for path,expected in manifest['existing_source_sha256'].items():
        assert hashlib.sha256((ROOT/path).read_bytes()).hexdigest()==expected,path
        preserved.append(path)
    if len(reports)==5:
        (OUT/'verification-summary.json').write_text(json.dumps({'ok':True,'episodes':reports,'total_frames':sum(r['frames'] for r in reports),
            'total_seconds':sum(r['duration_seconds'] for r in reports),'preserved_source_files':preserved,'unchanged_sources':len(preserved)},indent=2,ensure_ascii=False),encoding='utf-8')
        print('All five outputs verified; existing sources preserved.',flush=True)
