import json
from pathlib import Path
from lazy_graph import LazyGraph,select_witness
from evidence import EvidenceLedger
from registry import FrozenDefinitions
from transitions_005 import rewrite_receipt,reassess_receipt
root=Path(__file__).resolve().parents[1]
reg=FrozenDefinitions(json.loads((root/'history_003_extracted'/'LC-EXP-003'/'spec'/'relational_registry_predecessor.json').read_text())['macros'])
def row(id,atom,value='T',obs=0):return {'id':id,'atom':atom,'value':value,'observed_stage':obs,'valid_from':0,'valid_until':12,'source':'demonstration','persistence_policy':'bounded'}
expr='C(CHOICE(C(R(A,X),R(X,B)),C(R(A,Y),R(Y,B))),R(B,Z))'
before=EvidenceLedger([row('AX','R(A,X)'),row('XB','R(X,B)'),row('AY','R(A,Y)','F'),row('YB','R(Y,B)'),row('BZ','R(B,Z)')])
after=EvidenceLedger(before.records_as_dicts()+[row('NEW','R(A,Y)','T',obs=2)])
a=LazyGraph(reg).evaluate(expr,before,0,0)
b=LazyGraph(reg).evaluate(expr,after,0,2)
receipts={'sample_predecessor_evaluation':{k:a[k] for k in ('value','histogram','witness_count','root_id','ledger_sha256')},
          'sample_successor_evaluation':{k:b[k] for k in ('value','histogram','witness_count','root_id','ledger_sha256')},
          'first_witness':select_witness(a,0),
          'last_witness':select_witness(a,a['witness_count']-1),
          'rewrite':rewrite_receipt(expr,'CHAIN_CHOICE_LEFT',reg,before,0,0),
          'reassess':reassess_receipt(expr,reg,before,after,0,0,2)}
(root/'results'/'example_receipts.json').write_text(json.dumps(receipts,indent=2)+'\n')
print('examples written')
