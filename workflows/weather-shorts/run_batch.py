"""공식 Blender Python 렌더를 편별로 순차 실행. 다른 Blender 창은 종료/연결하지 않는다."""
from pathlib import Path
import argparse, json, subprocess, sys, time

parser=argparse.ArgumentParser()
parser.add_argument('--blender',required=True)
parser.add_argument('--mode',choices=['storyboard','full'],required=True)
args=parser.parse_args()
root=Path(__file__).resolve().parents[2]
out=root/'outputs/weather-shorts/v001'
manifest=json.loads((out/'production-manifest.json').read_text(encoding='utf-8'))
queue={ep['slug']:'pending' for ep in manifest['episodes']}
queue_path=out/(args.mode+'-queue.json')
for ep in manifest['episodes']:
    queue[ep['slug']]='running';queue_path.write_text(json.dumps(queue,indent=2),encoding='utf-8')
    folder=out/ep['slug'];started=time.monotonic()
    with (folder/(args.mode+'-render.log')).open('w',encoding='utf-8') as log:
        result=subprocess.run([args.blender,'--background',str(root/ep['source']),
             '--python',str(root/'workflows/weather-shorts/05_render_episode.py'),'--','--mode',args.mode],
             cwd=root,stdout=log,stderr=subprocess.STDOUT,
             creationflags=getattr(subprocess,'CREATE_NO_WINDOW',0))
    record=folder/('render-result.json' if args.mode=='full' else 'storyboard-verification.json')
    if result.returncode or not record.exists() or not json.loads(record.read_text(encoding='utf-8')).get('ok'):
        queue[ep['slug']]='failed';queue_path.write_text(json.dumps(queue,indent=2),encoding='utf-8')
        raise RuntimeError(f"{ep['slug']} failed; inspect its {args.mode}-render.log")
    if args.mode=='full':
        queue[ep['slug']]='encoding';queue_path.write_text(json.dumps(queue,indent=2),encoding='utf-8')
        subprocess.run([sys.executable,str(root/'workflows/weather-shorts/06_package_movies.py'),'--episode',str(ep['id'])],cwd=root,check=True)
        subprocess.run([sys.executable,str(root/'workflows/weather-shorts/06_package_movies.py'),'--episode',str(ep['id']),'--contacts','video'],cwd=root,check=True)
    queue[ep['slug']]='complete';queue_path.write_text(json.dumps(queue,indent=2),encoding='utf-8')
    print(json.dumps({'completed':ep['slug'],'mode':args.mode,'seconds':round(time.monotonic()-started,2)},ensure_ascii=False),flush=True)
print('All five '+args.mode+' jobs complete.',flush=True)
