"""Run immutable predecessor and LC009 tests in disposable dependency trees."""
import datetime
import json
from pathlib import Path
import platform
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT / 'src'))
from bootstrap import resolve, PARENT_SHA256


def main():
    (ROOT / 'results').mkdir(exist_ok=True)
    with tempfile.TemporaryDirectory(prefix='lc009-suite-') as work:
        parent, manifests = resolve(work)
        predecessor = subprocess.run([sys.executable, 'run_all.py'], cwd=parent,
                                     capture_output=True, text=True, timeout=180)
        (ROOT / 'results' / 'predecessor_fresh.log').write_text(predecessor.stdout + predecessor.stderr)
        if predecessor.returncode:
            raise RuntimeError('LC008 predecessor failed: ' + predecessor.stderr[-3000:])
        parent_receipt = json.loads((parent / 'results' / 'execution_receipt.json').read_text())
        suite = unittest.defaultTestLoader.discover(str(ROOT / 'tests'), pattern='test_*.py')
        with (ROOT / 'results' / 'tests.log').open('w') as log:
            result = unittest.TextTestRunner(stream=log, verbosity=2).run(suite)
        receipt = {
            'experiment': ROOT.name,
            'execution_utc': datetime.datetime.now(datetime.timezone.utc).isoformat(),
            'python': platform.python_version(), 'platform': platform.platform(),
            'predecessor_sha256': PARENT_SHA256, 'dependency_manifest_entries': manifests,
            'predecessor_receipt': parent_receipt,
            'tests': result.testsRun, 'failures': len(result.failures),
            'errors': len(result.errors), 'passed': result.wasSuccessful(),
            'claim_ceiling': 'bounded fixed-query append relation and scoped supplied commitment matches; no authentication, method qualification or performance advantage'}
        (ROOT / 'results' / 'execution_receipt.json').write_text(json.dumps(receipt, indent=2, sort_keys=True) + '\n')
        print((ROOT / 'results' / 'tests.log').read_text())
        print(json.dumps(receipt, indent=2, sort_keys=True))
        return 0 if result.wasSuccessful() else 1


if __name__ == '__main__':
    sys.exit(main())