"""No third-party dependencies. Deterministic withheld-composition and mutation suite."""
import itertools, json, random, sys, unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'src'))
from common import registry, EVIDENCE, details, digest
from interpreter_a import InterpreterA
from interpreter_b import InterpreterB
from baseline import TypedEvaluator, TRANSFER_TREE
from experiment import run_episode, prove_rewrite, verify_history

R=registry()['definitions']

class Conformance(unittest.TestCase):
    def setUp(self):
        self.a=InterpreterA(R)
        self.b=InterpreterB(R)

    def test_three_stage_episode_and_control(self):
        results=run_episode(save=False)
        self.assertEqual([x['three_valued_result'] for x in results['conclusions']],['U','T','F'])
        self.assertEqual([x['authorization'] for x in results['conclusions']],
                         ['not_established','established','not_established'])
        self.assertEqual(results['conclusions'][0]['unmet_conditions'][0]['reason'],'missing')
        self.assertEqual(results['conclusions'][2]['unmet_conditions'][0]['reason'],'observed')
        self.assertEqual(len(results['audit']),5)
        for idx in range(3):
            entry=results['audit'][idx]
            self.assertTrue(entry['semantic_reconstruction_agreement'])
            self.assertEqual(entry['full_evidence_log_digest'],digest(EVIDENCE))
            self.assertIn('interpreter_a',entry['reconstructions'])
            self.assertIn('interpreter_b',entry['reconstructions'])
        self.assertTrue(results['trace_verified'])
        self.assertTrue(results['accepted_rewrite']['valid'])
        self.assertFalse(results['rejected_rewrite']['valid'])
        # Stage 1 historical conclusion is intact when stage 2 changes.
        self.assertEqual(results['audit'][1]['output_conclusion']['three_valued_result'],'T')
        self.assertEqual(results['audit'][2]['output_conclusion']['three_valued_result'],'F')
        for stage in range(3):
            expected=TypedEvaluator().evaluate(TRANSFER_TREE,EVIDENCE,stage)
            self.assertEqual(self.a.evaluate('G1(A)',evidence=EVIDENCE,stage=stage),expected)
            self.assertEqual(self.b.evaluate('G1(A)',evidence=EVIDENCE,stage=stage),expected)

    def test_non_equivalence_and_scope(self):
        pairs=[
            ('!(&(S(A),P(A)))','|(!(S(A)),!(P(A)))',True),
            ('!(&(S(A),P(A)))','&(!(S(A)),P(A))',False),
            ('>(S(A),P(A))','>(P(A),S(A))',False),
            ('G1(A)','G2(A)',False),
            ('!(!(S(A)))','S(A)',True),
            ('>(S(A),P(A))','|(!(S(A)),P(A))',True),
        ]
        for first,second,expect in pairs:
            with self.subTest(first=first,second=second):
                proof=prove_rewrite(first,second,self.a,self.b)
                self.assertEqual(proof['valid'],expect)
                self.assertTrue(proof['checked']>0)
                if not expect: self.assertIn('witness',proof)

    def test_unknown_version_and_bad_grammar(self):
        invalid=['G9(A)','S()','&(S(A))','&(S(A),)','S(A) and P(A)','&(S(A),P(A)','S(A),P(A)',
                 '!S(A)','Z(A)','&(S(A),P(A),P(A))','!()','S(A$)','S(A))','S(S)','P(P)','S(G1)']
        for e in invalid:
            for interp in (self.a,self.b):
                with self.subTest(e=e,interp=type(interp).__name__):
                    with self.assertRaises(ValueError): interp.evaluate(e,valuation={})

    def test_conflicting_claims_do_not_become_false(self):
        e=EVIDENCE+[{'id':'E004','stage':2,'predicate':'S','entity':'A',
                     'value':'T','source':'conflicting seal observation'}]
        self.assertEqual(details(e,2,'S','A')['reason'],'conflict')
        for interp in (self.a,self.b):
            self.assertEqual(interp.evaluate('G1(A)',evidence=e,stage=2)['value'],'U')
        self.assertEqual(self.a.evaluate('G1(A)',evidence=EVIDENCE,stage=2)['value'],'F')

    def test_cache_evidence_invalidation_and_registry_freeze(self):
        a=InterpreterA(R, reuse=True, result_cache=True)
        self.assertEqual(a.evaluate('G1(A)',evidence=EVIDENCE[:1],stage=2)['value'],'U')
        self.assertEqual(a.evaluate('G1(A)',evidence=EVIDENCE[:2],stage=2)['value'],'T')
        self.assertEqual(a.evaluate('G1(A)',evidence=EVIDENCE,stage=2)['value'],'F')
        a.evaluate('G1(A)',evidence=EVIDENCE,stage=2)
        self.assertGreater(a.stats['result_cache_hits'],0)
        a.definitions['G1']['expression']='S({x})'
        with self.assertRaises(ValueError): a.evaluate('G1(A)',evidence=EVIDENCE,stage=1)
        cyc=dict(R)
        cyc['G1']={'expression':'G1({x})'}
        for cls in (InterpreterA,InterpreterB):
            with self.assertRaises(ValueError): cls(cyc).evaluate('G1(A)',valuation={})

    def test_audit_chain_detects_tampering(self):
        history=run_episode(save=False)['audit']
        history[1]['output_conclusion']['authorization']='not_established'
        self.assertFalse(verify_history(history))

    def test_independent_implementations_on_unseen_compositions(self):
        # Generator seeded and withheld from handwritten episode; assertions use an
        # independent tree oracle, not A or B as the expected-value oracle.
        random.seed(20261017)
        atoms=['S(A)','P(A)','S(B)','P(B)']
        def make(depth):
            if depth==0 or random.random()<0.3:
                return ('atom',random.choice(atoms))
            op=random.choice(('not','and','or','implies'))
            if op=='not':return (op,make(depth-1))
            return (op,make(depth-1),make(depth-1))
        def render(tree):
            if tree[0]=='atom':return tree[1]
            if tree[0]=='not':return '!('+render(tree[1])+')'
            return {'and':'&','or':'|','implies':'>'}[tree[0]]+'('+render(tree[1])+','+render(tree[2])+')'
        def independent_oracle(tree,values):
            kind=tree[0]
            if kind=='atom':return values[tree[1]]
            if kind=='not':return {'T':'F','F':'T','U':'U'}[independent_oracle(tree[1],values)]
            left=independent_oracle(tree[1],values)
            right=independent_oracle(tree[2],values)
            truth={
                'and':{'TT':'T','TU':'U','TF':'F','UT':'U','UU':'U','UF':'F','FT':'F','FU':'F','FF':'F'},
                'or': {'TT':'T','TU':'T','TF':'T','UT':'T','UU':'U','UF':'U','FT':'T','FU':'U','FF':'F'},
                'implies':{'TT':'T','TU':'U','TF':'F','UT':'T','UU':'U','UF':'U','FT':'T','FU':'T','FF':'T'},
            }
            return truth[kind][left+right]
        compositions=[make(3) for _ in range(220)]
        total=0
        for tree in compositions:
            e=render(tree)
            for truth_values in itertools.product('TUF',repeat=4):
                valuation=dict(zip(atoms,truth_values))
                expected=independent_oracle(tree,valuation)
                self.assertEqual(self.a.evaluate(e,valuation=valuation)['value'],expected)
                self.assertEqual(self.b.evaluate(e,valuation=valuation)['value'],expected)
                total+=1
        self.assertEqual(total,17820)

if __name__=='__main__':
    suite=unittest.defaultTestLoader.loadTestsFromTestCase(Conformance)
    outcome=unittest.TextTestRunner(verbosity=2).run(suite)
    (ROOT/'results'/'test_report.json').write_text(json.dumps({
        'ran':outcome.testsRun,'failures':len(outcome.failures),'errors':len(outcome.errors),
        'success':outcome.wasSuccessful(),'generated_compositions_not_sequestered':220,
        'valuation_checks':17820,'registry_digest':digest(registry())},indent=2)+'\n')
    sys.exit(0 if outcome.wasSuccessful() else 1)
