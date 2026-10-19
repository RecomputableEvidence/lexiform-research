"""Example receipt builder; replay uses preserved predecessor, no modification."""
from pathlib import Path
import sys,json,hashlib,zipfile,tempfile,subprocess
ROOT=Path(__file__).resolve().parent
ARCHIVE=ROOT/'history'/'LC-EXP-005-LAZY-COMPOSITION-001.zip'
with tempfile.TemporaryDirectory(prefix='lc006-demo-') as t:
    with zipfile.ZipFile(ARCHIVE) as z:z.extractall(t)
    pred=Path(t)/'LC-EXP-005-LAZY-COMPOSITION-001'
    subprocess.run([sys.executable,str(pred/'run_all.py')],cwd=pred,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL,check=True)
    sys.path[:0]=[str(pred/'history_003_extracted'/'LC-EXP-003'/'src'),str(pred/'src'),str(ROOT/'src')]
    from evidence import EvidenceLedger
    from registry import FrozenDefinitions
    from reuse import BoundReuse
    from typed_audit import TypedAudit
    defs=json.loads((pred/'history_003_extracted'/'LC-EXP-003'/'spec'/'relational_registry_predecessor.json').read_text())['macros']
    reg=FrozenDefinitions(defs)
    def row(i,atom,value='T'):
        return {'id':i,'atom':atom,'value':value,'observed_stage':0,'valid_from':0,'valid_until':10,
                'source':'LC006 demonstrative assertion (not attested)','persistence_policy':'bounded'}
    expr='C(CHOICE(C(R(A,X),R(X,B)),C(R(A,Y),R(Y,B))),R(B,Z))'
    initial=[row('AX','R(A,X)'),row('XB','R(X,B)'),row('AY','R(A,Y)'),row('YB','R(Y,B)'),row('BZ','R(B,Z)')]
    updates=[[],[row('UNRELATED','R(Q,W)')],[row('CORROBORATE','R(B,Z)')],[row('CHANGE','R(A,X)','F')]]
    selected=[];rows=list(initial)
    engine=BoundReuse(reg,'A')
    for ix,add in enumerate(updates):
        rows+=add;ledger=EvidenceLedger(rows)
        r=engine.evaluate(expr,ledger,0,0)
        typed=TypedAudit(reg).evaluate(expr,ledger,0,0)
        assert r['root_id']==typed['root_id'] and r['nodes']==typed['nodes']
        selected.append({'step':ix,'added_evidence_ids':[x['id'] for x in add],
                         'value':r['value'],'witness_histogram':r['histogram'],
                         'graph_nodes':len(r['nodes']),'transition':engine.last_receipt})
    destination=ROOT/'results'/'example_transitions.json'
    destination.write_text(json.dumps({'experiment':'LC-EXP-006-EXAMPLE-001',
        'claim_scope':'synthetic assertions / derived paths; no authenticating real-world evidence',
        'expression':expr,'snapshots':selected},indent=2)+'\n')
