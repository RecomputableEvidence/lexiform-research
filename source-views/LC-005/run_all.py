"""No predecessor mutation; install only Python standard library for candidate."""
from pathlib import Path
import hashlib,json,sys,unittest,zipfile,shutil
ROOT=Path(__file__).resolve().parent
PRED=ROOT/'history'/'LC-EXP-004-DESCRIPTOR-PRESSURE-001.zip'
FREEZE=ROOT/'history'/'predecessor_sha256.txt'
TARGET=ROOT/'history_extracted'
def run():
    digest=hashlib.sha256(PRED.read_bytes()).hexdigest()
    if digest!=FREEZE.read_text().strip():raise RuntimeError('predecessor mismatch')
    if TARGET.exists():shutil.rmtree(TARGET)
    TARGET.mkdir()
    with zipfile.ZipFile(PRED) as z:
        for n in z.namelist():
            p=Path(n)
            if p.is_absolute() or '..' in p.parts:raise ValueError('unsafe predecessor path')
        z.extractall(TARGET)
    nested=TARGET/'LC-EXP-004-DESCRIPTOR-PRESSURE-001'/'history'/'LC-EXP-003-EVIDENCE-BOUND-EXECUTED.zip'
    nested_expected=(TARGET/'LC-EXP-004-DESCRIPTOR-PRESSURE-001'/'history'/'predecessor_sha256.txt').read_text().strip()
    if hashlib.sha256(nested.read_bytes()).hexdigest()!=nested_expected:raise RuntimeError('embedded 003 mismatch')
    inner=ROOT/'history_003_extracted'
    if inner.exists():shutil.rmtree(inner)
    inner.mkdir()
    with zipfile.ZipFile(nested) as z:
        for n in z.namelist():
            p=Path(n)
            if p.is_absolute() or '..' in p.parts:raise ValueError('unsafe nested predecessor path')
        z.extractall(inner)
    sys.path.insert(0,str(inner/'LC-EXP-003'/'src'))
    sys.path.insert(0,str(ROOT/'src'))
    suite=unittest.defaultTestLoader.discover(str(ROOT/'tests'))
    runner=unittest.TextTestRunner(verbosity=2)
    res=runner.run(suite)
    receipt={'id':'LC-EXP-005-LAZY-COMPOSITION-001','predecessor_004_sha256':digest,
             'embedded_003_sha256':nested_expected,'test_count':res.testsRun,
             'failures':len(res.failures),'errors':len(res.errors),'pass':res.wasSuccessful(),
             'claim_ceiling':'bounded lazy symbolic DAG; no semantic emergence or speed supremacy'}
    (ROOT/'results'/'execution_receipt.json').write_text(json.dumps(receipt,indent=2)+'\n')
    print(json.dumps(receipt,indent=2))
    if not res.wasSuccessful():sys.exit(1)
if __name__=='__main__':run()
