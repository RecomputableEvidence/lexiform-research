"""Run exploratory descriptor pressure against exact embedded frozen predecessor.
Runs tests without altering the predecessor ZIP. Python 3.10+ standard library.
"""
import hashlib
import json
import shutil
import sys
import unittest
import zipfile
from pathlib import Path
ROOT=Path(__file__).resolve().parent
FROZEN=ROOT/'history'/'LC-EXP-003-EVIDENCE-BOUND-EXECUTED.zip'
TARGET=ROOT/'history_extracted'
MANIFEST=ROOT/'history'/'predecessor_sha256.txt'

def run():
    expected=MANIFEST.read_text().strip()
    actual=hashlib.sha256(FROZEN.read_bytes()).hexdigest()
    if actual!=expected:raise RuntimeError('predecessor SHA-256 mismatch')
    if TARGET.exists():shutil.rmtree(TARGET)
    TARGET.mkdir()
    with zipfile.ZipFile(FROZEN) as z:
        for name in z.namelist():
            path=Path(name)
            if path.is_absolute() or '..' in path.parts:raise ValueError('unsafe zip path')
        z.extractall(TARGET)
    sys.path.insert(0,str(TARGET/'LC-EXP-003'/'src'))
    sys.path.insert(0,str(ROOT/'src'))
    suite=unittest.defaultTestLoader.discover(str(ROOT/'tests'),pattern='test_*.py')
    result=unittest.TextTestRunner(verbosity=2).run(suite)
    receipt={'id':'LC-EXP-004-DESCRIPTOR-PRESSURE-001','predecessor_zip_sha256':actual,
             'test_run_count':result.testsRun,'failure_count':len(result.failures),
             'error_count':len(result.errors),'passed':result.wasSuccessful(),
             'claim_ceiling':'candidate bounded symbolic extension, not semantic emergence'}
    (ROOT/'results'/'execution_receipt.json').write_text(json.dumps(receipt,indent=2)+'\n')
    print(json.dumps(receipt,indent=2))
    if not result.wasSuccessful():sys.exit(1)
if __name__=='__main__':run()
