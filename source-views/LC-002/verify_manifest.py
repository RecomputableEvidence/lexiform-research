"""Verify frozen payload files against included SHA-256 manifest (not an external trust anchor)."""
from pathlib import Path
import hashlib,sys
root=Path(__file__).resolve().parent
manifest=root/'MANIFEST.sha256'
rows=manifest.read_text(encoding='utf-8').splitlines()
problems=[]
for line in rows:
    want,name=line.split('  ',1)
    file=root/name
    actual=hashlib.sha256(file.read_bytes()).hexdigest() if file.is_file() else 'MISSING'
    if want!=actual:problems.append(name)
print(f'checked {len(rows)} files; disagreements={len(problems)}',problems)
sys.exit(1 if problems else 0)
