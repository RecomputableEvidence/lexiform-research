"""Exploratory, non-equivalence-controlled Python microbenchmark. No speed claim.
Shared CHOICE syntax; unequal caching/compiler profiles reported explicitly.
"""
import json
import statistics
import time
from pathlib import Path
from choice_a import ChoiceA
from choice_b import ChoiceB
from choice_control import ChoiceTypedBaseline
from evidence import EvidenceLedger
from registry import FrozenDefinitions

ROOT=Path(__file__).resolve().parents[1]
REGISTRY=json.loads((ROOT/'history_extracted'/'LC-EXP-003'/'spec'/'relational_registry_predecessor.json').read_text())['macros']

def row(i,atom):return {'id':i,'atom':atom,'value':'T','observed_stage':0,'valid_from':0,'valid_until':5,
                        'source':'microbenchmark-fixture','persistence_policy':'bounded'}
def balanced(items):
    while len(items)>1:
        items=[f'CHOICE({items[i]},{items[i+1]})' if i+1<len(items) else items[i]
               for i in range(0,len(items),2)]
    return items[0]

def execute():
    reg=FrozenDefinitions(REGISTRY)
    rows=[]
    for n in (2,8,16,64):
        ev=[row(f'AB{i}',f'R(A,N{i})') for i in range(n)]+[row(f'BZ{i}',f'R(N{i},Z)') for i in range(n)]
        expr=balanced([f'C(R(A,N{i}),R(N{i},Z))' for i in range(n)])
        led=EvidenceLedger(ev)
        for cls in (ChoiceA,ChoiceB,ChoiceTypedBaseline):
            obj=cls(reg)
            timings=[]
            for trial in range(31):
                t=time.perf_counter_ns();result=obj.evaluate(expr,led,0);elapsed=time.perf_counter_ns()-t
                if result['value']!='T':raise ValueError('comparison mismatch')
                timings.append(elapsed/1000)
            rows.append({'arms':n,'implementation':cls.__name__,
                         'cold_first_us':round(timings[0],1),
                         'warm_median_us':round(statistics.median(timings[1:]),1),
                         'samples_after_cold':30,'expression_chars':len(expr),
                         'evidence_rows':len(ev)})
    output={'method':'Python perf_counter_ns, CPU process, 31 sequential trials, warm median of 30',
            'limitation':'not randomized, no process independence; A result cache, B recompiles, baseline uncached; not an optimization-equivalent comparative benchmark',
            'data':rows}
    (ROOT/'results'/'exploratory_benchmark.json').write_text(json.dumps(output,indent=2)+'\n')
    return output
if __name__=='__main__':print(json.dumps(execute(),indent=2))
