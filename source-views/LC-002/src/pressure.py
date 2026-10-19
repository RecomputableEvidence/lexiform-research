"""Repeatable named boundary probes, with explicit expected/observed assertions."""
import json,sys,copy,hashlib,platform
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'src'))
from interpreter_a import InterpreterA
from interpreter_b import InterpreterB
from relational_a import RelationalA
from relational_b import RelationalB
from common import registry, EVIDENCE
MACROS=json.loads((ROOT/'spec/relational_registry.json').read_text())['macros']
E=[
    {'id':'E1','atom':'R(A,B)','stage':0,'value':'T'},
    {'id':'E2','atom':'R(B,C)','stage':0,'value':'T'},
    {'id':'E3','atom':'P(B)','stage':0,'value':'F'},
    {'id':'E4','atom':'P(B)','stage':1,'value':'T'},
]

observations=[]
def record(identifier,observed,expected,notes):
    success=observed==expected
    observations.append({'id':identifier,'expected':expected,'observed':observed,'pass':success,'notes':notes})
    assert success,identifier

def main():
    R=registry()['definitions']
    external=copy.deepcopy(R)
    b=InterpreterB(external)
    initial=b.evaluate('G1(A)',valuation={'S(A)':'T','P(A)':'F'})['value']
    external['G1']['expression']='S({x})'
    observed=b.evaluate('G1(A)',valuation={'S(A)':'T','P(A)':'F'})['value']
    record('REPAIR-B-EXTERNAL',f'{initial}->{observed}','F->F','External registry change cannot silently alter the interpreter snapshot')
    b.definitions['G1']['expression']='S({x})'
    try:b.evaluate('G1(A)',valuation={'S(A)':'T','P(A)':'F'});result='accepted'
    except ValueError:result='rejected'
    record('REPAIR-B-INTERNAL',result,'rejected','Internal registry tampering must be rejected')
    a=InterpreterA(R)
    exposed=a.evaluate('G1(A)',evidence=EVIDENCE,stage=1)
    exposed['value']='F';exposed['atoms'].append('S(Z)')
    recovered=a.evaluate('G1(A)',evidence=EVIDENCE,stage=1)
    record('REPAIR-A-CACHE',recovered,{'value':'T','atoms':['P(A)','S(A)']},'Caller cannot corrupt cached result through returned object')
    for name,engine in [('A',RelationalA(MACROS)),('B',RelationalB(MACROS))]:
        for stage in (0,1):
            for expr,want in [('H1(A,B,C)','T'),('H2(A,B,C)','F' if stage==0 else 'T')]:
                result=engine.reconstruct(expr,E,stage)
                record(f'{name}-MACRO-{stage}-{expr[:2]}',result['value'],want,
                       'Versioned macro context qualification; same declared graph, different treatment')
        old=engine.evaluate('AT(0,H2(A,B,C))',E,1)
        record(f'{name}-TEMPORAL-REPLAY',old['value'],'F','Later evidence cannot rewrite explicit earlier query stage')
        try:engine.evaluate('C(AT(0,R(A,B)),AT(1,R(B,C)))',E,1);status='accepted'
        except ValueError:status='rejected'
        record(f'{name}-MIXED-STAGES',status,'rejected','Mixed snapshots are not silently composable')
        try:engine.evaluate('C(R(B,C),R(A,B))',E,1);status='accepted'
        except ValueError:status='rejected'
        record(f'{name}-REVERSED-CHAIN',status,'rejected','Descriptor ordering changes validity; no auto-reordering')
    report={'subject':'LC-EXP-002','source_archive_sha256':'1014aa4b0948ec04f0f859905a3af3dad35034368e5016300a7c29215079e9e8',
            'python_version':platform.python_version(),'platform':platform.platform(),
            'probes':observations,'passed':sum(x['pass'] for x in observations),
            'total':len(observations),'all_pass':all(x['pass'] for x in observations)}
    (ROOT/'results/pressure_run.json').write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps({'passed':report['passed'],'total':report['total'],'all_pass':report['all_pass']}))

if __name__=='__main__':main()
