"""브리찌: v002의 20개 모델과 수정된 어깨 동작을 개별 저장."""
import sys,importlib
sys.path.insert(0,str(PROJECT_ROOT/'workflows/storybook-cast'))
import motions,exporting
importlib.reload(motions);importlib.reload(exporting)
from catalog import THEMES
for theme in THEMES:exporting.export_theme(PROJECT_ROOT,theme,version='v002')
