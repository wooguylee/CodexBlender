"""Unity 생성 자산과 검증 증거를 회수하고 배포 압축 파일의 무결성을 확인한다."""
import argparse,hashlib,json,shutil,tarfile,zipfile
from pathlib import Path
from PIL import Image

root=Path(__file__).resolve().parents[2];out=root/'outputs/weather-unity/v001';delivery=root/'exports/weather-fairies/v001'
parser=argparse.ArgumentParser();parser.add_argument('--project',required=True);parser.add_argument('--evidence',required=True);args=parser.parse_args()
project=Path(args.project).resolve();evidence=Path(args.evidence).resolve()
for relative in ('Assets/WeatherFairies','Assets/Scripts/WeatherFairies'):
    shutil.copytree(project/relative,delivery/'unity'/relative,dirs_exist_ok=True)
    shutil.copy2(project/(relative+'.meta'),delivery/'unity'/(relative+'.meta'))
final_previews=['unity-'+pose+'-final.png' for pose in ('neutral','surprise','special')]
for name in final_previews:shutil.copy2(evidence/name,out/name)
for name in ('unity-verification.json','play-verification.json','console-final.json'):shutil.copy2(evidence/name,out/name)
manifest=json.loads((out/'export-manifest.json').read_text(encoding='utf-8'))
unity=json.loads((out/'unity-verification.json').read_text(encoding='utf-8'));assert unity['ok']
play=json.loads((out/'play-verification.json').read_text());assert play['playing'] and len(play['actors'])==5
assert all(a['initialized'] and a['surpriseWeight']>99 for a in play['actors'])
console=json.loads((out/'console-final.json').read_text());assert console['success'] and not console['data']
for relative in ('WeatherFairyExpressions.cs','Editor/WeatherFairySetup.cs'):
    assert (root/'workflows/weather-unity/Unity'/relative).read_bytes()==(delivery/'unity/Assets/Scripts/WeatherFairies'/relative).read_bytes()
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
for path,digest in manifest['preserved_sources'].items():assert sha(root/path)==digest,path
for character in manifest['characters']:
    assert sha(root/character['fbx'])==character['fbx_sha256']
    assert sha(root/character['blender'])==character['blender_sha256']
    check=next(c for c in unity['characters'] if c['name']==character['name'])
    assert check['bones']==character['bones'] and check['skinnedMeshes']==character['meshes'] and check['blendShapes']==character['shape_keys']
    assert check['maxFaceWeightChange']>99 and abs(check['min'][1])<.00001
    bounds=character['sample_poses'][0]['bounds'];size=[bounds['max'][i]-bounds['min'][i] for i in (0,2,1)]
    assert max(abs(a-b) for a,b in zip(check['size'],size))<.001,(character['name'],check['size'],size)
package=delivery/'WeatherFairies-Unity6-URP-v001.unitypackage';assert package.is_file()
with tarfile.open(package,'r:gz') as tar:
    paths=[tar.extractfile(m).read().decode('utf-8').strip() for m in tar.getmembers() if m.name.endswith('/pathname')]
    assert paths and all(p.startswith('Assets/WeatherFairies') or p.startswith('Assets/Scripts/WeatherFairies') for p in paths),paths
    assert len([p for p in paths if p.endswith('.fbx')])==5
    assert len([p for p in paths if p.endswith('.prefab')])==5
    assert len([p for p in paths if p.endswith('.controller')])==5
    matched_assets=0
    for member in tar.getmembers():
        if not member.name.endswith('/pathname'):continue
        relative=tar.extractfile(member).read().decode('utf-8').strip()
        local=delivery/'unity'/relative
        if local.is_file():
            asset_name=member.name.rsplit('/',1)[0]+'/asset'
            assert tar.extractfile(asset_name).read()==local.read_bytes(),relative
            matched_assets+=1
previews=delivery/'previews';previews.mkdir(exist_ok=True)
for path in out.glob('*-native.png'):
    with Image.open(path) as im:im.verify()
    shutil.copy2(path,previews/path.name)
for name in final_previews:
    path=out/name
    with Image.open(path) as im:im.load();assert im.size==(1920,1080)
    shutil.copy2(path,previews/path.name)
# Verify that expressions and special motion changed the actual rendered output.
assert len({sha(previews/name) for name in final_previews})==3
bundle=delivery/'WeatherFairies-Models-v001.zip'
with zipfile.ZipFile(bundle,'w',zipfile.ZIP_DEFLATED,compresslevel=6) as archive:
    archive.write(delivery/'README.md','README.md');archive.write(package,package.name)
    for path in sorted((delivery/'blender').glob('*.blend')):archive.write(path,'blender/'+path.name)
    for path in sorted((delivery/'unity/Assets/WeatherFairies/Models').glob('*.fbx')):archive.write(path,'fbx/'+path.name)
    for name in sorted([p.name for p in previews.glob('*-native.png')]+final_previews):archive.write(previews/name,'previews/'+name)
with zipfile.ZipFile(bundle) as archive:
    assert archive.testzip() is None
    assert len([n for n in archive.namelist() if n.endswith('.blend')])==5
    assert len([n for n in archive.namelist() if n.endswith('.fbx')])==5
report={'ok':True,'native_models':5,'fbx_models':5,'prefabs':5,'animator_controllers':5,'materials':len(manifest['materials']),
 'bones':sum(c['bones'] for c in unity['characters']),'blend_shapes':sum(c['blendShapes'] for c in unity['characters']),
 'animation_clips':sum(len(c['clips']) for c in unity['characters']),'package_paths':paths,'archive_integrity':True,
 'runtime_play_verified':True,'preserved_sources':manifest['preserved_sources'],'unity_version':unity['unityVersion'],
 'package_assets_match_files':matched_assets,'final_console_errors_and_warnings':0,
 'package_sha256':sha(package),'package_bytes':package.stat().st_size,'bundle_sha256':sha(bundle),'bundle_bytes':bundle.stat().st_size,
 'visual_review':['All five standalone native model previews rendered and directly inspected.',
                  'Unity front-facing neutral, surprised and special poses directly inspected after import fixes.'],
 'limitations':['Blender constraints/drivers remain in native models; FBX animations are baked.',
                'Unity live IK solver, Humanoid retargeting, mobile LOD optimization and other render pipelines are outside this export.']}
(out/'delivery-verification.json').write_text(json.dumps(report,indent=2,ensure_ascii=False),encoding='utf-8')
shutil.copy2(out/'delivery-verification.json',delivery/'delivery-verification.json')
shutil.copy2(out/'delivery-verification.json',evidence/'delivery-verification.json')
print(json.dumps({k:v for k,v in report.items() if k not in ('package_paths','visual_review','limitations')},ensure_ascii=False))
