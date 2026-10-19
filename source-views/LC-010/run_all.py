"""Verify predecessor and execute successor tests; write no frozen files."""
import json
from pathlib import Path
import sys
import tempfile
import unittest

ROOT=Path(__file__).resolve().parent
sys.path.insert(0,str(ROOT/'src'))
from bootstrap import load_frozen
with tempfile.TemporaryDirectory(prefix='lc010-run-') as work:
    _,identities=load_frozen(work)
    from chain_audit import verify_chain
    suite=unittest.defaultTestLoader.discover(str(ROOT/'tests'), pattern='test_*.py')
    result=unittest.TextTestRunner(verbosity=2).run(suite)
    print(json.dumps({'experiment':'LC-EXP-010-RELATIONAL-CONTINUITY-001','test_count':result.testsRun,
            'errors':len(result.errors),'failures':len(result.failures),
            'predecessor_manifests':identities,'passed':result.wasSuccessful()},indent=2))
    sys.exit(0 if result.wasSuccessful() else 1)
