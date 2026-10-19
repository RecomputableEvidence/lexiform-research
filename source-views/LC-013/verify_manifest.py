"""Release byte identity check. Not an external trust or signature service."""
import hashlib
from pathlib import Path
root=Path(__file__).resolve().parent
rows=(root/'MANIFEST.sha256').read_text().splitlines()
files=set()
for row in rows:
    digest,sep,rel=row.partition('  ')
    assert sep and rel not in files
    files.add(rel)
    p=(root/rel).resolve()
    assert root.resolve() in p.parents and p.is_file()
    assert hashlib.sha256(p.read_bytes()).hexdigest()==digest,rel
seen={p.relative_to(root).as_posix() for p in root.rglob('*') if p.is_file()
      and p.name!='MANIFEST.sha256' and not p.name.endswith('_latest.json')
      and not p.name.endswith('.pyc') and '__pycache__' not in p.parts}
assert files==seen,{'missing':sorted(files-seen),'extra':sorted(seen-files)}
print('LC013 manifest verified',len(rows),'files')
