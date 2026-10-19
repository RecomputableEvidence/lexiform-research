"""Matched-in-process illustrative CPU measurements; excludes disk I/O and evidence authentication."""
import sys,time,statistics,json,tracemalloc
from pathlib import Path
ROOT=Path(__file__).resolve().parent
sys.path.insert(0,str(ROOT/'src'))
from fixtures import full_fixture,ATOM,POLICY,to_lex
from typed_control import Typed,build
from lexicon import Lexicon

def go():
    led=full_fixture()
    expressions=[ATOM,POLICY,{'op':'ANY','args':[ATOM,POLICY]},
       {'op':'ALL','args':[{'op':'NOT','arg':ATOM},POLICY]}]+[
       {'op':'SCOPE','query':q,'knowledge':k,'context':c,'body':ATOM}
       for q in [3,6,9] for k in [0,2,4,6,8] for c in ['default','lab']]
    lx=[to_lex(x) for x in expressions]
    tx=[build(x) for x in expressions]
    assert len(lx)==len(tx)
    rounds=10;repetitions=9
    data={}
    for name in ['lexicon','typed']:
        timings=[];cold=[]
        for _ in range(repetitions):
            start=time.perf_counter_ns()
            obj=Lexicon(led) if name=='lexicon' else Typed(led)
            prepared=lx if name=='lexicon' else tx
            for v in prepared:obj.eval(v,6,8)
            cold.append((time.perf_counter_ns()-start)/1e6)
            start=time.perf_counter_ns()
            for _ in range(rounds):
                for v in prepared:obj.eval(v,6,8)
            timings.append((time.perf_counter_ns()-start)/1e6/(len(prepared)*rounds))
        obj=Lexicon(led) if name=='lexicon' else Typed(led)
        tracemalloc.start()
        for v in (lx if name=='lexicon' else tx):obj.eval(v,6,8)
        _current,peak=tracemalloc.get_traced_memory();tracemalloc.stop()
        data[name]={'cold_batch_ms_median':round(statistics.median(cold),6),
                    'warm_per_query_ms_median':round(statistics.median(timings),6),
                    'audit_output_included':True,'peak_traced_bytes_one_batch':peak}
    out={'environment':'single-process Python standard-library CPU',
         'query_count_per_batch':len(expressions),
         'warm_repeats_per_trial':rounds,
         'timing_trials':repetitions,
         'arms':data,
         'claim_ceiling':'informal single-run CPU microbenchmarks; no efficiency superiority claim'}
    (ROOT/'results'/'benchmark_latest.json').write_text(json.dumps(out,indent=2)+'\n')
    print(json.dumps(out,indent=2))
if __name__=='__main__':go()
