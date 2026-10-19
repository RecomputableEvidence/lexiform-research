"""Positive/negative semantic pressure. Oracle enumerates only modest finite instances."""
import copy,json,random,unittest,sys
from pathlib import Path
from lazy_graph import LazyGraph,select_witness
from typed_controls import TypedDP,EagerOracle
from typed_audit import TypedAudit
from evidence import EvidenceLedger
from registry import FrozenDefinitions
BASE=Path(__file__).resolve().parents[1]
DEFS=BASE/'history_003_extracted'/'LC-EXP-003'/'spec'/'relational_registry_predecessor.json'

def row(id,atom,value='T',obs=0,start=0,end=100):
    return {'id':id,'atom':atom,'value':value,'observed_stage':obs,'valid_from':start,
            'valid_until':end,'source':'LC-005-fixture','persistence_policy':'bounded'}

def example():
    expr='C(CHOICE(C(R(A,X),R(X,B)),C(R(A,Y),R(Y,B))),CHOICE(C(R(B,M),R(M,Z)),C(R(B,N),R(N,Z))))'
    rows=[row('AX','R(A,X)','T'),row('XB','R(X,B)','T'),
          row('AY','R(A,Y)','F'),row('YB','R(Y,B)','T'),
          row('BM','R(B,M)','U'),row('MZ','R(M,Z)','T'),
          row('BN','R(B,N)','T'),row('NZ','R(N,Z)','T')]
    return expr,EvidenceLedger(rows)

class LazyTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # See bundled LC-003 registry; exact fixture verified in predecessor suite.
        if not DEFS.exists():raise RuntimeError(f'missing predecessor registry {DEFS}')
        cls.registry=FrozenDefinitions(json.loads(DEFS.read_text())['macros'])
    def engines(self,expr,ledger,q=0,k=None,eager=True):
        lazy=LazyGraph(self.registry).evaluate(expr,ledger,q,k)
        typed=TypedDP(self.registry).evaluate(expr,ledger,q,k)
        for f in ('start','end','stage','value','histogram','witness_count','ledger_sha256','registry_sha256'):
            self.assertEqual(lazy[f],typed[f],f)
        audited=TypedAudit(self.registry).evaluate(expr,ledger,q,k)
        for f in ('start','end','stage','value','histogram','witness_count','root_id','nodes','ledger_sha256','registry_sha256'):
            self.assertEqual(lazy[f],audited[f],f'audit-equal comparator {f}')
        if eager:
            oracle=EagerOracle(self.registry).evaluate(expr,ledger,q,k)
            for f in ('start','end','stage','value','histogram','witness_count'):
                self.assertEqual(lazy[f],oracle[f],f)
            for i,w in enumerate(oracle['paths']):
                selected=select_witness(lazy,i)
                self.assertEqual((selected['nodes'],selected['value']),(w['nodes'],w['value']))
        return lazy

    def test_serial_choice_interleaving_four_distinct_witnesses(self):
        expr,ledger=example();r=self.engines(expr,ledger)
        self.assertEqual(r['witness_count'],4)
        self.assertEqual(r['histogram'],{'F':2,'U':1,'T':1})
        self.assertEqual(r['value'],'T')
        self.assertEqual([select_witness(r,i)['nodes'] for i in range(4)],
                         [['A','X','B','M','Z'],['A','X','B','N','Z'],
                          ['A','Y','B','M','Z'],['A','Y','B','N','Z']])

    def test_guard_on_universal_entity_and_guard_outside_choice(self):
        expr,ledger=example()
        enriched=EvidenceLedger(ledger.records_as_dicts()+[row('PB','P(B)','F'),row('PX','P(X)','T')])
        guarded=f'J(P(B),{expr})';r=self.engines(guarded,enriched)
        self.assertEqual(r['value'],'F')
        self.assertEqual(r['histogram'],{'F':4,'U':0,'T':0})
        for i in range(4):self.assertIn('PB',select_witness(r,i)['evidence_ids'])
        with self.assertRaisesRegex(ValueError,'guard|universal'):
            LazyGraph(self.registry).evaluate(f'J(P(X),{expr})',enriched,0)
        with self.assertRaisesRegex(ValueError,'guard|universal'):
            TypedDP(self.registry).evaluate(f'J(P(X),{expr})',enriched,0)

    def test_scope_temporal_expiry_and_knowledge_cutoff(self):
        expr,ledger=example()
        records=ledger.records_as_dicts()
        for r in records:r['valid_until']=1
        old=EvidenceLedger(records)
        self.assertEqual(self.engines(f'AT(0,{expr})',old,2,2)['value'],'T')
        at2=self.engines(f'AT(2,{expr})',old,0,2)
        self.assertEqual(at2['value'],'U')
        later=EvidenceLedger(records+[row('NEW','R(A,X)','T',obs=3,start=0,end=10)])
        q0=self.engines('R(A,X)',later,0,0)
        q3=self.engines('R(A,X)',later,0,3)
        self.assertEqual((q0['value'],q3['value']),('T','T'))
        self.assertNotEqual(select_witness(q0,0)['evidence_ids'],select_witness(q3,0)['evidence_ids'])

    def test_macro_source_identity_and_interpreter_reuse(self):
        expression='C(CHOICE(H1(A,B,C),H1(A,D,C)),R(C,Z))'
        ledger=EvidenceLedger([row('AB','R(A,B)'),row('BC','R(B,C)'),row('AD','R(A,D)','F'),
                               row('DC','R(D,C)'),row('CZ','R(C,Z)')])
        r=self.engines(expression,ledger)
        self.assertEqual(r['value'],'T')
        self.assertEqual(r['witness_count'],2)
        self.assertEqual(select_witness(r,0)['lineage'][0]['name'],'H1')
        self.assertEqual(select_witness(r,0)['lineage'][0]['version'],1)
        self.assertEqual(select_witness(r,1)['lineage'][0]['arguments'],['A','D','C'])
        self.assertEqual(r['source_expression'],expression)

    def test_invalid_endpoint_stage_and_arity_rejections(self):
        l=EvidenceLedger([])
        bad=['CHOICE(R(A,B),R(A,C))','C(R(A,B),R(C,D))',
             'C(AT(0,R(A,B)),AT(1,R(B,C)))','CHOICE(R(A,B),AT(1,R(A,B)))',
             'CHOICE(R(A,B))','R(A,B,C)','J(P(B),R(A,C))',
             'CHOICE(R(A,B),)','CHOICE(R(A,B),R(A,B),R(A,B))',
             'AT(-1,R(A,B))','R(a,B)','C(R(A,B),R(B,C)',
             'CHOICE(R(A,B),R(A,B)) trailing']
        for expr in bad:
            for engine in (LazyGraph(self.registry),TypedDP(self.registry)):
                with self.subTest(expr=expr,engine=type(engine).__name__):
                    with self.assertRaises(ValueError):engine.evaluate(expr,l,0)

    def test_known_three_value_exhaustive_scalar_algebra(self):
        for a in 'FUT':
            for b in 'FUT':
                ledger=EvidenceLedger([row('EA','R(A,B)',a),row('EB','R(B,C)',b),
                                       row('EC','R(A,C)',b)])
                r=self.engines('CHOICE(C(R(A,B),R(B,C)),R(A,C))',ledger)
                self.assertEqual(r['value'],max((min(a,b,key='FUT'.index),b),key='FUT'.index))

    def test_seeded_unfamiliar_interleaved_compositions(self):
        rng=random.Random(20261017);expressions=set();classes=set()
        for run in range(128):
            seg=rng.randint(1,5);parts=[];rows=[]
            for i in range(seg):
                a=f'N{i}';b=f'N{i+1}';left=f'X{i}';right=f'Y{i}'
                parts.append(f'CHOICE(C(R({a},{left}),R({left},{b})),C(R({a},{right}),R({right},{b})))')
                for side in (left,right):
                    rows.extend([row(f'ID{run}A{i}{side}',f'R({a},{side})',rng.choice('FUT')),
                                 row(f'ID{run}B{i}{side}',f'R({side},{b})',rng.choice('FUT'))])
            expression=parts[0]
            for part in parts[1:]:expression=f'C({expression},{part})'
            expressions.add(expression)
            r=self.engines(expression,EvidenceLedger(rows))
            classes.add(r['value'])
            self.assertEqual(r['witness_count'],2**seg)
        self.assertGreaterEqual(len(expressions),5)
        self.assertEqual(classes,set('FUT'))

    def test_exponential_witness_identity_with_bounded_graph_and_random_access(self):
        n=64;expr='';rows=[]
        for i in range(n):
            a=f'N{i}';b=f'N{i+1}'
            leaf=f'CHOICE(R({a},{b}),R({a},{b}))'
            expr=leaf if not expr else f'C({expr},{leaf})'
            rows.append(row(f'E{i}',f'R({a},{b})'))
        ledger=EvidenceLedger(rows)
        r=self.engines(expr,ledger,eager=False)
        self.assertEqual(r['witness_count'],2**64)
        self.assertEqual(r['histogram']['T'],2**64)
        self.assertLessEqual(len(r['nodes']),3*n)
        for i in (0,1,2**63,2**64-1):
            w=select_witness(r,i)
            self.assertEqual(len(w['nodes']),n+1)
            self.assertEqual(len(w['decisions']),n)
            self.assertEqual(w['value'],'T')
            self.assertEqual(len(set(w['evidence_ids'])),n)
        self.assertEqual(select_witness(r,0)['decisions'][-1]['arm'],0)
        self.assertEqual(select_witness(r,2**64-1)['decisions'][-1]['arm'],1)
        with self.assertRaises(ValueError):select_witness(r,2**64)
        with self.assertRaises(OverflowError):EagerOracle(self.registry).evaluate(expr,ledger,0,cap=4096)

    def test_mutation_does_not_corrupt_cache_and_new_evidence_invalidates(self):
        expr,ledger=example();g=LazyGraph(self.registry);g.reset_stats()
        one=g.evaluate(expr,ledger,0);one['nodes'].clear();one['histogram']['T']=12345
        another=g.evaluate(expr,ledger,0)
        self.assertEqual((another['value'],another['histogram']['T']),( 'T',1))
        self.assertEqual(g.stats['cache_hits'],1)
        altered=EvidenceLedger(ledger.records_as_dicts()+[row('FRESH','R(B,N)','F',obs=2)])
        after=g.evaluate(expr,altered,0,2)
        self.assertNotEqual(another['ledger_sha256'],after['ledger_sha256'])
        self.assertEqual(after['value'],'U')

    def test_distinct_branch_routes_exponentially_many_without_expansion(self):
        n=64;expr='';rows=[]
        for i in range(n):
            a=f'N{i}';b=f'N{i+1}';x=f'X{i}';y=f'Y{i}'
            segment=f'CHOICE(C(R({a},{x}),R({x},{b})),C(R({a},{y}),R({y},{b})))'
            expr=segment if not expr else f'C({expr},{segment})'
            for side in (x,y):
                rows.extend([row(f'EA{i}{side}',f'R({a},{side})'),row(f'EB{i}{side}',f'R({side},{b})')])
        ledger=EvidenceLedger(rows)
        result=self.engines(expr,ledger,eager=False)
        self.assertEqual(result['witness_count'],2**64)
        self.assertEqual(result['histogram'],{'F':0,'U':0,'T':2**64})
        self.assertLessEqual(len(result['nodes']),8*n)
        first=select_witness(result,0);last=select_witness(result,2**64-1)
        self.assertEqual(len(first['nodes']),2*n+1)
        self.assertEqual(len(last['nodes']),2*n+1)
        self.assertNotEqual(first['nodes'],last['nodes'])
        self.assertEqual(len(set(first['evidence_ids'])),2*n)
        self.assertEqual(len(set(last['evidence_ids'])),2*n)
        self.assertNotEqual(set(first['evidence_ids']),set(last['evidence_ids']))
        self.assertEqual(len(set(first['evidence_ids']) | set(last['evidence_ids'])),4*n)
        self.assertEqual(first['value'],last['value'])

    def test_invalid_history_cannot_become_append_only(self):
        from continuity import strict_reassess
        a=row('A','R(A,B)');b=row('B','R(A,B)','F')
        before=EvidenceLedger([a,b]);reordered=EvidenceLedger([b,a]);extended=EvidenceLedger([a,b,row('C','R(A,B)',obs=1)])
        with self.assertRaises(ValueError):strict_reassess('R(A,B)',self.registry,before,reordered,0,0,0)
        receipt,_,_=strict_reassess('R(A,B)',self.registry,before,extended,0,0,1)
        self.assertEqual(receipt['added_ids'],['C'])

if __name__=='__main__':unittest.main()

class TransitionPressure(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.registry=FrozenDefinitions(json.loads(DEFS.read_text())['macros'])
    def test_proven_distributive_rewrites_and_auditable_lineage(self):
        from transitions_005 import rewrite_receipt
        expr,ledger=example()
        left='C(CHOICE(C(R(A,X),R(X,B)),C(R(A,Y),R(Y,B))),R(B,M))'
        right='C(R(A,X),CHOICE(C(R(X,B),R(B,M)),C(R(X,B),R(B,M))))'
        for expression,rule in [
            (left,'CHAIN_CHOICE_LEFT'),
            ('C(R(A,X),CHOICE(R(X,B),R(X,B)))','CHAIN_CHOICE_RIGHT'),
            ('J(P(A),CHOICE(C(R(A,X),R(X,B)),C(R(A,Y),R(Y,B))))','GUARD_CHOICE'),
            ('AT(2,CHOICE(R(A,B),R(A,B)))','TIME_CHOICE')]:
            rows=ledger.records_as_dicts()
            if 'P(A)' in expression:rows.append(row('PAA','P(A)'))
            witness=rewrite_receipt(expression,rule,self.registry,EvidenceLedger(rows),2,2)
            self.assertEqual(witness['source_summary_sha256'],witness['target_summary_sha256'])
            self.assertNotEqual(witness['source'],witness['target'])
        with self.assertRaises(ValueError):rewrite_receipt('R(A,B)','CHAIN_CHOICE_LEFT',self.registry,ledger,0)
        # A graph stage mismatch must not be silently solved by distributivity.
        with self.assertRaises(ValueError):rewrite_receipt('C(CHOICE(R(A,B),AT(1,R(A,B))),R(B,C))',
                                                            'CHAIN_CHOICE_LEFT',self.registry,ledger,0)

    def test_context_bound_reassessment_retains_both_incompatible_histories(self):
        from transitions_005 import reassess_receipt
        x='CHOICE(C(R(A,B),R(B,Z)),C(R(A,C),R(C,Z)))'
        old=EvidenceLedger([row('AB','R(A,B)','F'),row('BZ','R(B,Z)'),
                            row('AC','R(A,C)','F'),row('CZ','R(C,Z)')])
        new=EvidenceLedger(old.records_as_dicts()+[row('AC2','R(A,C)','T',obs=2)])
        t=reassess_receipt(x,self.registry,old,new,0,0,2)
        self.assertEqual((t['previous']['value'],t['successor']['value']),('F','T'))
        self.assertTrue(t['interpretive_change'])
        self.assertEqual(t['added_evidence_ids'],['AC2'])
        self.assertNotEqual(t['previous']['ledger_sha256'],t['successor']['ledger_sha256'])
        self.assertNotEqual(t['previous']['root_id'],t['successor']['root_id'])
        with self.assertRaisesRegex(ValueError,'prefix'):
            reassess_receipt(x,self.registry,old,EvidenceLedger(new.records_as_dicts()[::-1]),0,0,2)
        with self.assertRaisesRegex(ValueError,'regression'):
            reassess_receipt(x,self.registry,old,new,0,3,2)
