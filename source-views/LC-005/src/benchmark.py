"""Exploratory CPU comparison. Typed baseline is algebraically matched but lacks
lazy's full per-witness provenance DAG; do not infer a fair audit-equivalent speed claim.
"""
import json,platform,statistics,sys,time,tracemalloc
from pathlib import Path
from lazy_graph import LazyGraph
from typed_controls import TypedDP,EagerOracle
from typed_audit import TypedAudit
from evidence import EvidenceLedger
from registry import FrozenDefinitions

ROOT=Path(__file__).resolve().parents[1]
reg=FrozenDefinitions(json.loads((ROOT/'history_003_extracted'/'LC-EXP-003'/'spec'/'relational_registry_predecessor.json').read_text())['macros'])

def row(id,atom):
    return {'id':id,'atom':atom,'value':'T','observed_stage':0,'valid_from':0,
            'valid_until':10,'source':'benchmark-constructed','persistence_policy':'bounded'}

def instance(n):
    expr='';rows=[]
    for i in range(n):
        a=f'N{i}';b=f'N{i+1}';x=f'X{i}';y=f'Y{i}'
        leaf=f'CHOICE(C(R({a},{x}),R({x},{b})),C(R({a},{y}),R({y},{b})))'
        expr=leaf if not expr else f'C({expr},{leaf})'
        for side in (x,y):
            rows += [row(f'Ea{i}{side}',f'R({a},{side})'),row(f'Eb{i}{side}',f'R({side},{b})')]
    return expr,rows

def times(engine_class,expr,ledger,reps=9,warm_iters=40):
    cold=[];warm=[];stats=[]
    for _ in range(reps):
        engine=engine_class(reg);engine.reset_stats()
        start=time.perf_counter_ns();r=engine.evaluate(expr,ledger,0);cold.append((time.perf_counter_ns()-start)/1e6)
        stats.append(dict(engine.stats))
        start=time.perf_counter_ns()
        for _ in range(warm_iters):engine.evaluate(expr,ledger,0)
        warm.append((time.perf_counter_ns()-start)/1e6/warm_iters)
    engine=engine_class(reg);tracemalloc.start();engine.evaluate(expr,ledger,0)
    _,peak=tracemalloc.get_traced_memory();tracemalloc.stop()
    return {'median_cold_ms':round(statistics.median(cold),4),
            'median_warm_ms':round(statistics.median(warm),4),
            'median_peak_alloc_bytes':peak,'first_execution_stats':stats[0],
            'reported_derivations':r['witness_count']}

def run():
    rows=[]
    for n in (2,4,8,16,32,64):
        expr,r=instance(n)
        before=time.perf_counter_ns();ledger=EvidenceLedger(r)
        idxms=(time.perf_counter_ns()-before)/1e6
        lex=times(LazyGraph,expr,ledger);typed=times(TypedDP,expr,ledger);audit=times(TypedAudit,expr,ledger)
        eager=None
        if n<=8:
            samples=[]
            for _ in range(3):
                start=time.perf_counter_ns();v=EagerOracle(reg).evaluate(expr,ledger,0)
                samples.append((time.perf_counter_ns()-start)/1e6)
            eager={'median_ms':round(statistics.median(samples),4),'path_count':v['witness_count']}
        rows.append({'segments':n,'distinct_records':len(r),'derivation_count_decimal':str(2**n),
                     'index_build_ms':round(idxms,4),'lexicon_lazy':lex,
                     'conventional_typed_dp':typed,'conventional_typed_audit':audit,'eager_enumerator':eager})
        print(f'{n:>3} 2^{n}: LC cold {lex["median_cold_ms"]:>8.3f}ms '
              f' typed cold {typed["median_cold_ms"]:>8.3f}ms '
              f' audit cold {audit["median_cold_ms"]:>8.3f}ms '
              f' LC warm {lex["median_warm_ms"]:>8.3f}ms '
              f' typed warm {typed["median_warm_ms"]:>8.3f}ms '
              f' audit warm {audit["median_warm_ms"]:>8.3f}ms')
    return {'id':'LC-EXP-005-CPU-PRESSURE-001','python':sys.version,'platform':platform.platform(),
            'measurement':'monotonic wall-clock; single-thread Python; medians of 9 fresh engines per arm; warm 40 iterations/run',
            'notes':['The controls share LC-003 evidence semantics, ledger index, and validator',
                     'Typed DP returns aggregate result, lazy and typed-audit arms return identical full witness graphs',
                     'No model inference, training, or comparison to LLM token cost',
                     'Witness count is derivation combinations, not independent evidence observations',
                     'Eager arm intentionally unoptimized and limited to <=256 combinations'],
            'runs':rows}
if __name__=='__main__':
    result=run()
    (ROOT/'results'/'benchmark.json').write_text(json.dumps(result,indent=2)+'\n')
