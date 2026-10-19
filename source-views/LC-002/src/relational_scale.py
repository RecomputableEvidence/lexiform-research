"""Within-treatment scaling probe; not a competitive baseline or a speed claim."""
from pathlib import Path
import json,sys,statistics,time,platform,random
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'src'))
from relational_a import RelationalA
from relational_b import RelationalB

MACROS=json.loads((ROOT/'spec'/'relational_registry.json').read_text())['macros']

def make(n):
    nodes=[f'N{i}' for i in range(n+1)]
    expr=f'R({nodes[0]},{nodes[1]})'
    evidence=[]
    for i in range(n):
        atom=f'R({nodes[i]},{nodes[i+1]})'
        evidence.append({'id':f'EV{i:03}', 'stage':0,'atom':atom,'value':'T'})
        if i:expr=f'C({expr},{atom})'
    return expr,evidence

def run():
    results=[]
    for n in (2,4,8,16,32):
        expr,evidence=make(n)
        for name,cls in (('REL-A',RelationalA),('REL-B',RelationalB)):
            obj=cls(MACROS)
            assert obj.evaluate(expr,evidence,0)['value']=='T'
            trials=[]
            repetitions=180 if n<=8 else 90
            for i in range(5):
                for _ in range(10):obj.evaluate(expr,evidence,0)
                start=time.perf_counter_ns()
                for _ in range(repetitions):obj.evaluate(expr,evidence,0)
                trials.append((time.perf_counter_ns()-start)/repetitions/1000)
            results.append({'engine':name,'link_count':n,'expression_chars':len(expr),
                            'median_us_per_evaluation':round(statistics.median(trials),3),
                            'trial_us':list(map(lambda x:round(x,3),trials)),
                            'repetitions_per_trial':repetitions,'expected_truth':'T'})
    output={'description':'Unoptimized Python within-treatment scaling only; includes parsing, evidence selection, VM/AST evaluation; no I/O; not a full-system or LLM benchmark',
            'platform':platform.platform(),'python':platform.python_version(),'results':results}
    (ROOT/'results'/'relational_scale.json').write_text(json.dumps(output,indent=2)+'\n')
    print(json.dumps(output,indent=2))
if __name__=='__main__':run()
