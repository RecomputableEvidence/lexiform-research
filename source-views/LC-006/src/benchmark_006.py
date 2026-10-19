"""Reproducible exploratory microbenchmark. No general efficiency superiority claims."""
import json,random,statistics,time,platform,sys,hashlib,os
from pathlib import Path
from reuse import BoundReuse
from typed_audit import TypedAudit
from lazy_graph import LazyGraph
from evidence import EvidenceLedger
from registry import FrozenDefinitions

ROOT=Path(__file__).resolve().parents[1]
def row(name,atom,value='T',obs=0):
    return {'id':name,'atom':atom,'value':value,'observed_stage':obs,
            'valid_from':0,'valid_until':20,'source':'synthetic-benchmark',
            'persistence_policy':'bounded'}
def fixture(n):
    expr='';rows=[]
    for i in range(n):
        a,b,x,y=f'N{i}',f'N{i+1}',f'X{i}',f'Y{i}'
        piece=f'CHOICE(C(R({a},{x}),R({x},{b})),C(R({a},{y}),R({y},{b})))'
        expr=piece if not expr else f'C({expr},{piece})'
        for j,(u,v) in enumerate(((a,x),(x,b),(a,y),(y,b))):
            rows.append(row(f'E{i}-{j}',f'R({u},{v})'))
    return expr,rows

def elapsed_ns(f):
    t=time.perf_counter_ns();out=f()
    return time.perf_counter_ns()-t,out

def main():
    regdoc=json.loads((Path(os.environ['LC006_PREDECESSOR_ROOT'])/'history_003_extracted'/'LC-EXP-003'/'spec'/'relational_registry_predecessor.json').read_text())
    reg=FrozenDefinitions(regdoc['macros'])
    experiments=[]
    for n in (8,32,64):
        expr,source=fixture(n)
        for scenario in ('unrelated','last_segment','first_segment'):
            # A deterministic 16-event append stream; every result carries the full audit graph.
            rows=list(source);ledgers=[];build_times=[]
            for event in range(9):
                dt,ledger=elapsed_ns(lambda:EvidenceLedger(rows))
                ledgers.append(ledger);build_times.append(dt/1e6)
                atom={'unrelated':'R(Q,W)','last_segment':f'R(N{n-1},X{n-1})',
                      'first_segment':'R(N0,X0)'}[scenario]
                rows.append(row(f'ADD{event}',atom,'F'))
            arms={'lexicon_incremental_A':lambda:BoundReuse(reg,'A'),
                  'typed_incremental_B':lambda:BoundReuse(reg,'B'),
                  'lexicon_full_rebuild':lambda:LazyGraph(reg),
                  'typed_audit_full_rebuild':lambda:TypedAudit(reg)}
            all_measures={}
            for name,factory in arms.items():
                trials=[];lookups=[];recomp=[]
                for repeat in range(3):
                    eng=factory();cold=[];warm=[];last=None
                    for i,ledger in enumerate(ledgers):
                        if 'full_rebuild' in name:eng=factory()
                        dt,result=elapsed_ns(lambda:eng.evaluate(expr,ledger,0,0))
                        (cold if i==0 else warm).append(dt/1e6)
                        if i>0 and 'incremental' in name:
                            lookups.append(eng.last_receipt['lookup_calls'])
                            recomp.append(eng.last_receipt['nodes_recomputed'])
                        last=result
                    trials.append({'cold_ms':cold[0],'warm_median_ms':statistics.median(warm),
                                   'warm_total_ms':sum(warm),'root_id':last['root_id']})
                all_measures[name]={'cold_median_ms':round(statistics.median(x['cold_ms'] for x in trials),4),
                     'warm_median_ms':round(statistics.median(x['warm_median_ms'] for x in trials),4),
                     'warm_sequence_total_median_ms':round(statistics.median(x['warm_total_ms'] for x in trials),4),
                     'lookup_calls_per_append_mean':round(statistics.mean(lookups),3) if lookups else None,
                     'recomputed_nodes_per_append_mean':round(statistics.mean(recomp),3) if recomp else None,
                     'final_root_sha256':trials[0]['root_id']}
            assert len({entry['final_root_sha256'] for entry in all_measures.values()})==1
            experiments.append({'segments':n,'scenario':scenario,'new_events':8,
                'initial_evidence_records':len(source),
                'witnesses':str(2**n),
                'ledger_reconstruction_median_ms':round(statistics.median(build_times[1:]),4),
                'arms':all_measures})
            print(n,scenario, 'LC inc',all_measures['lexicon_incremental_A']['warm_median_ms'],
                  'typed inc',all_measures['typed_incremental_B']['warm_median_ms'],
                  'typed full',all_measures['typed_audit_full_rebuild']['warm_median_ms'])
    report={'experiment':'LC-EXP-006-CPU-001','python':sys.version,'platform':platform.platform(),
        'clock':'perf_counter_ns','runs_per_arm':3,'sequential_appends':8,
        'measures':'per-call median of 8 append evaluations, then median across 3 reruns',
        'scope_notes':['Audited complete graph returned by every arm, not aggregate-only output',
           'All arms share ledger and identical update sequence and underlying evidence semantics',
           'Two incremental arms share the selective invalidation algorithm and differ only in parser',
           'Full rebuild arms rebuild parser/graph every update; not a matched optimized incremental competitor',
           'Ledger reconstruction/index build measured separately and applies to all arms',
           'Append prefix check and complete graph serialization remain O(number of records/nodes)',
           'Python CPU benchmark, measurement noise; no LLM inference, no training, no superiority claim'],
        'rows':experiments}
    (ROOT/'results'/'benchmark_006.json').write_text(json.dumps(report,indent=2)+'\n')
    return report
if __name__=='__main__':main()
