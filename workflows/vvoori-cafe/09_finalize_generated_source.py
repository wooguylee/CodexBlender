"""AI 생성 이미지 버전의 독립 Blender 원본 검증 및 정상 파일 저장."""
from pathlib import Path
import runpy
runpy.run_path(str(Path(__file__).with_name('04_finalize_and_verify_source.py')), init_globals={'VERSION': 'v002'})
