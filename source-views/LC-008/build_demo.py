"""Reproducible synthetic T -> U ledger append, with the original T audit exported later."""
import json
from pathlib import Path
import sys
import tempfile
ROOT=Path(__file__).resolve().parent
sys.path.insert(0,str(ROOT/'src'))
from dependencies import load_dependency_paths


def row(i,atom,value):
    return {'id':i,'atom':atom,'value':value,'observed_stage':0,'valid_from':0,
            'valid_until':5,'source':'synthetic-declared','persistence_policy':'bounded'}


def main():
    with tempfile.TemporaryDirectory(prefix='lc008-demo-') as tmp:
        load_dependency_paths(tmp)
        from registry import FrozenDefinitions
        from persistent_ledger import AppendLedger
        from selective_audit import SelectiveAudit
        from portable_audit import export_packet,verify_packet
        d=FrozenDefinitions({'H1':{'version':1,'parameters':['a','b','c'],
                      'expression':'C(R({a},{b}),R({b},{c}))'},
                      'H2':{'version':2,'parameters':['a','b','c'],
                      'expression':'J(P({b}),C(R({a},{b}),R({b},{c})))'}})
        ledger=AppendLedger([row('claim-a','R(A,B)','T')]);before=ledger.snapshot()
        engine=SelectiveAudit(d,'A')
        old=engine.evaluate('R(A,B)',before,0,0)
        after=ledger.append(row('claim-b','R(A,B)','F'))
        new=engine.evaluate('R(A,B)',after,0,0)
        for name,handle,snap in (('historical_T',old['audit_handle'],before),
                                 ('later_U',new['audit_handle'],after)):
            packet=export_packet(engine,handle,snap,d,[0])
            result=verify_packet(packet,trusted_ledger_tip=snap.digest)
            assert result['verified']
            (ROOT/'examples'/(name+'.json')).write_text(json.dumps(packet,sort_keys=True,
                                                               indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
            (ROOT/'results'/(name+'_verification.json')).write_text(json.dumps(result,sort_keys=True,indent=2)+'\n')
        print('Created portable historical T and later U packets, both independently re-verifiable.')

if __name__=='__main__':main()
