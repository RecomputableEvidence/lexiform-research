from pathlib import Path
import hashlib,sys
root=Path(__file__).resolve().parent
manifest=root/'MANIFEST.sha256'
lines=[s.strip().split('  ',1) for s in manifest.read_text().splitlines() if s.strip()]
valid=0
for expected,rel in lines:
    p=(root/rel).resolve()
    if root.resolve() not in p.parents or not p.is_file():
        print('MISSING/INVALID',rel);sys.exit(1)
    actual=hashlib.sha256(p.read_bytes()).hexdigest()
    if actual!=expected:
        print('MISMATCH',rel,actual);sys.exit(1)
    valid+=1
print(f'MANIFEST VERIFIED {valid}/{len(lines)}')
