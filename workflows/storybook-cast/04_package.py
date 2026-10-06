"""실제 Unity 출력과 개별 모델을 한국어 사용법·미리보기·주제별 ZIP으로 포장."""
import argparse,hashlib,json,shutil,subprocess,sys,tarfile,zipfile
from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
import numpy as np
from catalog import THEMES,clip_ranges

ROOT=Path(__file__).resolve().parents[2];OUT=ROOT/'outputs/storybook-cast/v001';DEST=ROOT/'exports/storybook-cast/v001'
LABELS={'Idle':'대기','Walk':'걷기 / 느린 헤엄','Run':'달리기 / 빠른 헤엄','SitDown':'앉기','SitIdle':'앉아서 쉬기','StandUp':'일어나기','Wave':'인사','Celebrate':'기뻐하기'}
def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()
def write(path,data):path.parent.mkdir(parents=True,exist_ok=True);path.write_text(json.dumps(data,ensure_ascii=False,indent=2),encoding='utf-8')
def font(size):
    import os
    candidates=[Path(os.environ.get('WINDIR','C:/Windows'))/'Fonts/malgun.ttf',Path('/usr/share/fonts/truetype/noto/NotoSansCJK-Regular.ttc')]
    return ImageFont.truetype(str(next(p for p in candidates if p.exists())),size)
def ordered_records():
    report=json.loads((OUT/'export-manifest.json').read_text(encoding='utf-8'));bykey={c['key']:c for c in report['characters']}
    return report,[bykey[item[0]] for theme in THEMES.values() for item in theme['characters']]
def previews():
    report,records=ordered_records();folder=DEST/'previews';folder.mkdir(exist_ok=True)
    sheet=Image.new('RGB',(1600,1540),'#eef0f5');d=ImageDraw.Draw(sheet)
    d.text((32,20),'이야기 친구들 · 4개 마을, 20개의 개성',font=font(32),fill='#263247')
    for i,c in enumerate(records):
        img=Image.open(OUT/'native'/(c['key']+'.png'));assert img.size==(512,512) and img.mode=='RGBA' and img.getchannel('A').getbbox()
        thumb=img.resize((290,290),Image.Resampling.LANCZOS);x=(i%5)*320;y=(i//5)*360+80;sheet.paste(thumb,(x+15,y),thumb)
        d.text((x+18,y+295),c['ko']+' · '+c['role'],font=font(19),fill='#263247');shutil.copy2(OUT/'native'/(c['key']+'.png'),folder/(c['key']+'.png'))
    sheet.save(folder/'all-20-characters.png');sheet.save(OUT/'native-contact-sheet-final.png')
    poses=Image.new('RGB',(1920,1440),'#eef0f5');pd=ImageDraw.Draw(poses)
    for row,theme in enumerate(THEMES):
        for col,frame in enumerate((62,121,199)):
            img=Image.open(OUT/'unity'/(theme+'-Timeline')/(f'{frame:04}.png')).resize((640,360));poses.paste(img,(640*col,360*row))
            pd.text((640*col+12,360*row+12),theme+' · '+('Walk','Run','SitIdle')[col],font=font(20),fill='#263247')
        shutil.copy2(OUT/'unity'/(theme+'-Timeline')/'0000.png',folder/(theme+'-Unity.png'))
    poses.save(folder/'unity-motion-contact-sheet.png')
    return report,records
def movies(records):
    checks=[];folder=DEST/'previews';fps=24;ranges=clip_ranges()
    for theme,definition in THEMES.items():
        frames=OUT/'unity'/(theme+'-Timeline');paths=sorted(frames.glob('*.png'));assert len(paths)==368 and paths[-1].stem=='0367'
        chars=[c for c in records if c['theme']==theme];target=folder/(theme+'-motions.mp4')
        command=['ffmpeg','-hide_banner','-loglevel','error','-y','-f','rawvideo','-pix_fmt','rgb24','-s','1280x720','-r',str(fps),'-i','-','-an','-c:v','libx264','-preset','medium','-crf','18','-pix_fmt','yuv420p','-movflags','+faststart',str(target)]
        process=subprocess.Popen(command,stdin=subprocess.PIPE);reference=None;max_static=0;motion_samples=[]
        try:
            for index,path in enumerate(paths):
                assert path.stem==f'{index:04}'
                img=Image.open(path).convert('RGB');assert img.size==(1280,720);raw=np.asarray(img);patch=raw[10:100,10:100].astype(np.int16)
                if reference is None:reference=patch.copy()
                max_static=max(max_static,int(np.abs(patch-reference).max()))
                if index in (55,72,112,125,186,208):motion_samples.append(raw[210:510].copy())
                draw=ImageDraw.Draw(img);draw.text((42,38),definition['ko'],font=font(34),fill='#263247')
                clip=next(c for c in ranges if c['first']<=index+1<=c['last']);step=ranges.index(clip)+1
                draw.text((44,102),f'{step:02} / 08   '+LABELS[clip['name']]+' · '+clip['name'],font=font(23),fill='#465367')
                draw.line((44,156,1236,156),fill='#c0cbd3',width=2)
                for i,c in enumerate(chars):
                    x=155+i*243;draw.text((x,533),c['ko'],font=font(24),fill='#263247',anchor='mm');draw.text((x,569),c['role'],font=font(16),fill='#465367',anchor='mm')
                draw.text((44,664),'Unity 6 · Generic rig · 8 animation clips · in-place',font=font(17),fill='#465367')
                process.stdin.write(img.tobytes())
        finally:process.stdin.close()
        assert process.wait()==0;assert max_static==0,(theme,'background flicker',max_static)
        movement=float(np.abs(motion_samples[0].astype(float)-motion_samples[1]).mean());assert movement>.1
        probe=json.loads(subprocess.check_output(['ffprobe','-v','error','-count_frames','-show_entries','stream=codec_name,width,height,r_frame_rate,nb_read_frames:format=duration','-of','json',str(target)],text=True))
        stream=probe['streams'][0];assert stream['codec_name']=='h264' and int(stream['nb_read_frames'])==368 and stream['r_frame_rate']=='24/1'
        subprocess.run(['ffmpeg','-v','error','-i',str(target),'-f','null','-'],check=True)
        checks.append({'theme':theme,'path':target.relative_to(ROOT).as_posix(),'sha256':sha(target),'frames':368,'fps':24,'duration':float(probe['format']['duration']),'static_roi_max_delta':max_static,'walk_frame_mae':movement,'full_decode':True})
        print(json.dumps(checks[-1],ensure_ascii=False),flush=True)
    write(OUT/'movie-verification.json',{'ok':True,'videos':checks})
def copy_unity(project):
    for relative in ('Assets/StorybookCast','Assets/Scripts/StorybookCast'):
        source=project/relative;target=DEST/'unity'/relative;assert source.is_dir();shutil.copytree(source,target,dirs_exist_ok=True)
        if source.with_suffix('.meta').exists():shutil.copy2(source.with_suffix('.meta'),target.with_suffix('.meta'))
def readme(records):
    rows=['| 주제 | 이름 / 파일 키 | 캐릭터 |','|---|---|---|']
    for c in records:rows.append(f"| {THEMES[c['theme']]['ko']} | {c['ko']} / `{c['key']}` | {c['role']} |")
    counts=[c['vertices'] for c in records];bones=[c['bones'] for c in records]
    text=f'''# 이야기 친구들 20종 — Blender / Unity 모델 팩 v001

2026-10-06 제작. 숲속 우체국, 한입 디저트 마을, 꼬마 우주 정비소, 바닷속 작은 구조대 각각 5종. 외부 모델·텍스처·폰트 자산 없이 절차적으로 만든 모델입니다. 이전 날씨 요정 파일은 이 묶음에 포함하지 않습니다.

![20종 미리보기](previews/all-20-characters.png)

## 가장 빠른 Unity 사용법

1. Unity 6의 **URP 프로젝트**에서 `Assets → Import Package → Custom Package`로 `StorybookCast-Unity6-URP-v001.unitypackage`를 불러옵니다. 필요한 주제만 사용할 때는 `Forest-Unity6-URP-v001.unitypackage` 등 주제별 파일을 가져옵니다. 주제별 패키지는 같은 공통 스크립트 GUID를 공유하므로 함께 설치할 수 있습니다.
2. `Assets/StorybookCast/Themes/<주제>/Scenes/<주제>Showcase.unity`를 열고 ▶ Play를 누릅니다. 그 주제의 다섯 캐릭터가 8개 동작을 순서대로 보여 줍니다.
3. 내 장면에서는 `.../<주제>/Prefabs/<파일 키>.prefab`을 Hierarchy에 끌어 놓습니다. 재질과 Animator가 이미 연결되어 있습니다.
4. Play 중 캐릭터의 **Storybook Character → Motion**을 바꾸거나 코드에서 `character.Play(StorybookCast.CastMotion.Walk);`를 호출합니다. 시연 Scene에서 직접 조작할 때는 `Storybook Motion Demo → Auto Cycle`을 먼저 끕니다.
5. 표정을 직접 바꾸려면 **Manual Face**를 켠 뒤 Blink / Smile / Surprise를 0~1로 조절합니다. 꺼져 있으면 각 동작에 포함된 표정을 사용합니다. Surprise가 커질수록 Smile은 자동으로 줄어듭니다.

모델은 **Generic** 리그입니다. Humanoid Avatar로 변경하지 마세요. 이동 애니메이션은 **제자리 동작**이며 실제 전진은 게임 코드의 Transform/CharacterController/NavMesh 이동과 함께 사용합니다. 정면은 Unity **−Z**, 위는 +Y, 발/꼬리 바닥 기준은 Y=0입니다. +Z 이동 규칙을 쓰는 게임은 Prefab의 자식 모델만 Y축 180° 회전한 부모를 만들어 사용하세요. 모델 높이는 약 2~3 단위이므로 부모 Transform으로 용도에 맞게 함께 축소할 수 있습니다.

## 포함 동작 — 20종 × 8개 = 160개 클립

| 클립 | 의미 | 길이 | 반복 / 연결 |
|---|---|---|---|
| Idle | 대기·숨쉬기 | 2초 | 반복 |
| Walk | 걷기 | 2초 | 반복 |
| Run | 달리기 | 2초 | 반복 |
| SitDown | 앉기 | 1.5초 | SitIdle로 자동 연결 |
| SitIdle | 앉아서 쉬기 | 2초 | 반복 |
| StandUp | 일어나기 | 1.5초 | Idle로 자동 연결 |
| Wave | 손 흔들어 인사 | 2초 | Idle로 자동 연결 |
| Celebrate | 기뻐하기 | 2초 | Idle로 자동 연결 |

복어 **보바**와 해마 **하니**의 Walk/Run은 느린/빠른 **헤엄**입니다. 앉기는 몸을 낮추는 휴식 자세이며, 해마는 긴 몸을 낮추고 꼬리로 지탱합니다. 각 캐릭터의 귀·꼬리·촉수·안테나·장식도 해당 뼈를 따라 움직입니다. 데모 영상은 약 15.33초/24fps/1280×720, 무음입니다. Scene의 자동 시연은 18초 순환합니다.

## 파일 구성

- `<주제>/blender/<파일 키>.blend`: 캐릭터 1명만 있는 독립 Blender 원본. 하나의 Armature, 하나의 스킨 메시, 8개 개별 Action과 내보내기용 AllMotions Action을 포함합니다.
- `unity/Assets/StorybookCast/Themes/<주제>/Models/<파일 키>.fbx`: 캐릭터별 Unity 호환 모델과 베이크된 뼈/표정 애니메이션.
- `unity/Assets/.../Prefabs`, `Controllers`, `Materials`, `Scenes`: 연결을 마친 Unity 자산과 `.meta`.
- `unity/Assets/Scripts/StorybookCast`: 런타임 캐릭터/시연 컴포넌트, Editor 반입·검증 도구.
- `previews/`: 20종 개별 PNG, 전체 목록, Unity 미리보기와 주제별 동작 MP4.
- `<주제>-Models-v001.zip`: 해당 주제의 Blender 5개, FBX 5개, Unity 패키지, 미리보기, 이 사용법.
- `SHA256SUMS.json`: 전달 파일 무결성 목록. ZIP 자체는 ZIP 안에 중복 포함하지 않습니다.

Unity 패키지에 포함된 `.meta`를 유지해야 클립 범위·재질·Prefab 참조가 보존됩니다. `unity/Assets`를 복사하는 방식도 가능하지만 기존 동일 경로 자산을 수정한 프로젝트에서는 백업 후 병합하세요. FBX 하나만 가져오면 한 개의 긴 Take가 보일 수 있습니다. Model Importer의 Animation에서 아래 프레임으로 분할하거나 포함된 패키지를 사용하세요. `Tools → Storybook Cast → Prepare Imported Themes`는 존재하는 주제의 모델 반입 설정과 Prefab/Animator를 재구성하는 편집 도구입니다.

| 클립 | FBX 범위(Blender 24fps, 시작 프레임 1 기준) |
|---|---|
'''
    for c in clip_ranges():text+=f"| {c['name']} | {c['first']}–{c['last']} |\n"
    text+='''
Unity Importer가 첫 프레임을 0으로 표시하는 경우 각 숫자에서 1을 빼세요. 포함 Editor 설정은 실제 Take의 firstFrame을 읽어 이 차이를 자동 처리합니다.

## Blender에서 다시 편집하기

Blender 5.2.1 LTS에서 검증했습니다. 각 `.blend`를 열면 Idle의 1프레임, Pose Mode, CTRL_Body 선택 상태입니다. `CTRL_Hand.L/R`와 `CTRL_Foot.L/R`은 2관절 IK, `CTRL_Body`와 `CTRL_Head`는 몸/머리, `CTRL_Face`의 사용자 속성은 표정입니다. Extras Bone Collection에서 귀·꼬리 등 추가 뼈를 조절합니다. Action Editor에서 해당 캐릭터의 Idle / Walk / Run / SitDown / SitIdle / StandUp / Wave / Celebrate를 골라 수정하세요. 원본을 보존하려면 새 버전으로 저장합니다.

Blender의 IK 제약과 표정 driver는 **원본 파일에 유지**되어 있습니다. Unity에서는 평가한 결과를 애니메이션으로 재생합니다. Unity 실시간 IK solver, Humanoid 리타게팅, 이동/충돌/게임플레이 로직은 이 모델 팩에 포함하지 않습니다.

## 제작 목록

'''+ '\n'.join(rows)+f'''

## 검증과 사용 범위

- 20개 원본 독립 재개방, 캐릭터당 1 스킨 메시 / 3 얼굴 ShapeKey / {min(bones)}~{max(bones)}뼈 / {min(counts):,}~{max(counts):,}원본 정점. FBX 반입에서는 재질·법선 경계의 정점 분리로 수가 늘 수 있습니다.
- 가중치 정규화, 누락 뼈·외부 의존 없음, driver 유효, 바닥/반복 연결/실제 보행 변형/앉은 높이 변화 확인.
- Unity **6000.3.25f1 / URP 17.3.0 / Windows**에서 20개 Generic Avatar, 160개 클립, URP 재질을 검사했습니다. 실제 Play Mode의 160개 상태 전환, 스킨 변형, SitDown→SitIdle, 표정 수동 제어도 확인했습니다.
- LOD, 모바일 성능 최적화, 다른 Unity 버전·Built-in/HDRP·기기 빌드는 별도 검증이 필요합니다. 모델당 여러 색상 재질을 쓰므로 대량 배치에는 재질 아틀라스/LOD 작업을 권합니다.
- 절차형 부품 메시를 하나의 스킨 메시로 합친 캐릭터입니다. 3D 프린팅용 수밀/단일 연속 표면 모델은 아닙니다.

제작 소스와 검증 기록: 저장소 `workflows/storybook-cast/`, `outputs/storybook-cast/v001/`. 이 사용법의 경로는 이 전달 폴더를 기준으로 합니다.
'''
    (DEST/'README.md').write_text(text,encoding='utf-8')
def package_checks():
    results=[]
    for name in list(THEMES)+['StorybookCast']:
        path=DEST/(name+'-Unity6-URP-v001.unitypackage');assert path.is_file();checked=0;asset_paths=[]
        with tarfile.open(path,'r:gz') as tar:
            members={m.name:m for m in tar.getmembers()}
            for name2,member in members.items():
                if not name2.endswith('/pathname'):continue
                asset=tar.extractfile(member).read().decode('utf-8').rstrip('\0\r\n');prefix=name2.rsplit('/',1)[0];stored=members.get(prefix+'/asset');asset_paths.append(asset)
                assert asset.startswith(('Assets/StorybookCast','Assets/Scripts/StorybookCast')),asset
                if stored and stored.isfile():assert tar.extractfile(stored).read()==(DEST/'unity'/asset).read_bytes(),asset;checked+=1
                meta=members.get(prefix+'/asset.meta')
                if meta:assert tar.extractfile(meta).read()==(DEST/'unity'/(asset+'.meta')).read_bytes(),asset+' meta'
        count=sum(x.endswith('.fbx') for x in asset_paths);assert count==(20 if name=='StorybookCast' else 5)
        results.append({'name':path.name,'bytes':path.stat().st_size,'sha256':sha(path),'assets_verified':checked,'fbx':count})
    write(OUT/'unitypackage-verification.json',{'ok':True,'packages':results})
def zips(records):
    results=[]
    for theme in THEMES:
        files=[DEST/'README.md',DEST/(theme+'-Unity6-URP-v001.unitypackage'),DEST/'previews'/'all-20-characters.png',DEST/'previews'/(theme+'-motions.mp4'),DEST/'previews'/(theme+'-Unity.png')]
        for c in records:
            if c['theme']==theme:files.extend([ROOT/c['native'],ROOT/c['fbx'],DEST/'previews'/(c['key']+'.png')])
        target=DEST/(theme+'-Models-v001.zip')
        with zipfile.ZipFile(target,'w',zipfile.ZIP_DEFLATED,compresslevel=6) as archive:
            for path in files:archive.write(path,path.relative_to(DEST).as_posix())
        with zipfile.ZipFile(target) as archive:
            assert archive.testzip() is None
            for name in archive.namelist():assert archive.read(name)==(DEST/name).read_bytes()
        results.append({'path':target.name,'bytes':target.stat().st_size,'sha256':sha(target),'files':len(files),'crc_ok':True})
    write(OUT/'zip-verification.json',{'ok':True,'packages':results})
def final_checks(records,report):
    native=json.loads((OUT/'native-verification.json').read_text(encoding='utf-8'));assert native['ok'] and len(native['characters'])==20
    live=json.loads((OUT/'unity-runtime-verification.json').read_text(encoding='utf-8'));assert live['ok'] and len(live['characters'])==20
    for theme in THEMES:
        check=json.loads((OUT/(theme+'-unity-verification.json')).read_text(encoding='utf-8'));assert check['ok'] and len(check['characters'])==5
    for c in records:
        assert sha(ROOT/c['native'])==c['native_sha256'];assert sha(ROOT/c['fbx'])==c['fbx_sha256']
    preserved=report['preserved_sources']
    for path,digest in preserved.items():
        assert sha(ROOT/path)==digest,path
    files=[p for p in DEST.rglob('*') if p.is_file() and not p.name.endswith(('.blend1','.blend2')) and p.name!='SHA256SUMS.json']
    assert max(p.stat().st_size for p in files)<100*1024*1024
    hashes={p.relative_to(DEST).as_posix():sha(p) for p in files};write(DEST/'SHA256SUMS.json',hashes)
    write(OUT/'delivery-verification.json',{'ok':True,'characters':20,'native':20,'fbx':20,'prefabs':20,'controllers':20,'clips':160,'scene_files':4,'files':len(files),'preserved_sources':len(preserved),'largest_file_bytes':max(p.stat().st_size for p in files),'hash_manifest_sha256':sha(DEST/'SHA256SUMS.json')})
def main():
    parser=argparse.ArgumentParser();parser.add_argument('--unity-project',type=Path,required=True);parser.add_argument('--prepare',action='store_true');args=parser.parse_args()
    copy_unity(args.unity_project);report,records=previews();readme(records)
    if args.prepare:movies(records)
    else:package_checks();zips(records);final_checks(records,report)
    print(json.dumps({'ok':True,'prepare':args.prepare,'delivery':str(DEST)},ensure_ascii=False))
if __name__=='__main__':main()
