"""첫 렌더를 보존하고 Clip 경계 수정본을 전체 재렌더. 이 회복 스크립트는 1회 실행."""
from pathlib import Path
import shutil,json
out=PROJECT_ROOT/'outputs/vvoori-cafe-winter/v001'
assert json.loads((out/'edge-fix-verification.json').read_text())['ok']
frames=out/'master-frames';retained=out/'initial-frames-before-edge-fix'
assert frames.resolve().parent==out.resolve() and retained.resolve().parent==out.resolve()
assert not retained.exists() and len(list(frames.glob('*.png')))==480
frames.rename(retained)
source=PROJECT_ROOT/'scenes/vvoori-cafe-winter-v001.blend'
prior=out/'source-before-edge-fix.blend';assert not prior.exists()
source.rename(prior)
code=(PROJECT_ROOT/'workflows/vvoori-cafe-winter/03_render_master.py').read_text(encoding='utf-8')
exec(compile(code,'03_render_master.py','exec'),globals())
