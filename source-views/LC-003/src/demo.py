"""Generates append-only transition demo as inspectable JSON, not a proof of authority."""
import json
from pathlib import Path
from evidence import EvidenceLedger
from registry import FrozenDefinitions
from engine import EngineA,EngineB,projection
from transitions import rewrite_receipt,reassess_receipt

ROOT=Path(__file__).resolve().parents[1]

def record(id,atom,value,obs,begin,end):
    return {'id':id,'atom':atom,'value':value,'observed_stage':obs,'valid_from':begin,
            'valid_until':end,'source':'declared fixture; no real-world standing',
            'persistence_policy':'bounded'}

def run():
    registry=FrozenDefinitions(json.loads((ROOT/'spec/relational_registry_predecessor.json').read_text())['macros'])
    before=EvidenceLedger([record('A0','R(A,B)','T',0,0,3),record('B0','R(B,C)','T',0,0,3),record('C0','R(C,D)','T',0,0,3)])
    after=EvidenceLedger(before.records_as_dicts()+[record('B2','R(B,C)','F',2,2,4)])
    source='C(C(R(A,B),R(B,C)),R(C,D))'
    rewrite=rewrite_receipt(source,registry,before,2,1)
    reassess,prior,later=reassess_receipt(source,registry,before,after,2,1,2)
    historical=EngineA(registry).evaluate('R(A,B)',before,3,1)
    package={'subject':'LC-EXP-003-DEMO-001','description':'declared toy evidence, not an external measurement',
             'original_ledger':{'digest':before.digest,'records':before.records_as_dicts()},
             'successor_ledger':{'digest':after.digest,'records':after.records_as_dicts()},
             'prior':prior,'later':later,'rewrite_receipt':rewrite,'reassess_receipt':reassess,
             'expired_query':historical,
             'interpretive_scope':'Truth labels are bounded satisfaction of a witness under asserted interval metadata, not authenticated validity.'}
    dest=ROOT/'results'/'demo_trace.json';dest.write_text(json.dumps(package,indent=2,sort_keys=True)+'\n')
    return package

if __name__=='__main__':
    pkg=run()
    print('demo:',pkg['prior']['value'],'→',pkg['later']['value'],'; expired witness:',pkg['expired_query']['value'])
