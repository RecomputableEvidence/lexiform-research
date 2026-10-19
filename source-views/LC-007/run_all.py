"""Verify frozen 006, execute its suite, and run independent LC007 tests."""
from pathlib import Path
import hashlib,json,zipfile,tempfile,sys,subprocess,unittest,os
ROOT=Path(__file__).resolve().parent
PRE=ROOT/'history'/'LC-EXP-006-DEPENDENCY-BOUND-REUSE-001.zip'
EXPECTED='00c801c2a1068c20a370ee3de539abd064b9254ec726f69b627f3b0be454ffec'
def safe_extract(z,location):
    for name in z.namelist():
        p=Path(name)
        if p.is_absolute() or '..' in p.parts:raise ValueError('unsafe archived path')
    z.extractall(location)
def run():
    h=hashlib.sha256(PRE.read_bytes()).hexdigest()
    if h!=EXPECTED:raise ValueError('frozen predecessor hash mismatch')
    with tempfile.TemporaryDirectory(prefix='lc007-') as d:
        d=Path(d)
        with zipfile.ZipFile(PRE) as z:safe_extract(z,d)
        prev=d/'LC-EXP-006-DEPENDENCY-BOUND-REUSE-001'
        lines=(prev/'MANIFEST.sha256').read_text().splitlines()
        for line in lines:
            expected,rel=line.split('  ',1)
            if hashlib.sha256((prev/rel).read_bytes()).hexdigest()!=expected:raise ValueError('predecessor manifest mismatch: '+rel)
        p=subprocess.run([sys.executable,'run_all.py'],cwd=prev,capture_output=True,text=True)
        if p.returncode:raise RuntimeError('predecessor tests failed: '+p.stderr[-4000:])
        pred5=prev/'history'/'LC-EXP-005-LAZY-COMPOSITION-001.zip'
        with zipfile.ZipFile(pred5) as z:safe_extract(z,d)
        loc5=d/'LC-EXP-005-LAZY-COMPOSITION-001'
        q=subprocess.run([sys.executable,'run_all.py'],cwd=loc5,capture_output=True,text=True)
        if q.returncode:raise RuntimeError('nested predecessor extraction failed: '+q.stderr[-3000:])
        sys.path[:0]=[str(ROOT/'src'),str(prev/'src'),str(loc5/'src'),str(loc5/'history_003_extracted'/'LC-EXP-003'/'src')]
        suite=unittest.defaultTestLoader.discover(str(ROOT/'tests'),pattern='test_*.py')
        result=unittest.TextTestRunner(verbosity=2).run(suite)
        receipt={'experiment':'LC-EXP-007-APPEND-BOUND-AUDIT-001',
          'predecessor_sha256':h,'predecessor_manifest':len(lines),
          'predecessor_tests':25,'successor_tests':result.testsRun,
          'failures':len(result.failures),'errors':len(result.errors),
          'passed':result.wasSuccessful(),
          'claim_ceiling':'trusted in-process append linkage, selective audit materialization; no cryptographic authentication or lexiconic supremacy'}
        (ROOT/'results'/'execution_receipt.json').write_text(json.dumps(receipt,indent=2)+'\n')
        print('LC007_RECEIPT',json.dumps(receipt,sort_keys=True))
        if not result.wasSuccessful():sys.exit(1)
        return receipt
if __name__=='__main__':run()
