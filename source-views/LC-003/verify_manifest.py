"""Check each shipped entry in the LC-EXP-003 distribution, without rewriting it."""
import hashlib
from pathlib import Path
ROOT=Path(__file__).resolve().parent
expected={}
for line in (ROOT/'MANIFEST.sha256').read_text(encoding='utf-8').splitlines():
    digest,sep,name=line.partition('  ')
    if not sep or name in expected:raise SystemExit('malformed manifest')
    expected[name]=digest
actual={p.relative_to(ROOT).as_posix():hashlib.sha256(p.read_bytes()).hexdigest()
        for p in ROOT.rglob('*') if p.is_file() and p.name!='MANIFEST.sha256' and '__pycache__' not in p.parts and p.suffix!='.pyc'}
missing=sorted(set(expected)-set(actual));extra=sorted(set(actual)-set(expected))
mismatched=sorted(k for k in set(expected)&set(actual) if expected[k]!=actual[k])
print(f'manifest: {len(expected)} expected, {len(actual)} observed; missing={missing}; extra={extra}; mismatched={mismatched}')
if missing or extra or mismatched:raise SystemExit(1)
