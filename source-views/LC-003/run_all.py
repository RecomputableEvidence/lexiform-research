"""Execute sealed successor tests and benchmark in an extracted writable copy."""
import json
import subprocess
import sys
from pathlib import Path
ROOT=Path(__file__).resolve().parent
OUT=ROOT/'results'
OUT.mkdir(exist_ok=True)
commands=[
    ('tests',[sys.executable,'-m','unittest','discover','-s','tests','-v']),
    ('demonstration',[sys.executable,'src/demo.py']),
    ('benchmark',[sys.executable,'src/benchmark.py']),
]
report={'identity':'LC-EXP-003-COMPLIANCE-RUN-001','python':sys.version.split()[0],'commands':{}}
for name,command in commands:
    result=subprocess.run(command,cwd=ROOT,text=True,capture_output=True)
    (OUT/f'{name}.stdout.log').write_text(result.stdout)
    (OUT/f'{name}.stderr.log').write_text(result.stderr)
    report['commands'][name]={'exit_code':result.returncode,'command':command,'stdout_file':f'{name}.stdout.log','stderr_file':f'{name}.stderr.log'}
    print(name,'exit_code',result.returncode)
    if result.returncode:break
(OUT/'run_receipt.json').write_text(json.dumps(report,indent=2)+'\n')
sys.exit(0 if len(report['commands'])==len(commands) and all(c['exit_code']==0 for c in report['commands'].values()) else 1)
