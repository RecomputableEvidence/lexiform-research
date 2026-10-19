#!/usr/bin/env python3
"""Read-only verifier of the unmodified LexiFORM archive population."""
from pathlib import Path
import argparse
import hashlib
import json
import re
import zipfile
import sys
ROOT=Path(__file__).resolve().parents[1]

def verify():
    reg=json.loads((ROOT/'registry'/'experiments.json').read_text(encoding='utf-8'))
    passes=0; entries=0; failed=[]
    for item in reg['experiments']:
        p=ROOT/item['archive_path']
        try:
            raw=p.read_bytes()
            if len(raw)!=item['archive_size_bytes'] or hashlib.sha256(raw).hexdigest()!=item['archive_sha256']:
                raise ValueError('archive bytes/sha256 mismatch')
            with zipfile.ZipFile(p) as z:
                corrupt=z.testzip()
                if corrupt is not None:raise ValueError('CRC:'+corrupt)
                mfs=[x for x in z.namelist() if x.endswith('/MANIFEST.sha256')]
                if len(mfs)!=1:raise ValueError('manifest missing/ambiguous')
                prefix=mfs[0].rsplit('/',1)[0]+'/'
                count=0
                for line in z.read(mfs[0]).decode('utf-8').splitlines():
                    if not line.strip() or line.startswith('#'):continue
                    m=re.fullmatch(r'([a-fA-F0-9]{64})\s+\*?(.+?)\s*',line)
                    if not m:raise ValueError('bad line in '+mfs[0])
                    expected,rel=m.groups()
                    rel=rel.removeprefix('./')
                    if rel.startswith('/') or '..' in Path(rel).parts: raise ValueError('unsafe path')
                    member=prefix+rel
                    content=z.read(member)
                    if hashlib.sha256(content).hexdigest()!=expected.lower():raise ValueError('member hash mismatch:'+member)
                    count+=1
                if count!=item['internal_manifest_entries']:raise ValueError('unexpected member count')
                passes+=1;entries+=count
                print(f"PASS {item['experiment_id']} {count}/{count} sha256 manifest entries")
        except Exception as e:failed.append({'experiment_id':item['experiment_id'],'error':str(e)})
    for extra in reg['additional_examination_archives']:
        p=ROOT/extra['path']
        try:
            if hashlib.sha256(p.read_bytes()).hexdigest()!=extra['sha256']:raise ValueError('sha256 mismatch')
            with zipfile.ZipFile(p) as z:
                if z.testzip():raise ValueError('CRC mismatch')
            print('PASS EXTRA '+str(extra['path']))
        except Exception as e:failed.append({'artifact':extra['path'],'error':str(e)})
    print(json.dumps({'archive_count_verified':passes,'manifest_entries_verified':entries,'failed':failed,'standing_effect':'NONE'},indent=2))
    return 0 if len(failed)==0 and passes==len(reg['experiments']) else 1

if __name__=='__main__':sys.exit(verify())
