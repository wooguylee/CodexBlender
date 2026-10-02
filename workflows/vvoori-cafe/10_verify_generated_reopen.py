"""최종 AI 이미지 원본의 새 프로세스 재개방 및 실제 렌더 검증."""
from pathlib import Path
import runpy
runpy.run_path(str(Path(__file__).with_name('05_verify_native_reopen.py')), init_globals={'VERSION': 'v002'})
