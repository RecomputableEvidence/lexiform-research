"""Run copied LC012 tests plus LC013 targeted tests in the same isolated successor tree."""
from pathlib import Path
import json,sys,time,unittest
root=Path(__file__).resolve().parent
suite=unittest.defaultTestLoader.discover(str(root/'tests'),pattern='test_*.py')
t=time.perf_counter();result=unittest.TextTestRunner(verbosity=2).run(suite)
r={'suite':'LC-EXP-013','tests_run':result.testsRun,'failures':len(result.failures),
   'errors':len(result.errors),'skipped':len(result.skipped),'passed':result.wasSuccessful(),
   'seconds':round(time.perf_counter()-t,3)}
(root/'results'/'test_results_latest.json').write_text(json.dumps(r,indent=2)+'\n')
print('LC013 EXECUTION RECEIPT',json.dumps(r,sort_keys=True))
sys.exit(0 if result.wasSuccessful() else 1)
