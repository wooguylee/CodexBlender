"""브리찌: 20종 어깨를 체형에 연결한 별도 v002 Scene 제작."""
import sys,importlib,runpy
sys.path.insert(0,str(PROJECT_ROOT/'workflows/storybook-cast'))
import geometry,rigging
importlib.reload(geometry);importlib.reload(rigging)
runpy.run_path(str(PROJECT_ROOT/'workflows/storybook-cast/01_build_models.py'),init_globals={'PROJECT_ROOT':PROJECT_ROOT,'bpy':bpy,'VERSION':'v002','ATTACH_SHOULDERS':True})
