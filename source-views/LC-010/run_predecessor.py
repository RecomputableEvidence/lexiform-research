"""Separately run original LC009 inherited suite from a fresh extraction."""
import subprocess
import sys
import tempfile
from pathlib import Path
ROOT=Path(__file__).resolve().parent
sys.path.insert(0,str(ROOT/'src'))
from bootstrap import load_frozen
if __name__=='__main__':
    with tempfile.TemporaryDirectory(prefix='lc010-lc009-') as work:
        parent,_=load_frozen(work)
        result=subprocess.run([sys.executable,'run_all.py'],cwd=parent,timeout=180)
        sys.exit(result.returncode)
