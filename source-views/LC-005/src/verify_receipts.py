"""Independent replay of archived typed transition receipts from preserved inputs."""
import json
from pathlib import Path
from evidence import EvidenceLedger,sha
from registry import FrozenDefinitions
from lazy_graph import LazyGraph
from transitions_005 import rewrite_receipt,reassess_receipt

ROOT=Path(__file__).resolve().parents[1]
reg=FrozenDefinitions(json.loads((ROOT/'history_003_extracted'/'LC-EXP-003'/'spec'/'relational_registry_predecessor.json').read_text())['macros'])
receipts=json.loads((ROOT/'results'/'example_receipts.json').read_text())

def verify(r):
    payload={k:v for k,v in r.items() if k!='receipt_sha256'}
    if sha(payload)!=r['receipt_sha256']:raise ValueError('receipt hash mismatch')
    if r['kind']=='REWRITE':
        ledger=EvidenceLedger(r['evidence_records']);q=r['requested_query_stage'];k=r['knowledge_stage']
        recomputed=rewrite_receipt(r['source'],r['rule'],reg,ledger,q,k)
    else:
        previous=EvidenceLedger(r['previous_evidence_records'])
        successor=EvidenceLedger(r['successor_evidence_records'])
        q=r['requested_query_stage']
        recomputed=reassess_receipt(r['source_expression'],reg,previous,successor,
                                  q,r['previous']['knowledge_stage'],r['successor']['knowledge_stage'])
    if r!=recomputed:raise ValueError('receipt recomputation mismatch')
    return r['kind']
if __name__=='__main__':
    labels=[verify(receipts['rewrite']),verify(receipts['reassess'])]
    print('RECOMPUTED',labels)
