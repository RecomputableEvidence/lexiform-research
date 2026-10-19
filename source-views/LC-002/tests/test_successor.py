"""Independent successor regression and relational-composition pressure suite."""
import itertools
import json
import random
import sys
import unittest
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'src'))
from interpreter_a import InterpreterA
from interpreter_b import InterpreterB
from relational_a import RelationalA
from relational_b import RelationalB
from common import EVIDENCE,registry

DEFS=registry()['definitions']
MACROS=json.loads((ROOT/'spec'/'relational_registry.json').read_text())['macros']
EXAMPLE=[
    {'id':'L001','atom':'R(A,B)','stage':0,'value':'T'},
    {'id':'L002','atom':'R(B,C)','stage':0,'value':'T'},
    {'id':'L003','atom':'P(B)','stage':0,'value':'F'},
    {'id':'L004','atom':'S(A)','stage':0,'value':'T'},
    {'id':'L005','atom':'R(A,B)','stage':1,'value':'F'},
    {'id':'L006','atom':'P(B)','stage':1,'value':'T'},
    {'id':'L007','atom':'R(B,C)','stage':2,'value':'F'},
    {'id':'L008','atom':'R(B,C)','stage':2,'value':'T'},
]

class Successor(unittest.TestCase):
    def setUp(self):
        self.a=RelationalA(MACROS)
        self.b=RelationalB(MACROS)

    def _compare(self,expr,evidence,stage,truth=None):
        a=self.a.reconstruct(expr,evidence,stage)
        b=self.b.reconstruct(expr,evidence,stage)
        for k in ('start','end','stage','value','support','links','guards','nodes'):
            self.assertEqual(a[k],b[k],f'{expr} {k} mismatch')
        for item in a['support']:
            self.assertIn(item,a['text'])
            self.assertIn(item,b['text'])
            for eid in a['support'][item]['evidence_ids']:
                self.assertIn(eid,a['text'])
                self.assertIn(eid,b['text'])
            self.assertIn(a['support'][item]['reason'],a['text'])
            self.assertIn(a['support'][item]['reason'],b['text'])
        if truth is not None:self.assertEqual(a['value'],truth,expr)
        return a

    def test_predecessor_a_cache_output_is_defensively_copied(self):
        a=InterpreterA(DEFS)
        x=a.evaluate('G1(A)',evidence=EVIDENCE,stage=1)
        x['value']='F';x['atoms'].append('S(Z)')
        y=a.evaluate('G1(A)',evidence=EVIDENCE,stage=1)
        self.assertEqual(y,{'value':'T','atoms':['P(A)','S(A)']})
        self.assertGreater(a.stats['result_cache_hits'],0)

    def test_predecessor_b_registry_is_bound_and_guarded(self):
        definitions=json.loads(json.dumps(DEFS))
        b=InterpreterB(definitions)
        self.assertEqual(b.evaluate('G1(A)',valuation={'S(A)':'T','P(A)':'F'})['value'],'F')
        definitions['G1']['expression']='S({x})'
        self.assertEqual(b.evaluate('G1(A)',valuation={'S(A)':'T','P(A)':'F'})['value'],'F')
        b.definitions['G1']['expression']='S({x})'
        with self.assertRaisesRegex(ValueError,'registry changed'):
            b.evaluate('G1(A)',valuation={'S(A)':'T','P(A)':'F'})

    def test_semantics_observed_history_and_cadence(self):
        cases=[
            ('H1(A,B,C)',0,'T'),('H2(A,B,C)',0,'F'),
            ('H1(A,B,C)',1,'F'),('H2(A,B,C)',1,'F'),
            ('J(P(B),R(B,C))',0,'F'),('J(P(B),R(B,C))',1,'T'),
            ('J(P(B),R(B,C))',2,'U'),
            ('AT(0,H1(A,B,C))',2,'T'),
            ('AT(0,H2(A,B,C))',2,'F'),
            ('AT(1,J(P(B),R(B,C)))',2,'T'),
            ('R(B,A)',0,'U'),
            ('R(A,B)',2,'F'),
            ('C(R(A,B),R(B,C))',2,'F'),
            ('J(S(A),C(R(A,B),R(B,C)))',0,'T'),
        ]
        for expr,stage,result in cases:
            with self.subTest(expr=expr,stage=stage):
                row=self._compare(expr,EXAMPLE,stage,result)
                self.assertEqual(row['stage'],int(expr.split('(')[1].split(',')[0]) if expr.startswith('AT(') else stage)
        self.assertEqual(self.a.evaluate('J(P(B),R(B,C))',EXAMPLE,2)['support']['R(B,C)']['reason'],'conflict')
        self.assertEqual(self.b.evaluate('J(P(B),R(B,C))',EXAMPLE,2)['support']['R(B,C)']['evidence_ids'],['L007','L008'])

    def test_mismatched_direction_scope_and_temporal_mix_fail_closed(self):
        disallowed=[
            'C(R(B,C),R(A,B))',
            'C(R(A,B),R(A,B))',
            'J(P(D),R(A,B))',
            'C(AT(0,R(A,B)),AT(1,R(B,C)))',
            'AT(0,C(AT(1,R(A,B)),R(B,C)))',
            'J(P(B),J(S(D),R(A,B)))',
        ]
        for expr in disallowed:
            for engine in (self.a,self.b):
                with self.subTest(expr=expr,engine=type(engine).__name__):
                    with self.assertRaises(ValueError):engine.evaluate(expr,EXAMPLE,2)

    def test_malformed_inputs_have_explicit_failure(self):
        disallowed=['','R(A)','R(A,)','R(A,B','R(A,B))','R(B,A)R(A,B)','AT(-1,R(A,B))',
                    'AT(01,R(A,B))','AT(x,R(A,B))','H3(A,B,C)', 'H1(A,B)',
                    'C(R(A,B),P(B))','J(R(A,B),R(B,C))', 'J(P(B),S(A))',
                    'R(3,B)','AT(0,S(A))','G1(A)','R(A,B$)','R(A B,C)', 'R(A, B C)', 'H1(A,B C,D)']
        for expr in disallowed:
            for engine in (self.a,self.b):
                with self.subTest(expr=expr,engine=type(engine).__name__):
                    with self.assertRaises(ValueError):engine.evaluate(expr,EXAMPLE,0)

    def test_boolean_stage_is_not_treated_as_integer(self):
        evidence=[{'id':'Q','atom':'R(A,B)','stage':True,'value':'T'}]
        self._compare('R(A,B)',evidence,1,'U')

    def test_registry_freezing_copy_and_cycle_detection(self):
        external=json.loads(json.dumps(MACROS))
        a=RelationalA(external);b=RelationalB(external)
        external['H1']['expression']='R({a},{c})'
        self.assertEqual(a.evaluate('H1(A,B,C)',EXAMPLE,0)['value'],'T')
        self.assertEqual(b.evaluate('H1(A,B,C)',EXAMPLE,0)['value'],'T')
        for engine in (a,b):
            engine.macros['H1']['expression']='R({a},{c})'
            with self.assertRaises(ValueError):engine.evaluate('H1(A,B,C)',EXAMPLE,0)
        cyclic=json.loads(json.dumps(MACROS))
        cyclic['H1']['expression']='H1({a},{b},{c})'
        for engine in (RelationalA(cyclic),RelationalB(cyclic)):
            with self.assertRaises(ValueError):engine.evaluate('H1(A,B,C)',EXAMPLE,0)

    def test_generated_unseen_compositions_oracle(self):
        # Fresh graph instances; expected values computed from an independently written
        # direct truth table, not from either source interpreter.
        rng=random.Random(261017)
        truth={'T':1,'U':0,'F':-1}
        counted=0
        variants=[]
        for _ in range(120):
            n=rng.choice((2,3))
            nodes=['A','B','C','D'][:n+1]
            linklist=[f'R({nodes[i]},{nodes[i+1]})' for i in range(n)]
            expr=linklist[0]
            for piece in linklist[1:]:expr=f'C({expr},{piece})'
            qual=rng.choice((None,'P(B)','S(A)'))
            if qual:expr=f'J({qual},{expr})'
            variants.append((expr,linklist,qual))
        for i,(expr,links,guard) in enumerate(variants):
            for combination in itertools.product(('T','F','U'),repeat=4):
                keys=['R(A,B)','R(B,C)','R(C,D)','P(B)']
                signals=dict(zip(keys,combination))
                signals['S(A)']='T'
                evidence=[{'id':f'Q{k:02}','stage':0,'atom':atom,'value':value}
                          for k,(atom,value) in enumerate(signals.items())]
                expected=min([truth[signals[x]] for x in links]+([truth[signals[guard]]] if guard else []))
                expected={v:k for k,v in truth.items()}[expected]
                got=self._compare(expr,evidence,0,expected)
                self.assertEqual(got['links'],links)
                self.assertEqual(got['guards'],[guard] if guard else [])
                counted+=1
        self.assertEqual(counted,9720)

    def test_scale_chain_32(self):
        nodes=[f'N{i}' for i in range(33)]
        expr=f'R({nodes[0]},{nodes[1]})'
        evidence=[]
        for i in range(32):
            atom=f'R({nodes[i]},{nodes[i+1]})'
            evidence.append({'id':f'X{i:02}','stage':0,'atom':atom,'value':'T'})
            if i>0:expr=f'C({expr},R({nodes[i]},{nodes[i+1]}))'
        out=self._compare(expr,evidence,0,'T')
        self.assertEqual(len(out['links']),32)
        self.assertEqual(out['start'],'N0')
        self.assertEqual(out['end'],'N32')

if __name__=='__main__':
    suite=unittest.defaultTestLoader.loadTestsFromTestCase(Successor)
    result=unittest.TextTestRunner(verbosity=2).run(suite)
    sys.exit(0 if result.wasSuccessful() else 1)
