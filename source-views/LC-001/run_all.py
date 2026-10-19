"""Cross-platform offline LC-EXP-001 runner; calls all three shipped experiments."""
import json, subprocess, sys
from pathlib import Path
ROOT=Path(__file__).resolve().parent
SCRIPTS=['tests/test_conformance.py','src/experiment.py','src/benchmark.py']
for target in SCRIPTS:
    print('RUN:',target,flush=True)
    proc=subprocess.run([sys.executable,str(ROOT/target)],cwd=ROOT)
    if proc.returncode:
        sys.exit(proc.returncode)
print('COMPLETED: tests, episode, benchmark. Reports are in results/.')
