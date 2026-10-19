"""Verifies nested predecessor from frozen ZIP in disposable directory, then successor."""
from pathlib import Path
import sys,json,hashlib,zipfile,tempfile,subprocess,unittest
ROOT=Path(__file__).resolve().parent
HISTORY=ROOT/'history'/'LC-EXP-005-LAZY-COMPOSITION-001.zip'
EXPECTED='c51ee49b709fe4bca705a058b37eac7ac155a6e322d8d78e3a5e0c24d4124791'
def run():
    got=hashlib.sha256(HISTORY.read_bytes()).hexdigest()
    if got!=EXPECTED:raise RuntimeError('predecessor identity mismatch')
    with tempfile.TemporaryDirectory(prefix='lc006-') as temp:
        location=Path(temp)
        with zipfile.ZipFile(HISTORY) as z:
            for name in z.namelist():
                p=Path(name)
                if p.is_absolute() or '..' in p.parts:raise ValueError('unsafe path')
            z.extractall(location)
        pred=location/'LC-EXP-005-LAZY-COMPOSITION-001'
        manifest=(pred/'MANIFEST.sha256').read_text().splitlines()
        for entry in manifest:
            expected,relative=entry.split('  ',1)
            actual=hashlib.sha256((pred/relative).read_bytes()).hexdigest()
            if actual!=expected:raise RuntimeError('predecessor manifest failure '+relative)
        subprocess.run([sys.executable,str(pred/'run_all.py')],cwd=pred,check=True)
        sys.path.insert(0,str(pred/'history_003_extracted'/'LC-EXP-003'/'src'))
        sys.path.insert(0,str(pred/'src'))
        sys.path.insert(0,str(ROOT/'src'))
        import os
        os.environ['LC006_PREDECESSOR_ROOT']=str(pred)
        suite=unittest.defaultTestLoader.discover(str(ROOT/'tests'),pattern='test_*.py')
        result=unittest.TextTestRunner(verbosity=2).run(suite)
        receipt={'id':'LC-EXP-006-DEPENDENCY-BOUND-REUSE-001',
                 'predecessor_sha256':got,'predecessor_test_groups':13,
                 'successor_test_groups':result.testsRun,'failures':len(result.failures),
                 'errors':len(result.errors),'passed':result.wasSuccessful(),
                 'claim_ceiling':'bounded append-only selective recomputation; no unique lexiconic advantage'}
        print('LC006_RECEIPT',json.dumps(receipt,sort_keys=True))
        if not result.wasSuccessful():sys.exit(1)
        return receipt
if __name__=='__main__':run()
