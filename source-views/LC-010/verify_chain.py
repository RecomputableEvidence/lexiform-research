"""Portable, cross-process full-replay declared chain verification."""
import argparse
import json
from pathlib import Path
import sys
import tempfile
ROOT=Path(__file__).resolve().parent
sys.path.insert(0,str(ROOT/'src'))
from bootstrap import load_frozen

def pairs(items):
    out={}
    for k,v in items:
        if k in out:raise ValueError('duplicate JSON key: '+k)
        out[k]=v
    return out

def load_file(path):
    raw=path.read_bytes()
    if len(raw)>8_000_000:raise ValueError('8 MB input cap exceeded')
    return json.loads(raw.decode('utf-8'),object_pairs_hook=pairs,
                      parse_constant=lambda k: (_ for _ in ()).throw(ValueError('invalid constant: '+k)))

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('file',type=Path)
    parser.add_argument('--trusted-start-packet-hash')
    parser.add_argument('--trusted-chain-tip')
    args=parser.parse_args()
    try:
        with tempfile.TemporaryDirectory(prefix='lc010-verify-') as work:
            load_frozen(work)
            from chain_audit import verify_chain
            obj=load_file(args.file)
            result=verify_chain(obj,args.trusted_start_packet_hash,args.trusted_chain_tip)
        print(json.dumps(result,indent=2,sort_keys=True));return 0
    except (ValueError,TypeError,KeyError,AttributeError,IndexError,RecursionError,OSError,UnicodeError,OverflowError) as e:
        print(json.dumps({'verified':False,'error':str(e)}),file=sys.stderr);return 1
if __name__=='__main__':sys.exit(main())
