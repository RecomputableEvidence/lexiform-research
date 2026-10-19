"""LC-EXP-003 independent explicit negative tests plus withheld-shape seeded oracle.
Tests intentionally do not infer coverage from simple test case counts.
"""
import copy
import itertools
import json
import random
import sys
import unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'src'))
from evidence import EvidenceLedger, sha
from registry import FrozenDefinitions
from engine import EngineA,EngineB,projection
from baseline import TypedBaseline
from transitions import rewrite_receipt, reassess_receipt

ORIGINAL_MACROS=json.loads((ROOT/'spec/relational_registry_predecessor.json').read_text())['macros']

def e(i,atom,val='T',obs=0,begin=0,end=4,source='fixture'):
    return {'id':i,'atom':atom,'value':val,'observed_stage':obs,
            'valid_from':begin,'valid_until':end,'source':source,
            'persistence_policy':'bounded' if end is not None else 'open_asserted'}

class EvidenceBound(unittest.TestCase):
    def setUp(self):
        self.reg=FrozenDefinitions(ORIGINAL_MACROS)
        self.a=EngineA(self.reg)
        self.b=EngineB(self.reg)
    def compare(self,expr,ledger,q,k=None,expected=None):
        a=self.a.evaluate(expr,ledger,q,k)
        b=self.b.evaluate(expr,ledger,q,k)
        t=TypedBaseline(self.reg,True).evaluate(expr,ledger,q,k)
        self.assertEqual(projection(a),projection(b),expr)
        self.assertEqual(projection(a),projection(t),expr)
        if expected:self.assertEqual(a['value'],expected,expr)
        return a

    def test_temporal_validity_is_not_observation_recency(self):
        ledger=EvidenceLedger([e('PAST','R(A,B)',obs=0,begin=0,end=1),
                               e('CURRENT','R(B,C)',obs=2,begin=2,end=4)])
        x=self.compare('C(R(A,B),R(B,C))',ledger,2,2,'U')
        self.assertEqual(x['support']['R(A,B)']['reason'],'not_valid_at_query')
        self.assertEqual(x['support']['R(A,B)']['nonapplicable_ids'],['PAST'])
        self.assertEqual(x['support']['R(B,C)']['evidence_ids'],['CURRENT'])
        self.compare('C(R(A,B),R(B,C))',ledger,0,0,'U')
        extended=EvidenceLedger([e('PAST','R(A,B)',obs=0,begin=0,end=3),e('CURRENT','R(B,C)',obs=2,begin=2,end=4)])
        self.compare('C(R(A,B),R(B,C))',extended,2,2,'T')

    def test_query_time_vs_evidence_availability(self):
        retro=EvidenceLedger([e('RETRO','R(A,B)',obs=2,begin=0,end=4)])
        self.assertEqual(self.compare('R(A,B)',retro,0,0,'U')['support']['R(A,B)']['reason'],'not_yet_observed')
        r=self.compare('R(A,B)',retro,0,2,'T')
        self.assertEqual(r['support']['R(A,B)']['selected_records'][0]['observed_stage'],2)
        self.assertEqual(r['support']['R(A,B)']['query_stage'],0)
        self.assertEqual(r['knowledge_stage'],2)

    def test_latest_eligible_and_conflicting_observations(self):
        rows=[e('OLD','R(A,B)','T',0,0,5),e('NEW','R(A,B)','F',2,1,4)]
        self.compare('R(A,B)',EvidenceLedger(rows),1,1,'T')
        self.compare('R(A,B)',EvidenceLedger(rows),1,2,'F')
        self.compare('R(A,B)',EvidenceLedger(rows),4,2,'T')
        conflict=EvidenceLedger(rows+[e('DISSENT','R(A,B)','T',2,1,4)])
        got=self.compare('R(A,B)',conflict,1,2,'U')
        self.assertEqual(got['support']['R(A,B)']['reason'],'conflict')
        self.assertEqual(got['support']['R(A,B)']['evidence_ids'],['DISSENT','NEW'])

    def test_unknown_distinguished_from_false(self):
        self.compare('J(P(B),R(A,B))',EvidenceLedger([e('X','R(A,B)')]),0,0,'U')
        self.compare('J(P(B),R(A,B))',EvidenceLedger([e('X','R(A,B)'),e('Y','P(B)','F')]),0,0,'F')
        self.compare('J(P(B),R(A,B))',EvidenceLedger([e('X','R(A,B)'),e('Y','P(B)','U')]),0,0,'U')

    def test_invalid_evidence_ingress_rejected(self):
        good=e('X','R(A,B)')
        bad=[]
        for field,value in (('observed_stage',-1),('observed_stage',True),('observed_stage',1.0),
                            ('valid_from',-1),('valid_from',False),('valid_until',0),
                            ('valid_until',True),('value','M'),('atom','R(A,)'),('id',''),('source','')):
            row={**good,field:value};bad.append([row])
        bad.extend([[good,good],[{k:v for k,v in good.items() if k!='valid_until'}],
                    [[1]],['nonsense'],[{'id':'X','stage':0,'atom':'R(A,B)','value':'T'}]])
        for bundle in bad:
            with self.subTest(bundle=bundle),self.assertRaises(ValueError):EvidenceLedger(bundle)
        with self.assertRaises(ValueError):EvidenceLedger([good]).lookup('R(A,B)',-1,0)
        from evidence import EvidenceRecord
        with self.assertRaises(ValueError):EvidenceLedger([EvidenceRecord('FORGED','R(A,B)','T',-3,0,1,'fake','bounded')])
        with self.assertRaises(ValueError):EvidenceLedger([good]).lookup('R(A,B)',0,True)
        with self.assertRaises(ValueError):EvidenceLedger([{**good,'valid_until':None}])
        with self.assertRaises(ValueError):EvidenceLedger([{**good,'persistence_policy':'open_asserted'}])
        self.assertEqual(EvidenceLedger([{**good,'valid_until':None,'persistence_policy':'open_asserted'}]).lookup('R(A,B)',999,0)['value'],'T')

    def test_duplicate_id_wins_no_access(self):
        with self.assertRaisesRegex(ValueError,'duplicate'):
            EvidenceLedger([e('Z','R(A,B)','T'),e('Z','R(A,B)','F')])

    def test_stage_scope_and_reverse_relation_reject(self):
        ledger=EvidenceLedger([e('A','R(A,B)'),e('B','R(B,C)')])
        self.compare('R(B,A)',ledger,0,0,'U')
        self.compare('AT(0,C(R(A,B),R(B,C)))',ledger,1,1,'T')
        for src in ('C(R(A,B),R(C,B))','C(AT(0,R(A,B)),AT(1,R(B,C)))',
                    'J(P(Z),R(A,B))','R(B,A) R(A,B)','AT(-1,R(A,B))'):
            for engine in (self.a,self.b):
                with self.subTest(expr=src,engine=engine.__class__.__name__),self.assertRaises(ValueError):
                    engine.evaluate(src,ledger,1,1)

    def test_definition_identity_is_retained(self):
        rows=EvidenceLedger([e('A','R(A,B)'),e('B','R(B,C)'),e('P','P(B)')])
        a=self.compare('H1(A,B,C)',rows,0,0,'T')
        expanded=self.compare('C(R(A,B),R(B,C))',rows,0,0,'T')
        self.assertEqual(projection(a),projection(expanded))
        self.assertNotEqual(a['source_expression'],expanded['source_expression'])
        self.assertEqual(a['definition_lineage'][0]['name'],'H1')
        self.assertEqual(a['definition_lineage'][0]['version'],1)
        self.assertEqual(expanded['definition_lineage'],[])
        self.assertEqual(a['definition_registry_sha256'],expanded['definition_registry_sha256'])
        self.assertEqual(a['semantic_projection_sha256'],expanded['semantic_projection_sha256'])

    def test_unsupported_definition_version_rejected(self):
        for key,version in (('H1',0),('H2',-9),('H1',True),('H2','1')):
            altered=copy.deepcopy(ORIGINAL_MACROS);altered[key]['version']=version
            with self.assertRaises(ValueError):FrozenDefinitions(altered)
        changed=copy.deepcopy(ORIGINAL_MACROS)
        changed['H1']['expression']='R({a},{c})'
        with self.assertRaisesRegex(ValueError,'version/content'):
            FrozenDefinitions(changed)
        external=copy.deepcopy(ORIGINAL_MACROS)
        registry=FrozenDefinitions(external)
        external['H1']['expression']='R({a},{c})'
        rows=EvidenceLedger([e('A','R(A,B)'),e('B','R(B,C)')])
        self.assertEqual(EngineA(registry).evaluate('H1(A,B,C)',rows,0)['value'],'T')
        registry._defs['H1']['version']=99
        with self.assertRaisesRegex(ValueError,'registry changed'):
            EngineA(registry).evaluate('H1(A,B,C)',rows,0)

    def test_rewrite_assoc_semantic_equality_and_receipt(self):
        ledger=EvidenceLedger([e('ID1','R(A,B)'),e('ID2','R(B,C)','F'),e('ID3','R(C,D)')])
        old='C(C(R(A,B),R(B,C)),R(C,D))'
        receipt=rewrite_receipt(old,self.reg,ledger,0)
        self.assertEqual(receipt['successor_expression'],'C(R(A,B),C(R(B,C),R(C,D)))')
        self.assertEqual(receipt['type'],'REWRITE')
        self.assertEqual(receipt['projection_sha256'],sha(projection(self.a.evaluate(old,ledger,0))))
        self.compare(receipt['successor_expression'],ledger,0,0,'F')
        with self.assertRaises(ValueError):rewrite_receipt('R(A,B)',self.reg,ledger,0)

    def test_reassess_preserves_predecessor_and_rejects_id_reuse(self):
        before=EvidenceLedger([e('A','R(A,B)',end=3)])
        after=EvidenceLedger([e('A','R(A,B)',end=3),e('B','R(A,B)','F',2,2,4)])
        receipt,old,new=reassess_receipt('R(A,B)',self.reg,before,after,2,1,2)
        self.assertEqual((receipt['previous_value'],receipt['new_value']),('T','F'))
        self.assertEqual(receipt['added_ids'],['B'])
        self.assertEqual(old['support']['R(A,B)']['evidence_ids'],['A'])
        self.assertEqual(before.lookup('R(A,B)',2,1)['value'],'T')
        self.assertEqual(receipt['original_expression'],receipt['successor_expression'])
        replaced=EvidenceLedger([e('A','R(A,B)','F')])
        with self.assertRaises(ValueError):reassess_receipt('R(A,B)',self.reg,before,replaced,0,0,0)
        with self.assertRaisesRegex(ValueError,'append-only'):
            reassess_receipt('R(A,B)',self.reg,after,before,2,2,2)

    def test_cache_bound_to_query_knowledge_and_ledger(self):
        before=EvidenceLedger([e('A','R(A,B)',end=1)])
        after=EvidenceLedger([e('A','R(A,B)',end=1),e('B','R(A,B)','T',2,2,4)])
        self.assertEqual(self.a.evaluate('R(A,B)',before,0,0)['value'],'T')
        self.assertEqual(self.a.evaluate('R(A,B)',before,2,2)['value'],'U')
        self.assertEqual(self.a.evaluate('R(A,B)',after,2,2)['value'],'T')
        x=self.a.evaluate('R(A,B)',after,2,2)
        x['value']='F';x['support'].clear();x['definition_lineage'].append('forged')
        y=self.a.evaluate('R(A,B)',after,2,2)
        self.assertEqual(y['value'],'T')
        self.assertIn('R(A,B)',y['support'])
        self.assertEqual(y['definition_lineage'],[])
        self.assertGreater(self.a.stats['result_cache_hits'],0)

    def test_hash_cons_reuses_equivalent_substructure(self):
        rows=EvidenceLedger([e('A','R(A,B)'),e('B','R(B,C)')])
        self.a.evaluate('C(R(A,B),R(B,C))',rows,0,0)
        first=self.a.stats['graph_nodes_created']
        self.a.evaluate('J(P(B),C(R(A,B),R(B,C)))',rows,0,0)
        self.assertEqual(self.a.stats['graph_nodes_created'],first+2) # new guard atom + J node
        self.assertGreater(self.a.stats['result_cache_hits'],0)

    def test_randomized_novel_shapes_with_independent_oracle(self):
        # 128 independently sampled shapes; target truth is direct min of literal values,
        # not copied from either interpreter or the typed baseline.
        rng=random.Random(61026017);actual=set()
        for case in range(128):
            n=rng.randint(2,6);names=[f'X{i}' for i in range(n+1)]
            atoms=[f'R({names[i]},{names[i+1]})' for i in range(n)]
            vals=[rng.choice('TFU') for _ in atoms]
            evidence=[e(f'E{case}I{i}',atom,val,obs=0,begin=0,end=4) for i,(atom,val) in enumerate(zip(atoms,vals))]
            terms=atoms[:]
            # Varied random parenthesization, not only left-branch chains.
            while len(terms)>1:
                pos=rng.randrange(len(terms)-1)
                terms[pos:pos+2]=[f'C({terms[pos]},{terms[pos+1]})']
            expr=terms[0]
            if rng.choice((True,False)):
                guard=f'P({rng.choice(names)})';v=rng.choice('TFU')
                evidence.append(e(f'G{case}',guard,v));expr=f'J({guard},{expr})';vals.append(v)
            actual.add(expr)
            expected={-1:'F',0:'U',1:'T'}[min({'F':-1,'U':0,'T':1}[v] for v in vals)]
            self.compare(expr,EvidenceLedger(evidence),0,0,expected)
        self.assertGreaterEqual(len(actual),60)  # 65 distinct expression strings in seeded run

    def test_index_linear_candidate_visits_but_full_build_cost(self):
        n=64
        rows=EvidenceLedger([e(f'I{i}',f'R(N{i},N{i+1})') for i in range(n)])
        terms=[f'R(N{i},N{i+1})' for i in range(n)]
        while len(terms)>1:
            terms=[f'C({terms[i]},{terms[i+1]})' if i+1<len(terms) else terms[i] for i in range(0,len(terms),2)]
        expr=terms[0]
        self.a.reset_stats();self.b.reset_stats()
        x=self.compare(expr,rows,0,0,'T')
        self.assertEqual(self.a.stats['candidate_rows_examined'],n)
        self.assertEqual(self.b.stats['candidate_rows_examined'],n)
        self.assertEqual(rows.index_build_rows,n)
        with self.assertRaises(AttributeError):rows.digest='forged'
        with self.assertRaises(AttributeError):rows.records=()
        self.assertEqual(len(x['links']),n)

if __name__=='__main__':unittest.main()
