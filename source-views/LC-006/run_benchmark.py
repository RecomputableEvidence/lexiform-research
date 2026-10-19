from pathlib import Path
import tempfile,zipfile,sys,hashlib,subprocess
ROOT=Path(__file__).resolve().parent
p=ROOT/'history'/'LC-EXP-005-LAZY-COMPOSITION-001.zip'
assert hashlib.sha256(p.read_bytes()).hexdigest()=='c51ee49b709fe4bca705a058b37eac7ac155a6e322d8d78e3a5e0c24d4124791'
with tempfile.TemporaryDirectory(prefix='lc006-bench-') as t:
    root=Path(t)
    with zipfile.ZipFile(p) as z:
        for n in z.namelist():
            pp=Path(n)
            if pp.is_absolute() or '..' in pp.parts:raise ValueError('unsafe path')
        z.extractall(root)
    pred=root/'LC-EXP-005-LAZY-COMPOSITION-001'
    subprocess.run([sys.executable,str(pred/'run_all.py')],cwd=pred,stdout=subprocess.DEVNULL,check=True)
    sys.path[:0]=[str(pred/'history_003_extracted'/'LC-EXP-003'/'src'),str(pred/'src'),str(ROOT/'src')]
    import os
    os.environ['LC006_PREDECESSOR_ROOT']=str(pred)
    from benchmark_006 import main
    main()
