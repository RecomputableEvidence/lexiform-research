"""Matched benchmark: all arms see same expressions, queries, indexed evidence.
No GPU/LLM. Output is cost observation, not complexity certification.
"""
import json
import statistics
import sys
import time
import tracemalloc
import tracemalloc
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent))
from evidence import EvidenceLedger
from registry import FrozenDefinitions
from engine import EngineA,projection
from baseline import TypedBaseline

ROOT=Path(__file__).resolve().parents[1]


def chain(n):
    nodes=[f'N{i}' for i in range(n+1)]
    terms=[f'R({a},{b})' for a,b in zip(nodes,nodes[1:])]
    while len(terms)>1:
        terms=[f'C({terms[i]},{terms[i+1]})' if i+1<len(terms) else terms[i] for i in range(0,len(terms),2)]
    return terms[0]

def run_bench():
    registry=FrozenDefinitions(json.loads((ROOT/'spec/relational_registry_predecessor.json').read_text())['macros'])
    output={'experiment':'LC-EXP-003-INDEX-REUSE-001','method':'same indexed evidence, same expression and full provenance output; 40 warm repeats; 7 cold builds; tracemalloc peak is Python allocation proxy; index build separately timed; process-local monotonic clock',
            'arms':{},'index_cost':{},'environment':{'python':sys.version.split()[0]}}
    for size in (8,16,32,64):
        data=[{'id':f'E{i}','atom':f'R(N{i},N{i+1})','value':'T',
               'observed_stage':0,'valid_from':0,'valid_until':2,'source':'bounded fixture','persistence_policy':'bounded'} for i in range(size)]
        t0=time.perf_counter_ns();ledger=EvidenceLedger(data);index_ns=time.perf_counter_ns()-t0
        expr=chain(size);output['index_cost'][size]={'rows':size,'build_ns':index_ns}
        for name,ctor in (
            ('typed_ast_no_result_cache',lambda:TypedBaseline(registry,False)),
            ('typed_ast_result_cache',lambda:TypedBaseline(registry,True)),
            ('lexicon_dag_no_result_cache',lambda:EngineA(registry,False)),
            ('lexicon_dag_result_cache',lambda:EngineA(registry,True)),
        ):
            # A separate instance per arm. Each executes once for compilation and correctness.
            obj=ctor();expected=obj.evaluate(expr,ledger,1,1)
            if expected['value']!='T' or len(expected['links'])!=size:raise RuntimeError('bad benchmark fixture')
            obj.reset_stats()
            times=[]
            for i in range(40):
                start=time.perf_counter_ns();result=obj.evaluate(expr,ledger,1,1)
                times.append(time.perf_counter_ns()-start)
                if result['value']!='T':raise RuntimeError('incorrect output')
            cold=[]
            for trial in range(7):
                cold_obj=ctor()
                begin=time.perf_counter_ns()
                cold_result=cold_obj.evaluate(expr,ledger,1,1)
                cold.append(time.perf_counter_ns()-begin)
                if cold_result['value']!='T':raise RuntimeError('bad cold result')
            tracemalloc.start()
            measured=ctor()
            measured.evaluate(expr,ledger,1,1)
            _,peak=tracemalloc.get_traced_memory()
            tracemalloc.stop()
            output['arms'].setdefault(name,[]).append({'links':size,'tracemalloc_peak_bytes':peak,
                'cold_median_ns':round(statistics.median(cold)),
                'median_ns':round(statistics.median(times)),
                'min_ns':min(times),'lookups':obj.stats['lookup_calls'],
                'candidates_examined':obj.stats['candidate_rows_examined'],
                'cache_hits':obj.stats.get('result_cache_hits',0),
                'cache_misses':obj.stats.get('result_cache_misses',0),
                'note':'warm parser; memo primed for cache arms; cold includes parse+graph creation+evaluation+trace; index construction excluded'})
    return output

if __name__=='__main__':
    report=run_bench()
    target=ROOT/'results'/'benchmark.json'
    target.write_text(json.dumps(report,indent=2,sort_keys=True)+'\n')
    print(json.dumps(report,indent=2))
