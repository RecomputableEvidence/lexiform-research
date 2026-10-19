"""Pressure fixtures for dependency-sensitive reuse; compare full audit DAGs."""
import copy,json,random,unittest,os
from pathlib import Path
from reuse import BoundReuse
from lazy_graph import LazyGraph,select_witness
from typed_audit import TypedAudit
from evidence import EvidenceLedger
from registry import FrozenDefinitions
ROOT=Path(__file__).resolve().parents[1]


def row(name,atom,value='T',obs=0,start=0,end=20):
    return {'id':name,'atom':atom,'value':value,'observed_stage':obs,
            'valid_from':start,'valid_until':end,'source':'LC-006 synthetic',
            'persistence_policy':'bounded'}


def branch_chain(n):
    parts=[];rows=[]
    for i in range(n):
        a,b=f'N{i}',f'N{i+1}';x,y=f'X{i}',f'Y{i}'
        parts.append(f'CHOICE(C(R({a},{x}),R({x},{b})),C(R({a},{y}),R({y},{b})))')
        for j,(u,v) in enumerate(((a,x),(x,b),(a,y),(y,b))):
            rows.append(row(f'E{i}p{j}',f'R({u},{v})'))
    expr=parts[0]
    for part in parts[1:]:expr=f'C({expr},{part})'
    return expr,rows

class ReuseTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        doc=json.loads((Path(os.environ['LC006_PREDECESSOR_ROOT'])/'history_003_extracted'/'LC-EXP-003'/'spec'/'relational_registry_predecessor.json').read_text())
        cls.reg=FrozenDefinitions(doc['macros'])

    def oracle_equal(self, expression, ledger, q, k, *engines):
        oracle=TypedAudit(self.reg).evaluate(expression,ledger,q,k)
        for e in engines:
            result=e.evaluate(expression,ledger,q,k)
            for field in ('value','start','end','stage','histogram','witness_count','root_id','nodes',
                          'ledger_sha256','registry_sha256','knowledge_stage'):
                self.assertEqual(result[field],oracle[field],(e.parser_identity,field))
        return oracle

    def test_frozen_predecessor_and_initial_full_parity(self):
        expr,records=branch_chain(5);ledger=EvidenceLedger(records)
        a=BoundReuse(self.reg,'A');b=BoundReuse(self.reg,'B')
        out=self.oracle_equal(expr,ledger,0,0,a,b)
        self.assertEqual(out['witness_count'],32)
        self.assertEqual(a.last_receipt['nodes_reused'],0)
        self.assertEqual(len(select_witness(out,31)['atoms']),10)

    def test_unrelated_append_zero_lookup_and_unchanged_root(self):
        expr,records=branch_chain(12)
        a,b=BoundReuse(self.reg,'A'),BoundReuse(self.reg,'B')
        base=self.oracle_equal(expr,EvidenceLedger(records),0,0,a,b)
        later=EvidenceLedger(records+[row('other','R(Q,W)','F')])
        new=self.oracle_equal(expr,later,0,0,a,b)
        self.assertEqual(new['root_id'],base['root_id'])
        self.assertNotEqual(new['ledger_sha256'],base['ledger_sha256'])
        for e in (a,b):
            self.assertEqual(e.last_receipt['lookup_calls'],0)
            self.assertEqual(e.last_receipt['nodes_recomputed'],0)
            self.assertEqual(e.last_receipt['nodes_reused'],len(e.plan['order']))

    def test_conflict_changes_witness_and_selective_dependencies(self):
        expr,records=branch_chain(16);a,b=BoundReuse(self.reg,'A'),BoundReuse(self.reg,'B')
        prior=self.oracle_equal(expr,EvidenceLedger(records),0,0,a,b)
        updated=EvidenceLedger(records+[row('new_conflict','R(N15,X15)','F')])
        new=self.oracle_equal(expr,updated,0,0,a,b)
        self.assertNotEqual(new['root_id'],prior['root_id'])
        self.assertEqual(new['value'],'T') # alternative true branch remains
        w=select_witness(new,0)
        self.assertEqual(w['value'],'U')
        self.assertIn('new_conflict',w['evidence_ids'])
        for e in (a,b):
            r=e.last_receipt
            self.assertEqual(r['lookup_calls'],1)
            self.assertGreater(r['nodes_recomputed'],1)
            self.assertLess(r['nodes_recomputed'],len(e.plan['order']))
        # Historical prior result is not rewritten.
        self.assertEqual(prior['value'],'T')
        self.assertEqual(select_witness(prior,0)['value'],'T')

    def test_future_observation_changes_ledger_not_selection(self):
        expr='R(A,B)';base=[row('e0','R(A,B)','T')]
        a,b=BoundReuse(self.reg,'A'),BoundReuse(self.reg,'B')
        old=self.oracle_equal(expr,EvidenceLedger(base),0,0,a,b)
        new=self.oracle_equal(expr,EvidenceLedger(base+[row('e1','R(A,B)','F',obs=4)]),0,0,a,b)
        self.assertEqual(old['root_id'],new['root_id'])
        for e in (a,b):
            self.assertEqual(e.last_receipt['lookup_calls'],1)
            self.assertEqual(e.last_receipt['nodes_recomputed'],0)
        # A new knowledge cutoff requires a separate evaluator.
        for e in (a,b):
            with self.assertRaisesRegex(ValueError,'context'):
                e.evaluate(expr,EvidenceLedger(base+[row('e1','R(A,B)','F',obs=4)]),0,4)

    def test_observation_scope_change_without_scalar_change(self):
        expr='R(A,B)';base=[row('a','R(A,B)','T',obs=0)]
        a,b=BoundReuse(self.reg,'A'),BoundReuse(self.reg,'B')
        old=self.oracle_equal(expr,EvidenceLedger(base),0,0,a,b)
        # Additional corroborating equal value at same observed stage changes support IDs.
        new=self.oracle_equal(expr,EvidenceLedger(base+[row('b','R(A,B)','T',obs=0)]),0,0,a,b)
        self.assertEqual(old['value'],new['value'])
        self.assertNotEqual(old['root_id'],new['root_id'])
        self.assertEqual(new['nodes'][new['root_id']]['evidence']['evidence_ids'],['a','b'])

    def test_reassess_expired_evidence_without_rewriting_prior(self):
        expr='R(A,B)';base=[row('expired','R(A,B)','T',obs=0,start=0,end=2)]
        a,b=BoundReuse(self.reg,'A'),BoundReuse(self.reg,'B')
        old=self.oracle_equal(expr,EvidenceLedger(base),3,3,a,b)
        self.assertEqual(old['value'],'U')
        later=EvidenceLedger(base+[row('new','R(A,B)','F',obs=3,start=3,end=8)])
        new=self.oracle_equal(expr,later,3,3,a,b)
        self.assertEqual(new['value'],'F')
        self.assertEqual(old['nodes'][old['root_id']]['evidence']['reason'],'not_valid_at_query')
        self.assertEqual(new['nodes'][new['root_id']]['evidence']['evidence_ids'],['new'])

    def test_macro_guard_at_nested_aliases_and_separate_stage(self):
        expr='AT(0,J(P(B),CHOICE(H1(A,B,C),H1(A,D,C))))'
        base=[row('ab','R(A,B)'),row('bc','R(B,C)'),row('ad','R(A,D)'),
              row('dc','R(D,C)'),row('guard','P(B)')]
        # Here guard B is not universally present in the second branch: must reject.
        for parse in ('A','B'):
            with self.assertRaisesRegex(ValueError,'guard'):
                BoundReuse(self.reg,parse).evaluate(expr,EvidenceLedger(base),0,0)
        expr='AT(0,J(P(A),CHOICE(H1(A,B,C),H1(A,D,C))))'
        a,b=BoundReuse(self.reg,'A'),BoundReuse(self.reg,'B')
        self.oracle_equal(expr,EvidenceLedger(base),3,3,a,b)
        more=EvidenceLedger(base+[row('pa','P(A)','T')])
        r=self.oracle_equal(expr,more,3,3,a,b)
        self.assertEqual(r['value'],'T')
        for e in (a,b):
            self.assertEqual(e.last_receipt['lookup_calls'],1)
            self.assertLess(e.last_receipt['nodes_recomputed'],len(e.plan['order']))

    def test_reordering_or_mutation_rejected(self):
        expr='C(R(A,B),R(B,C))';base=[row('a','R(A,B)'),row('b','R(B,C)')]
        for parse in ('A','B'):
            e=BoundReuse(self.reg,parse)
            e.evaluate(expr,EvidenceLedger(base),0)
            for invalid in ([base[1],base[0]],
                            [dict(base[0],value='F'),base[1]],
                            [base[0]]):
                with self.assertRaisesRegex(ValueError,'non-append'):
                    e.evaluate(expr,EvidenceLedger(invalid),0)
            # First result must still be usable; invalid updates do not mutate state.
            replay=e.evaluate(expr,EvidenceLedger(base),0)
            self.assertEqual(replay['value'],'T')

    def test_defensive_snapshot_and_history_receipts(self):
        expr='R(A,B)';base=EvidenceLedger([row('e0','R(A,B)')])
        e=BoundReuse(self.reg,'A');prior=e.evaluate(expr,base,0)
        prior['nodes'][prior['root_id']]['value']='F'
        nxt=e.evaluate(expr,base,0)
        self.assertEqual(nxt['value'],'T')
        self.assertEqual(nxt['nodes'][nxt['root_id']]['value'],'T')
        self.assertEqual(e.receipts[0]['mode'],'COLD')
        self.assertEqual(e.receipts[1]['mode'],'REPLAY')
        self.assertEqual(e.receipts[1]['before_ledger_sha256'],base.digest)

    def test_invalid_evidence_and_false_type_rejection(self):
        expr='R(A,B)'
        for change in ({'observed_stage':-1},{'valid_from':-1},{'id':'invalid!'},
                       {'value':'maybe'},{'valid_until':0}):
            data=row('e0','R(A,B)');data.update(change)
            with self.subTest(change=change),self.assertRaises(ValueError):EvidenceLedger([data])
        with self.assertRaises(ValueError):BoundReuse(self.reg,'A').evaluate(expr,EvidenceLedger([]),True)

    def test_seeded_append_parity_across_128_updates(self):
        rng=random.Random(61006);expr,records=branch_chain(7)
        a,b=BoundReuse(self.reg,'A'),BoundReuse(self.reg,'B')
        self.oracle_equal(expr,EvidenceLedger(records),0,0,a,b)
        atoms=[r['atom'] for r in records]
        for i in range(128):
            atom=rng.choice(atoms+['R(Q,W)'])
            val=rng.choice(('T','F','U'))
            records.append(row(f'new{i}',atom,val,obs=0))
            ledger=EvidenceLedger(records)
            result=self.oracle_equal(expr,ledger,0,0,a,b)
            self.assertEqual(result['ledger_sha256'],ledger.digest)

    def test_64_segment_reuse_preserves_exponential_identity(self):
        expr,records=branch_chain(64)
        engine=BoundReuse(self.reg,'A')
        prior=engine.evaluate(expr,EvidenceLedger(records),0)
        self.assertEqual(prior['witness_count'],2**64)
        self.assertEqual(len(prior['nodes']),511)
        newer=engine.evaluate(expr,EvidenceLedger(records+[row('unrelated','R(Q,W)')]),0)
        self.assertEqual(newer['root_id'],prior['root_id'])
        self.assertEqual(engine.last_receipt['lookup_calls'],0)
        self.assertEqual(len(newer['nodes']),511)
        self.assertNotEqual(select_witness(newer,0)['atoms'],select_witness(newer,2**64-1)['atoms'])

if __name__=='__main__':unittest.main()
