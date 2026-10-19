"""Check bytes against the release manifest; hashes are identity checks, not semantic proofs."""
import hashlib
from pathlib import Path
ROOT=Path(__file__).resolve().parent

def run():
    lines=(ROOT/'MANIFEST.sha256').read_text(encoding='utf-8').splitlines()
    listed=set()
    for line in lines:
        digest,path=line.split('  ',1)
        target=(ROOT/path).resolve()
        if ROOT.resolve() not in target.parents:raise ValueError('manifest path escape')
        if path in listed:raise ValueError('duplicate manifest entry: '+path)
        listed.add(path)
        if hashlib.sha256(target.read_bytes()).hexdigest()!=digest:
            raise ValueError('hash mismatch: '+path)
    actual={str(p.relative_to(ROOT)) for p in ROOT.rglob('*') if p.is_file()
            and p.name!='MANIFEST.sha256' and '__pycache__' not in p.parts}
    missing=actual-listed
    if missing:raise ValueError('manifest omitted files: '+repr(sorted(missing)))
    print(f'{len(lines)} successor files match MANIFEST.sha256')

if __name__=='__main__':run()
