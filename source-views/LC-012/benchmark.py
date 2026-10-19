"""Matched-output CPU microbenchmark; cold per-query evaluator, no result cache in either arm.
Controls preparse once, instantiate and validate a new evaluator on each query.
Measured timings describe this Python implementation only; not semantic novelty.
"""
from pathlib import Path
from statistics import median
from time import perf_counter_ns
import json,sys,gc,tracemalloc
ROOT=Path(__file__).resolve().parent
sys.path.insert(0,str(ROOT/'src'))
from fixtures import episode,ATOM,to_lex
from lexicon import Lexicon
from typed_baseline import TypedControl,build
from engine import agreement
from contract import sha

L=episode()[-1]
terms=[]
for i in range(24):
    e=ATOM if i%3==0 else ({'op':'LINK','id':'cycle'} if i%3==1 else
       {'op':'ANY','args':[ATOM,{'op':'NOT','arg':ATOM}]})
    terms.append((e,2,i%5, 'default' if i%2 else 'lab'))
for e,q,k,c in terms:agreement(e,L,q,k,c)
lex_terms=[(to_lex(e),q,k,c) for e,q,k,c in terms]
typed_terms=[(build(e),q,k,c) for e,q,k,c in terms]

def lex_batch():
    for t,q,k,c in lex_terms:Lexicon(L).eval(t,q,k,c)
def typed_batch():
    for t,q,k,c in typed_terms:TypedControl(L).evaluate(t,q,k,c)

def sample(fn, repeats=17, loops=15):
    times=[];peaks=[]
    for i in range(repeats):
        gc.collect();tracemalloc.start()
        t0=perf_counter_ns()
        for _ in range(loops):fn()
        elapsed=(perf_counter_ns()-t0)/1e6
        _,peak=tracemalloc.get_traced_memory();tracemalloc.stop()
        times.append(elapsed/(loops*len(terms)));peaks.append(peak)
    return dict(median_ms_per_query=round(median(times),6),min_ms=round(min(times),6),
                max_ms=round(max(times),6),median_peak_bytes=round(median(peaks)),
                repetitions=repeats,loops_per_repetition=loops,queries_per_loop=len(terms))

result={'experiment':'LC-EXP-012','workload':'24 fixed query variants over contested cycle episode',
        'ledger_sha256':sha(L),'controls':'list/AST precompiled; same full result projection; fresh evaluator each call',
        'lexicon':sample(lex_batch),'conventional_typed':sample(typed_batch),
        'caveat':'Single-environment Python timing. No claim of LC-specific performance superiority.'}
(ROOT/'results'/'benchmark_latest.json').write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps(result,indent=2))
