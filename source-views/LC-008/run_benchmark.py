"""Bounded CPU observations of portable packet byte size and replay work; not a matched comparator."""
import json
from pathlib import Path
import platform
import statistics
import sys
import tempfile
import time

ROOT=Path(__file__).resolve().parent
sys.path.insert(0,str(ROOT/'src'))
from dependencies import load_dependency_paths


def row(i,atom):
    return {'id':i,'atom':atom,'value':'T','observed_stage':0,'valid_from':0,
            'valid_until':10,'source':'synthetic','persistence_policy':'bounded'}


def path(n):
    expr='';rows=[]
    for i in range(n):
        a,b=f'N{i}',f'N{i+1}';x,y=f'X{i}',f'Y{i}'
        part=f'CHOICE(C(R({a},{x}),R({x},{b})),C(R({a},{y}),R({y},{b})))'
        expr=part if not expr else f'C({expr},{part})'
        for j,(u,v) in enumerate(((a,x),(x,b),(a,y),(y,b))):
            rows.append(row(f'E{i}-{j}',f'R({u},{v})'))
    return expr,rows


def main():
    with tempfile.TemporaryDirectory(prefix='lc008-bench-') as tmp:
        load_dependency_paths(tmp)
        from registry import FrozenDefinitions
        from selective_audit import SelectiveAudit
        from persistent_ledger import AppendLedger
        from portable_audit import export_packet,verify_packet
        defs={'H1':{'version':1,'parameters':['a','b','c'],'expression':'C(R({a},{b}),R({b},{c}))'},
              'H2':{'version':2,'parameters':['a','b','c'],'expression':'J(P({b}),C(R({a},{b}),R({b},{c})))'}}
        d=FrozenDefinitions(defs)
        records=[]
        for n in (8,32,64):
            expr,rows=path(n);snap=AppendLedger(rows).snapshot()
            engine=SelectiveAudit(d,'A');h=engine.evaluate(expr,snap,0)['audit_handle']
            t_export=[];t_verify=[]
            for k in range(5):
                start=time.perf_counter_ns()
                p=export_packet(engine,h,snap,d,[0,2**n-1])
                t_export.append((time.perf_counter_ns()-start)/1e6)
                start=time.perf_counter_ns()
                result=verify_packet(p,trusted_ledger_tip=snap.digest)
                t_verify.append((time.perf_counter_ns()-start)/1e6)
                assert result['verified']
            size=len(json.dumps(p,sort_keys=True,ensure_ascii=False,separators=(',',':')).encode('utf-8'))
            records.append({'segments':n,'synthetic_evidence_records':len(rows),
                            'syntactic_witness_count_decimal':str(2**n),
                            'packet_bytes_compact_json':size,
                            'packet_export_median_ms':round(statistics.median(t_export),4),
                            'full_replay_median_ms':round(statistics.median(t_verify),4),
                            'graph_nodes':result['graph_nodes'],'repetitions':5})
        payload={'experiment':'LC-EXP-008-PORTABLE-AUDIT-001',
                 'purpose':'Illustrative synthetic full-history serialization and complete offline replay cost',
                 'environment':{'python':platform.python_version(),'system':platform.system(),
                                'machine':platform.machine()},
                 'constraints':'Single CPU process; timings exclude subprocess startup and dependency archive extraction; no optimized comparator; no end-to-end performance advantage claimed',
                 'results':records}
        (ROOT/'results'/'benchmark_008.json').write_text(json.dumps(payload,indent=2)+'\n')
        print(json.dumps(payload,indent=2))

if __name__=='__main__':main()
