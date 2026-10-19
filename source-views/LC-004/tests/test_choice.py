import json
import random
import unittest
from pathlib import Path
from evidence import EvidenceLedger
from registry import FrozenDefinitions
from engine import EngineA,EngineB
from choice_a import ChoiceA
from choice_b import ChoiceB
from choice_control import ChoiceTypedBaseline
from continuity import strict_reassess
from transitions import reassess_receipt
from expressivity import run as expressive_gap

REGISTRY_PATH=Path(__file__).resolve().parents[1]/'history_extracted'/'LC-EXP-003'/'spec'/'relational_registry_predecessor.json'

def row(i, atom, value='T', obs=0, start=0, end=10):
    return {'id':i,'atom':atom,'value':value,'observed_stage':obs,
            'valid_from':start,'valid_until':end,'source':'synthetic-structured-fixture',
            'persistence_policy':'bounded'}

def nest(branches, rng=None):
    terms=branches[:]
    while len(terms)>1:
        idx=0 if rng is None else rng.randrange(len(terms)-1)
        terms[idx:idx+2]=[f'CHOICE({terms[idx]},{terms[idx+1]})']
    return terms[0]

class ChoicePressure(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.reg=FrozenDefinitions(json.loads(REGISTRY_PATH.read_text())['macros'])
    def both(self,expr,ledger,q=0,k=None,expected=None):
        a=ChoiceA(self.reg).evaluate(expr,ledger,q,k)
        b=ChoiceB(self.reg).evaluate(expr,ledger,q,k)
        for key in ('value','start','end','stage','branches','winning_branch_indices','operator','registry_sha256','ledger_sha256'):
            self.assertEqual(a[key],b[key],key)
        c=ChoiceTypedBaseline(self.reg).evaluate(expr,ledger,q,k)
        for key in ('value','start','end','stage','branches','winning_branch_indices'):
            self.assertEqual(a[key],c[key],f'conventional comparator {key}')
        if expected is not None:self.assertEqual(a['value'],expected)
        return a

    def test_meet_only_expressivity_gap_is_real_but_scoped(self):
        gap=expressive_gap()
        self.assertEqual(len(gap['truth_table']),9)
        self.assertTrue(all(gap['counterexamples'].values()))
        # Old engines reject the candidate constructor: explicit evidence of grammar boundary.
        for engine in (EngineA(self.reg),EngineB(self.reg)):
            with self.assertRaises(ValueError):
                engine.evaluate('CHOICE(R(A,B),R(A,B))',EvidenceLedger([]),0)

    def test_all_truth_table_pairs_under_proposed_join_semantics(self):
        for a in 'FUT':
            for b in 'FUT':
                ledger=EvidenceLedger([row('EA','R(A,B)',a),row('EB','R(A,C)',b),
                                       row('EC','R(B,Z)'),row('ED','R(C,Z)')])
                expr='CHOICE(C(R(A,B),R(B,Z)),C(R(A,C),R(C,Z)))'
                expected=max((a,b),key='FUT'.index)
                result=self.both(expr,ledger,expected=expected)
                self.assertEqual(len(result['branches']),2)

    def test_temporal_standing_cannot_be_invented_by_choice(self):
        ledger=EvidenceLedger([row('XA','R(A,B)',end=1),row('XB','R(B,Z)',end=1),
                               row('YA','R(A,C)','F',obs=0,start=0,end=4),
                               row('YB','R(C,Z)','T',obs=0,start=0,end=4)])
        expr='CHOICE(C(R(A,B),R(B,Z)),C(R(A,C),R(C,Z)))'
        t0=self.both(expr,ledger,0,0,'T')
        t2=self.both(expr,ledger,2,2,'U')
        self.assertEqual(t2['branches'][0]['projection']['support']['R(A,B)']['reason'],'not_valid_at_query')
        self.assertNotEqual(t0['value'],t2['value'])

    def test_retain_all_branches_not_fictitious_combined_path(self):
        ledger=EvidenceLedger([row('AB','R(A,B)'),row('BZ','R(B,Z)'),
                               row('AC','R(A,C)','F'),row('CZ','R(C,Z)')])
        a=self.both('CHOICE(H1(A,B,Z),H1(A,C,Z))',ledger,expected='T')
        self.assertEqual(a['winning_branch_indices'],[0])
        self.assertEqual(a['branches'][0]['projection']['nodes'],['A','B','Z'])
        self.assertEqual(a['branches'][1]['projection']['nodes'],['A','C','Z'])
        self.assertEqual(len(a['branches'][0]['definition_lineage']),1)
        self.assertEqual(a['branches'][0]['definition_lineage'][0]['version'],1)

    def test_nested_unfamiliar_compositions(self):
        ledger=EvidenceLedger([row('AB','R(A,B)','F'),row('BZ','R(B,Z)'),
                               row('AC','R(A,C)','U'),row('CZ','R(C,Z)'),
                               row('AD','R(A,D)','T'),row('DZ','R(D,Z)'),
                               row('PD','P(D)','T')])
        leaves=['H1(A,B,Z)','H1(A,C,Z)','H2(A,D,Z)']
        left=nest(leaves)
        right=f'CHOICE({leaves[0]},CHOICE({leaves[1]},{leaves[2]}))'
        la=self.both(left,ledger,expected='T');ra=self.both(right,ledger,expected='T')
        self.assertEqual(la['branches'],ra['branches'])
        self.assertEqual(la['winning_branch_indices'],ra['winning_branch_indices'])

    def test_invalid_endpoint_and_stage_rejections(self):
        ledger=EvidenceLedger([row('A','R(A,B)'),row('B','R(B,Z)'),
                               row('C','R(A,C)'),row('D','R(C,X)')])
        for expr in ['CHOICE(R(A,B),R(B,Z))',
                     'CHOICE(C(R(A,B),R(B,Z)),C(R(A,C),R(C,X)))',
                     'CHOICE(AT(0,C(R(A,B),R(B,Z))),AT(1,C(R(A,B),R(B,Z))))',
                     'CHOICE(R(A,B))','CHOICE(R(A,B),)','CHOICE(R(A,B),R(A,B),R(A,B))',
                     'CHOICE(R(A,B),CHOICE(R(A,B)))']:
            for engine in (ChoiceA(self.reg),ChoiceB(self.reg)):
                with self.subTest(expr=expr,engine=type(engine).__name__):
                    with self.assertRaises(ValueError):engine.evaluate(expr,ledger,0,1)

    def test_reassessment_retain_both_results_and_branch_evidence(self):
        first=EvidenceLedger([row('A1','R(A,B)','F'),row('A2','R(B,Z)'),
                              row('B1','R(A,C)','F'),row('B2','R(C,Z)')])
        second=EvidenceLedger(first.records_as_dicts()+[row('NEW','R(A,C)','T',obs=2)])
        expr='CHOICE(C(R(A,B),R(B,Z)),C(R(A,C),R(C,Z)))'
        old=self.both(expr,first,0,0,'F')
        new=self.both(expr,second,0,2,'T')
        self.assertEqual(old['branches'][1]['projection']['support']['R(A,C)']['evidence_ids'],['B1'])
        self.assertEqual(new['branches'][1]['projection']['support']['R(A,C)']['evidence_ids'],['NEW'])
        self.assertNotEqual(old['ledger_sha256'],new['ledger_sha256'])
        self.assertEqual(old['source_expression'],new['source_expression'])
        self.assertEqual(old['branches'][1]['projection']['value'],'F')

    def test_reassessment_order_adversary_and_strict_successor(self):
        x=row('X','R(A,B)','T');y=row('Y','R(A,B)','F')
        old=EvidenceLedger([x,y]);reordered=EvidenceLedger([y,x])
        # Reproduce original acceptance without changing old code.
        previous,_old,_new=reassess_receipt('R(A,B)',self.reg,old,reordered,0,0,0)
        self.assertEqual(previous['added_ids'],[])
        self.assertNotEqual(old.digest,reordered.digest)
        with self.assertRaisesRegex(ValueError,'append-only identity/order'):
            strict_reassess('R(A,B)',self.reg,old,reordered,0,0,0)
        extended=EvidenceLedger([x,y,row('Z','R(A,B)','T',obs=1)])
        receipt,_,_=strict_reassess('R(A,B)',self.reg,old,extended,0,0,1)
        self.assertEqual(receipt['added_ids'],['Z'])
        with self.assertRaisesRegex(ValueError,'nondescending'):
            strict_reassess('R(A,B)',self.reg,old,extended,0,1,0)

    def test_seeded_unfamiliar_branch_structures(self):
        rng=random.Random(20261017)
        count=128;seen=set();covered=set()
        for ci in range(count):
            arms=rng.randint(2,6)
            rows=[];leaves=[];expected=[]
            for k in range(arms):
                via=f'N{k}'
                v1=rng.choice('FUT');v2=rng.choice('FUT')
                rows += [row(f'A{ci}R{k}',f'R(A,{via})',v1),row(f'A{ci}Z{k}',f'R({via},Z)',v2)]
                ev=[v1,v2]
                mode=rng.choice(('plain','guard','macro1','macro2'))
                if mode=='guard':
                    v3=rng.choice('FUT');rows.append(row(f'G{ci}S{k}',f'S({via})',v3))
                    leaves.append(f'J(S({via}),C(R(A,{via}),R({via},Z)))');ev.append(v3)
                elif mode=='macro2':
                    v3=rng.choice('FUT');rows.append(row(f'G{ci}P{k}',f'P({via})',v3))
                    leaves.append(f'H2(A,{via},Z)');ev.append(v3)
                elif mode=='macro1':leaves.append(f'H1(A,{via},Z)')
                else:leaves.append(f'C(R(A,{via}),R({via},Z))')
                expected.append(min(ev,key='FUT'.index))
            expression=nest(leaves,rng)
            seen.add(expression)
            expected_value=max(expected,key='FUT'.index)
            covered.add(expected_value)
            result=self.both(expression,EvidenceLedger(rows),expected=expected_value)
            self.assertEqual(len(result['branches']),arms)
        self.assertGreaterEqual(len(seen),100) # observed 113 distinct expressions in 128 seeded episodes
        self.assertEqual(covered,{'T','F','U'})

if __name__=='__main__':unittest.main()
