"""CPU microbenchmark with fixed equivalent information; no ML performance claims."""
import json, platform, statistics, sys, time, tracemalloc
from pathlib import Path
from common import EVIDENCE,registry,canonical,digest
from interpreter_a import InterpreterA
from baseline import TypedEvaluator,TRANSFER_TREE

ROOT=Path(__file__).resolve().parents[1]
REG=registry()['definitions']
RUNS=6000
WORKLOAD=[i%3 for i in range(RUNS)]

def make_arm(name):
    if name=='typed_uncached':
        model=TypedEvaluator(cached=False)
        return lambda stage:model.evaluate(TRANSFER_TREE,EVIDENCE,stage)
    if name=='typed_cached':
        model=TypedEvaluator(cached=True)
        return lambda stage:model.evaluate(TRANSFER_TREE,EVIDENCE,stage)
    settings={
        'lc_reuse_cached':(True,True),
        'lc_reuse_no_result_cache':(True,False),
        'lc_no_reuse_no_result_cache':(False,False),
    }
    reuse,cached=settings[name]
    model=InterpreterA(REG,reuse=reuse,result_cache=cached)
    return lambda stage:model.evaluate('G1(A)',evidence=EVIDENCE,stage=stage)


def bench(name, *, trials=5):
    times=[]
    for _ in range(trials):
        compute=make_arm(name)
        # Warm up all three states identically; evaluate results before measurement.
        for stage,truth in enumerate(['U','T','F']):
            if compute(stage)['value']!=truth:
                raise AssertionError(f'arm {name} fails semantic control at {stage}')
        t0=time.perf_counter_ns()
        for stage in WORKLOAD:
            compute(stage)
        elapsed=time.perf_counter_ns()-t0
        times.append(elapsed / 1e6)
    mem=make_arm(name)
    tracemalloc.start()
    for stage in WORKLOAD[:300]: mem(stage)
    current,peak=tracemalloc.get_traced_memory()
    tracemalloc.stop()
    return {'arm':name,'queries':RUNS,'trials':trials,
            'median_ms_total':round(statistics.median(times),3),
            'min_ms_total':round(min(times),3),
            'max_ms_total':round(max(times),3),
            'median_us_per_query':round(statistics.median(times)*1000/RUNS,3),
            'python_traced_peak_bytes_for_300_queries':peak}


def main():
    arms=['typed_uncached','typed_cached','lc_reuse_cached','lc_reuse_no_result_cache','lc_no_reuse_no_result_cache']
    results=[bench(name) for name in arms]
    reg=registry()
    lex='G1(A)'
    typed_bytes=len(canonical(TRANSFER_TREE).encode('utf-8'))
    lex_bytes=len(lex.encode('utf-8'))
    registry_bytes=len(canonical(reg).encode('utf-8'))
    report={
        'methodology':{
            'type':'Python synthetic repeated-query CPU microbenchmark; not an end-to-end AI comparison',
            'same_inputs':'same toy policy, observations, and three snapshot stages for all arms',
            'query_count':RUNS,
            'per_arm_trials':5,
            'measurement':'perf_counter_ns; median of trials; sequential execution',
            'warmup':'three queries, one per evidence stage',
            'memory':'tracemalloc peak of 300 queries after fresh instantiation; Python allocations only',
            'excluded':'natural-language interpretation, text generation, training, full registry authoring/maintenance, disk IO and external-model baselines',
            'caution':'Interpreter A is one Python implementation; timings are not proof of inherent representational efficiency. Conventional typed baselines can also cache and reuse definitions.'},
        'environment':{'python':sys.version.split()[0],'platform':platform.platform(),
                       'machine':platform.machine(),'registry_digest':digest(reg)},
        'arms':results,
        'representation_bytes':{'lexicon_query':lex_bytes,'typed_json_query':typed_bytes,
                                'full_registry':registry_bytes,
                                'amortized_lexicon_storage_bytes':{str(n):registry_bytes+n*lex_bytes for n in [1,10,100,1000]},
                                'typed_json_storage_bytes':{str(n):n*typed_bytes for n in [1,10,100,1000]}},
        'finding':'Measurements are workload-local, warm-cache-sensitive and do not establish efficiency over modern LLMs.'}
    (ROOT/'results'/'benchmark.json').write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps(report,indent=2))

if __name__=='__main__': main()
