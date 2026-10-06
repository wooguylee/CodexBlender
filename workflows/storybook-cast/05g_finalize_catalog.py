"""브리찌: 부분 재내보내기 후 캐릭터 표준 순서를 복구한다. 모델 재작성 없음."""
import sys,importlib
sys.path.insert(0,str(PROJECT_ROOT/'workflows/storybook-cast'))
import exporting
importlib.reload(exporting)
exporting.export_theme(PROJECT_ROOT,'Sea',version='v002')
