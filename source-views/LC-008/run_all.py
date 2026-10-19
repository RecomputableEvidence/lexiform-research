"""Verify frozen predecessors and run LC008 tests, retaining original archived history."""
import hashlib,json,subprocess,sys,tempfile,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parent
sys.path.insert(0,str(ROOT/'src'))
from dependencies import load_dependency_paths,PARENT_SHA256


def main():
    with tempfile.TemporaryDirectory(prefix='lc008-all-') as directory:
        manifests=load_dependency_paths(directory)
        # Run frozen predecessor code in a disposable extracted copy, not in the original archive.
        prev=Path(directory)/'LC-EXP-007-APPEND-BOUND-AUDIT-001'
        p=subprocess.run([sys.executable,'run_all.py'],cwd=prev,capture_output=True,text=True,
                         timeout=120)
        if p.returncode:
            raise RuntimeError('predecessor LC007 tests failed: '+p.stderr[-3000:])
        suite=unittest.defaultTestLoader.discover(str(ROOT/'tests'),pattern='test_*.py')
        result=unittest.TextTestRunner(verbosity=2).run(suite)
        receipt={'experiment':'LC-EXP-008-PORTABLE-AUDIT-001','predecessor_sha256':PARENT_SHA256,
                 'predecessor_manifest_entries':manifests,
                 'predecessor_007_test_groups':10,'predecessor_inherited_test_groups':25,
                 'successor_test_groups':result.testsRun,'failures':len(result.failures),
                 'errors':len(result.errors),'passed':result.wasSuccessful(),
                 'claim_ceiling':'portable, full-replay-consistent declared evidence and witnesses; neither externally authenticated truth nor compact recovery'}
        (ROOT/'results'/'execution_receipt.json').write_text(json.dumps(receipt,indent=2,sort_keys=True)+'\n')
        print('LC008_RECEIPT',json.dumps(receipt,sort_keys=True))
        if not result.wasSuccessful():return 1
    return 0
if __name__=='__main__':sys.exit(main())
