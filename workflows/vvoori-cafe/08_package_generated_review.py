"""AI 생성 이미지 버전의 240장 검증과 MP4 패키징. 일반 Python에서 실행."""
from pathlib import Path
import runpy
runpy.run_path(str(Path(__file__).with_name('03_package_verify.py')), init_globals={'VERSION': 'v002'})
