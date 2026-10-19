#!/usr/bin/env python3
"""Re-run one archived experiment in disposable extraction; no source archive mutation."""
import argparse
import json
import subprocess
import sys
import tempfile
import zipfile
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]

def main():
    ap=argparse.ArgumentParser(description='Explicit per-experiment reproduction, stdlib Python')
    ap.add_argument('--experiment',required=True,choices=[f'LC-EXP-{i:03}' for i in range(1,14)])
    ap.add_argument('--timeout',type=int,default=90)
    args=ap.parse_args()
    reg=json.loads((ROOT/'registry'/'experiments.json').read_text())
    item=next(x for x in reg['experiments'] if x['experiment_id']==args.experiment)
    with tempfile.TemporaryDirectory(prefix='lexiform-replay-') as temp:
        tempdir=Path(temp)
        with zipfile.ZipFile(ROOT/item['archive_path']) as z:
            for info in z.infolist():
                rel=Path(info.filename)
                if rel.is_absolute() or '..' in rel.parts:raise ValueError('unsafe ZIP path')
                dest=tempdir/rel
                if info.is_dir():dest.mkdir(exist_ok=True);continue
                dest.parent.mkdir(parents=True,exist_ok=True)
                dest.write_bytes(z.read(info))
        roots=[p.parent for p in tempdir.glob('*/MANIFEST.sha256')]
        if len(roots)!=1:raise RuntimeError('expected exactly one archive root')
        cwd=roots[0]
        steps=[]
        if (cwd/'verify_manifest.py').exists():steps.append([sys.executable,'verify_manifest.py'])
        if (cwd/'run_all.py').exists():steps.append([sys.executable,'run_all.py'])
        elif (cwd/'tests').exists():steps.append([sys.executable,'-m','unittest','discover','-s','tests','-p','test_*.py','-v'])
        if not steps:raise RuntimeError('no known standard test entrypoint in archive')
        for step in steps:
            print('EXECUTE',step,'within disposable temp extraction',flush=True)
            p=subprocess.run(step,cwd=cwd,text=True,stdout=subprocess.PIPE,stderr=subprocess.STDOUT,timeout=args.timeout,env={'PATH': __import__('os').environ.get('PATH',''),'PYTHONPATH':str(cwd)})
            print(p.stdout[-12000:])
            if p.returncode:print('FAILED',p.returncode);return p.returncode
        print('REPLAY_COMMANDS_PASSED; result scope limited to the entrypoints run')
        return 0
if __name__=='__main__':sys.exit(main())
