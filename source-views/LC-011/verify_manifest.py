"""Content hash verification: excluded manifest itself and mutable derived benchmark_latest."""
import hashlib,pathlib,sys
root=pathlib.Path(__file__).resolve().parent
manifest=root/'MANIFEST.sha256'
entries=manifest.read_text().splitlines()
for line in entries:
    digest,rel=line.split('  ',1)
    p=root/rel
    if not p.is_file() or hashlib.sha256(p.read_bytes()).hexdigest()!=digest:
        raise SystemExit('FAIL: '+rel)
print(f'{len(entries)}/{len(entries)} frozen manifest entries match')
