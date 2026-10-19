"""Recompute deterministic illustration of changes to truth vs supporting identity."""
from pathlib import Path
import json,sys
from run_all import run
ROOT=Path(__file__).resolve().parent

def main():
    run()
    from persistent_ledger import AppendLedger,verify_transition
    from selective_audit import SelectiveAudit
    from registry import FrozenDefinitions
    macros={'H1':{'version':1,'parameters':['a','b','c'],'expression':'C(R({a},{b}),R({b},{c}))'},
            'H2':{'version':2,'parameters':['a','b','c'],'expression':'J(P({b}),C(R({a},{b}),R({b},{c})))'}}
    def row(i,atom,value):
        return {'id':i,'atom':atom,'value':value,'observed_stage':0,'valid_from':0,
                'valid_until':10,'source':'synthetic-only','persistence_policy':'bounded'}
    store=AppendLedger();engine=SelectiveAudit(FrozenDefinitions(macros))
    initial=store.snapshot();ids=set();prev=initial;events=[];first_handle=None
    for i,(name,atom,value) in enumerate((('e0','R(A,B)','T'),
                        ('corroborate','R(A,B)','T'),('unrelated','R(Q,W)','F'),
                        ('conflict','R(A,B)','F'))):
        snap=store.append(row(name,atom,value))
        proof=snap.transition(prev)
        assert verify_transition(proof,prev.digest,prev.length,ids)
        ids.add(name);prev=snap
        r=engine.evaluate('R(A,B)',snap,0)
        if i==0:first_handle=r['audit_handle']
        events.append({'event':name,'ledger_commitment':snap.digest,'value':r['value'],
          'root_id':r['root_id'],'revision':i,'lookup_calls':engine.last_receipt['lookups'],
          'nodes_recomputed':engine.last_receipt['nodes_recomputed'],
          'evidence_ids':engine.witness(r['audit_handle'],0)['evidence_ids'],
          'append_proof':proof})
    historical=engine.witness(first_handle,0)
    artifact={'experiment':'LC-EXP-007-APPEND-BOUND-AUDIT-001',
      'genesis_anchor':initial.digest,'events':events,
      'historical_first_result_after_all_updates':{
         'root_id':first_handle.root_id,'value':historical['value'],
         'evidence_ids':historical['evidence_ids']},
      'notes':['Evidence supplied by synthetic fixtures; no attestation of physical conditions',
               'Append proofs require trusted anchored prior digest and external prior-ID state',
               'A full portable audit requires independent full replay of recorded rows']}
    (ROOT/'results'/'example_transitions.json').write_text(json.dumps(artifact,indent=2)+'\n')
    return artifact
if __name__=='__main__':main()
