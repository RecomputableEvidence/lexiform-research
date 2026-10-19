"""Deterministic test execution, with separate live JSON result outside frozen manifest."""
import json,unittest,sys,time
from pathlib import Path
ROOT=Path(__file__).resolve().parent
suite=unittest.defaultTestLoader.discover(str(ROOT/'tests'),pattern='test_lc012.py')
start=time.perf_counter()
result=unittest.TextTestRunner(verbosity=2).run(suite)
report={'suite':'LC-EXP-012','tests_run':result.testsRun,'failures':len(result.failures),
        'errors':len(result.errors),'skipped':len(result.skipped),'passed':result.wasSuccessful(),
        'seconds':round(time.perf_counter()-start,3)}
(ROOT/'results'/'test_results_latest.json').write_text(json.dumps(report,indent=2)+'\n')
print('LC012 TEST RESULT',json.dumps(report,sort_keys=True))
sys.exit(0 if result.wasSuccessful() else 1)
