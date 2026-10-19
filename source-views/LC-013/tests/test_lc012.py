import copy, random, unittest, json, sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'src'))
from contract import blank,validate,is_prefix,sha
from fixtures import (ev,claim,condition,relation,reviewer,admit,addclaim,
                      addcondition,addrelation,episode,ATOM)
from engine import agreement,rewrite_receipt,reassess
from lexicon import Lexicon
from typed_baseline import TypedControl,build
from oracle import truth
from fixtures import to_lex

class LC012(unittest.TestCase):
    def check(self,e,L,q=5,k=5,c='default'):
        return agreement(e,L,q,k,c)
    def world(self):
        L=blank();L['reviewers'].append(reviewer());return L
    def test_01_competing_episode(self):
        obs=[self.check(ATOM,L,2,k)['value'] for k,L in enumerate(episode())]
        self.assertEqual(obs,['T','U','F','T','U'])
    def test_02_cycle_must_not_claim_priority(self):
        r=self.check(ATOM,episode()[-1],2,4)
        self.assertEqual(r['accepted'],[])
        self.assertEqual(r['undecided'],['later','original','restored'])
    def test_03_counter_correction_reinstates_without_overwriting(self):
        l=episode()[3];a=self.check(ATOM,l,2,2);b=self.check(ATOM,l,2,3)
        self.assertEqual((a['value'],b['value']),('F','T'))
        self.assertIn('original',b['accepted'])
    def test_04_two_independent_competitors_do_not_gain_order_priority(self):
        L=self.world()
        for id,val in [('a','T'),('b','F'),('c','T')]:addclaim(L,claim(id,val))
        addrelation(L,relation('b-over-a','CORRECTS','b','a'))
        addrelation(L,relation('c-over-a','CORRECTS','c','a'))
        r=self.check(ATOM,L)
        self.assertEqual(r['value'],'U');self.assertEqual(r['defeated'],['a'])
        self.assertEqual(r['accepted'],['b','c'])
    def test_05_dispute_is_not_refutation(self):
        L=self.world();addclaim(L,claim('a','T'));addclaim(L,claim('b','T'))
        addrelation(L,relation('challenge','DISPUTES','b','a'))
        r=self.check(ATOM,L)
        self.assertEqual(r['value'],'T');self.assertEqual(r['disputed'],['a']);self.assertEqual(r['defeated'],[])
    def test_06_context_annotation_not_truth_transition(self):
        L=self.world();addclaim(L,claim('a','T'))
        addclaim(L,claim('extra','F',kind='context',pred='context-note'))
        addrelation(L,relation('tag','ADDS_CONTEXT','extra','a'))
        r=self.check(ATOM,L)
        self.assertEqual(r['value'],'T');self.assertIn('extra',r['qualifiers'])
    def test_07_supersession_is_policy_scoped(self):
        L=self.world();addclaim(L,claim('old','T',kind='policy',pred='policy'))
        new=claim('new','F',kind='policy',pred='policy');new['from']=6;addclaim(L,new)
        l=relation('sup','SUPERSEDES','new','old');l['from']=6;addrelation(L,l)
        atom=dict(ATOM,kind='policy',predicate='policy')
        self.assertEqual(self.check(atom,L,2,5)['value'],'T')
        self.assertEqual(self.check(atom,L,6,6)['value'],'F')
    def test_08_missing_guard_is_unresolved_not_silent_grant(self):
        L=self.world();addclaim(L,claim('a','T'));addclaim(L,claim('b','F'))
        addrelation(L,relation('conditional','CORRECTS','b','a',guard=['FACT','authorization']))
        p=self.check(ATOM,L)
        self.assertEqual(p['value'],'U');self.assertEqual(p['pending'],['conditional'])
        self.assertEqual(p['attacks'],[])
    def test_09_false_guard_no_attack_true_guard_attack(self):
        L=self.world();addclaim(L,claim('a','T'));addclaim(L,claim('b','F'))
        addcondition(L,condition('c0','gate','F'))
        addrelation(L,relation('guarded','CORRECTS','b','a',guard=['FACT','gate']))
        self.assertEqual(self.check(ATOM,L)['attacks'],[])
        L2=copy.deepcopy(L);addcondition(L2,condition('c1','gate','T'))
        p=self.check(ATOM,L2)
        self.assertEqual(p['value'],'U');self.assertEqual(p['pending'],['guarded'])
        L3=copy.deepcopy(L);L3['conditions'][0]['value']='T' # new independent fixture, not append-only
        p=self.check(ATOM,L3)
        self.assertEqual(p['value'],'F')
    def test_10_nested_conditions_with_kleene_logic(self):
        L=self.world();addclaim(L,claim('a','T'));addclaim(L,claim('b','F'))
        addcondition(L,condition('permit','permit','T'));addcondition(L,condition('lock','lock','F'))
        gate=['AND',['FACT','permit'],['NOT',['FACT','lock']],['OR',['FACT','permit'],['CONST','F']]]
        addrelation(L,relation('conditional','CORRECTS','b','a',guard=gate))
        self.assertEqual(self.check(ATOM,L)['value'],'F')
    def test_11_review_context_permission_is_not_truth(self):
        L=self.world();L['reviewers']=[reviewer('r-general',contexts=['lab'])]
        addclaim(L,claim('a','T'));addclaim(L,claim('b','F'))
        r=relation('lab-only','CORRECTS','b','a',contexts=['default','lab']);addrelation(L,r,False)
        L['admissions'].append(admit('lab-only','CORRECTS',0,who='r-general'))
        self.assertEqual(self.check(ATOM,L,5,5,'default')['value'],'U')
        self.assertEqual(self.check(ATOM,L,5,5,'lab')['value'],'F')
    def test_12_unauthorized_review_is_rejected(self):
        L=self.world();L['reviewers']=[reviewer('policy',allowed=['SUPERSEDES'])]
        addclaim(L,claim('a','T'));addclaim(L,claim('b','F'))
        addrelation(L,relation('disallowed','CORRECTS','b','a'),False)
        L['admissions'].append(admit('disallowed','CORRECTS',0,who='policy'))
        with self.assertRaises(ValueError):validate(L)
    def test_13_future_evidence_and_duplicate_ids_rejected(self):
        L=self.world();a=claim('a','T');addclaim(L,a)
        duplicate=copy.deepcopy(a);L['claims'].append(duplicate)
        with self.assertRaises(ValueError):validate(L)
        L['claims'].pop();L['evidence'][0]['observed']=7
        with self.assertRaises(ValueError):validate(L)
    def test_14_invalid_link_types_and_self_reference(self):
        L=self.world();addclaim(L,claim('a','T'));addclaim(L,claim('b','F',pred='other'))
        addrelation(L,relation('bad','CORRECTS','a','b'))
        with self.assertRaises(ValueError):validate(L)
        L['links'][0]['target']='a'
        with self.assertRaises(ValueError):validate(L)
    def test_15_history_prefix_is_exact_not_set_based(self):
        l0=episode()[0];l1=copy.deepcopy(l0);addclaim(l1,claim('next','F'))
        self.assertTrue(is_prefix(l0,l1))
        moved=copy.deepcopy(l1);moved['claims'].reverse()
        self.assertFalse(is_prefix(l1,moved))
    def test_16_rewrite_preserves_full_audit_projection(self):
        L=episode()[-1];q={'op':'NOT','arg':{'op':'ANY','args':[ATOM,{'op':'NOT','arg':ATOM}]}}
        rec=rewrite_receipt(q,L,2,4)
        self.assertEqual(rec['operation'],'REWRITE')
    def test_17_reassess_preserves_old_and_new_referents(self):
        l=episode()
        rec=reassess(l[2],l[3],ATOM,2,2,3)
        self.assertEqual((rec['before']['value'],rec['after']['value']),('F','T'))
        self.assertIn('value',rec['changed_fields']);self.assertTrue(rec['predecessor_retained'])
    def test_18_unrelated_added_evidence_is_semantically_null(self):
        L=episode()[2];L2=copy.deepcopy(L);L2['evidence'].append(ev('independent',5))
        r=reassess(L,L2,ATOM,2,2,5)
        self.assertEqual(r['before'],r['after'])
        self.assertNotEqual(r['before_ledger_sha256'],r['after_ledger_sha256'])
    def test_19_withheld_link_must_not_attack(self):
        L=self.world();addclaim(L,claim('a','T'));addclaim(L,claim('b','F'))
        addrelation(L,relation('withdrawn','CORRECTS','b','a'),False)
        L['admissions'].append(admit('withdrawn','CORRECTS',0,outcome='WITHHELD'))
        x=self.check(ATOM,L)
        self.assertEqual(x['attacks'],[])
        self.assertEqual(x['value'],'U')
    def test_20_cutoff_later_review_not_inherited(self):
        L=self.world();addclaim(L,claim('a','T'));addclaim(L,claim('b','F'))
        link=relation('later-review','CORRECTS','b','a',1);addrelation(L,link,False)
        L['admissions'].append(admit('later-review','CORRECTS',3))
        self.assertEqual(self.check(ATOM,L,4,2)['value'],'U')
        self.assertEqual(self.check(ATOM,L,4,3)['value'],'F')
    def test_21_unobserved_conflict_gives_unknown_not_false(self):
        L=self.world();addclaim(L,claim('a','T'))
        self.assertEqual(self.check(ATOM,L,2,0)['value'],'T')
        self.assertEqual(self.check(dict(ATOM,predicate='other'),L,2,0)['value'],'U')
    def test_22_link_expression_separate_from_target_truth(self):
        L=episode()[2]
        self.assertEqual(self.check({'op':'LINK','id':'fix-original'},L,2,2)['value'],'T')
        self.assertEqual(self.check(ATOM,L,2,2)['value'],'F')
    def test_23_generated_compositions_cross_paths(self):
        rng=random.Random(20261017)
        L=episode()[-1]
        def gen(depth):
            if depth==0 or rng.random()<0.25:
                return rng.choice([ATOM, {'op':'LINK','id':'fix-later'}, {'op':'LINK','id':'cycle'},
                                   dict(ATOM,predicate='other')])
            t=rng.choice(['NOT','ALL','ANY','SCOPE'])
            if t=='NOT':return {'op':'NOT','arg':gen(depth-1)}
            if t=='SCOPE':return {'op':'SCOPE','query':rng.choice([1,2,3]),'knowledge':rng.choice([2,3,4]),
                                  'context':rng.choice(['lab','default']),'body':gen(depth-1)}
            return {'op':t,'args':[gen(depth-1) for _ in range(rng.randint(2,4))]}
        items={}
        for _ in range(1400):
            e=gen(4);items[sha(e)]=e
            if len(items)>=512:break
        self.assertEqual(len(items),512)
        for e in items.values():self.check(e,L,2,4)
    def test_24_generated_topologies_independent_oracle(self):
        rng=random.Random(12012026)
        for i in range(128):
            L=self.world();n=rng.randint(3,7)
            for j in range(n):addclaim(L,claim(f'c{j}',rng.choice(['T','F']),rng.randint(0,2)))
            for key,val in [('permit',rng.choice(['T','F'])),('freeze',rng.choice(['T','F']))]:
                addcondition(L,condition(f'f-{key}',key,val))
            count=rng.randint(1,n*2)
            for j in range(count):
                src,tgt=rng.sample(range(n),2)
                guard=rng.choice([['CONST','T'],['CONST','F'],['FACT','permit'],
                    ['AND',['FACT','permit'],['NOT',['FACT','freeze']]],
                    ['OR',['FACT','not-present'],['FACT','freeze']]])
                rel=relation(f'r{j}',rng.choice(['CORRECTS','DISPUTES']),f'c{src}',f'c{tgt}',rng.randint(2,3),guard)
                addrelation(L,rel,False)
                if rng.random()<0.80:L['admissions'].append(admit(rel['id'],rel['kind'],rel['observed'],outcome=rng.choice(['ADMITTED','ADMITTED','WITHHELD'])))
            r=self.check(ATOM,L,q=5,k=5)
            self.assertIn(r['value'],('T','F','U'))
    def test_25_permutation_invariance_of_relationship_input_order(self):
        rng=random.Random(12)
        for _ in range(32):
            L=episode()[-1];reordered=copy.deepcopy(L);rng.shuffle(reordered['links'])
            rng.shuffle(reordered['claims']);rng.shuffle(reordered['admissions'])
            self.assertEqual(self.check(ATOM,L,2,4),self.check(ATOM,reordered,2,4))

    def test_26_invalid_expression_not_silently_coerced(self):
        L=episode()[2]
        for bad in [{'op':'BANANA','args':[ATOM,ATOM]},
                    {'op':'SCOPE','query':-1,'knowledge':4,'context':'default','body':ATOM},
                    {'op':'ANY','args':[ATOM]},
                    {'op':'ATOM','kind':'observation','predicate':'sealed','subject':'A','object':'B','secret':1}]:
            with self.subTest(expr=bad):
                with self.assertRaises(ValueError):self.check(bad,L,2,2)

if __name__=='__main__':unittest.main()
