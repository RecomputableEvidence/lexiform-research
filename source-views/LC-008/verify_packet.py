"""Standalone cross-process packet verifier. Requires the embedded dependency ZIPs."""
import argparse
import json
from pathlib import Path
import sys
import tempfile

ROOT=Path(__file__).resolve().parent
sys.path.insert(0,str(ROOT/'src'))
from dependencies import load_dependency_paths


def no_duplicate_object(pairs):
    d={}
    for key,value in pairs:
        if key in d:raise ValueError('duplicate JSON key: '+key)
        d[key]=value
    return d


def main():
    p=argparse.ArgumentParser(description='Replay a portable audit packet from frozen code')
    p.add_argument('packet',type=Path)
    p.add_argument('--trusted-tip',help='SHA-256 tip obtained independently of the packet')
    p.add_argument('--trusted-packet-hash',help='SHA-256 hash obtained independently of the packet')
    args=p.parse_args()
    try:
        packet=json.loads(args.packet.read_text(encoding='utf-8'),object_pairs_hook=no_duplicate_object,
                          parse_constant=lambda x: (_ for _ in ()).throw(ValueError('invalid JSON constant '+x)))
        with tempfile.TemporaryDirectory(prefix='lc008-vfy-') as directory:
            load_dependency_paths(directory)
            from portable_audit import verify_packet
            result=verify_packet(packet,args.trusted_tip,args.trusted_packet_hash)
        print(json.dumps(result,indent=2,sort_keys=True))
        return 0
    except (ValueError,TypeError,KeyError,AttributeError,IndexError,RecursionError) as e:
        print(json.dumps({'verified':False,'error':str(e)},indent=2,sort_keys=True),file=sys.stderr)
        return 1

if __name__=='__main__':sys.exit(main())
