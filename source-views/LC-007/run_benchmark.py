"""Measured CPU microbenchmark. Replays frozen lineage before importing engines."""
import json,time,statistics,platform,sys
from pathlib import Path
from run_all import run
ROOT=Path(__file__).resolve().parent

def timing(fn):
    t=time.perf_counter_ns();v=fn();return (time.perf_counter_ns()-t)/1e6,v

def median(xs):return round(statistics.median(xs),5)

def benchmark():
    run()  # imports frozen predecessor source during clean nested extraction
    from persistent_ledger import AppendLedger
    from selective_audit import SelectiveAudit
    from evidence import EvidenceLedger
    from registry import FrozenDefinitions
    defs={'H1':{'version':1,'parameters':['a','b','c'],'expression':'C(R({a},{b}),R({b},{c}))'},
          'H2':{'version':2,'parameters':['a','b','c'],'expression':'J(P({b}),C(R({a},{b}),R({b},{c})))'}}
    reg=FrozenDefinitions(defs)
    def row(rid,atom,value='T'):
        return {'id':rid,'atom':atom,'value':value,'observed_stage':0,'valid_from':0,
                'valid_until':10,'source':'LC007-benchmark','persistence_policy':'bounded'}
    def fixture(n):
        parts=[];records=[]
        for i in range(n):
            a,b,x,y=f'N{i}',f'N{i+1}',f'X{i}',f'Y{i}'
            parts.append(f'CHOICE(C(R({a},{x}),R({x},{b})),C(R({a},{y}),R({y},{b})))')
            for j,(u,v) in enumerate(((a,x),(x,b),(a,y),(y,b))):
                records.append(row(f'E{i}-{j}',f'R({u},{v})'))
        expr=parts[0]
        for part in parts[1:]:expr=f'C({expr},{part})'
        return expr,records
    results=[]
    for n in (8,32,64):
        samples={'incremental_ledger_append_ms':[],'full_ledger_rebuild_ms':[],
                 'lexicon_root_only_ms':[],'typed_root_only_ms':[],
                 'lexicon_full_audit_ms':[],'single_witness_ms':[]}
        for repeat in range(4):
            expr,rows=fixture(n)
            store=AppendLedger(rows)
            a=SelectiveAudit(reg,'A');b=SelectiveAudit(reg,'B')
            a.evaluate(expr,store.snapshot(),0);b.evaluate(expr,store.snapshot(),0)
            for i in range(8):
                update=row(f'NEW_{repeat}_{i}',f'R(Q{i},W{i})')
                rows.append(update)
                t,snapshot=timing(lambda:store.append(update))
                samples['incremental_ledger_append_ms'].append(t)
                t,reference=timing(lambda:EvidenceLedger(rows))
                samples['full_ledger_rebuild_ms'].append(t)
                t,res=timing(lambda:a.evaluate(expr,snapshot,0))
                samples['lexicon_root_only_ms'].append(t)
                t,res_b=timing(lambda:b.evaluate(expr,snapshot,0))
                samples['typed_root_only_ms'].append(t)
                assert res['root_id']==res_b['root_id']
                if i==7:
                    t,g=timing(lambda:a.full_graph(res['audit_handle']))
                    samples['lexicon_full_audit_ms'].append(t)
                    t,w=timing(lambda:a.witness(res['audit_handle'],2**n-1))
                    samples['single_witness_ms'].append(t)
                    assert len(w['nodes'])==2*n+1
        results.append({'segments':n,'initial_evidence_records':4*n,'graph_node_count':8*n-1,
          'repetitions':4,'append_events_per_repetition':8,
          'median_ms':{key:median(value) for key,value in samples.items()},
          'notes':'Root-only arms A and B share update algorithm; full audit is invoked only on final event.'})
        print(n,results[-1]['median_ms'])
    report={'experiment':'LC-EXP-007-APPEND-BOUND-AUDIT-001','python':sys.version,
      'platform':platform.platform(),'clock':'perf_counter_ns','results':results,
      'claim_limits':['CPU Python microbenchmark; no hardware/software-level universal speedup',
        'A/B root arms share LC007 update algorithm, only parsers differ',
        'Incremental append chain and full SHA-256 ledger use different digest schemes; not interchangeable',
        'The independently recomputed typed comparator is used in correctness tests, not as a matched root-only latency arm',
        'Full graph and full replay remain O(size of graph/ledger) on demand',
        'In-process builder is trusted and not resistant to malicious introspection or storage tampering',
        'Hash linking is not signature-based evidence authentication']}
    (ROOT/'results'/'benchmark_007.json').write_text(json.dumps(report,indent=2)+'\n')
    return report
if __name__=='__main__':benchmark()
