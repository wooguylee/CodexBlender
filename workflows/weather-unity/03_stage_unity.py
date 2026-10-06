"""새 전용 경로로 Unity 모델/스크립트를 복사한다. 임의 프로젝트 파일은 덮어쓰지 않는다."""
from pathlib import Path
import argparse,shutil
root=Path(__file__).resolve().parents[2]
parser=argparse.ArgumentParser();parser.add_argument('--project',required=True);args=parser.parse_args()
project=Path(args.project).resolve();assert (project/'ProjectSettings/ProjectVersion.txt').is_file()
delivery=root/'exports/weather-fairies/v001/unity'
scripts=delivery/'Assets/Scripts/WeatherFairies';scripts.mkdir(parents=True,exist_ok=True)
for file in (root/'workflows/weather-unity/Unity').rglob('*.cs'):
    dest=scripts/file.relative_to(root/'workflows/weather-unity/Unity');dest.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(file,dest)
for relative in ['Assets/WeatherFairies','Assets/Scripts/WeatherFairies']:
    destination=project/relative;assert not destination.exists(),destination
    shutil.copytree(delivery/relative,destination)
print('Staged scoped WeatherFairies assets in',project)
