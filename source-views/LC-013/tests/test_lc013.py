"""Post-inventory successor regression tests. These fixtures are not external truth evidence."""
import sys,unittest,copy
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'src'))
from fixtures import blank,claim,relation,reviewer,addclaim,addrelation,admit,ATOM,condition,addcondition
from engine import agreement,reassess

class ScopedRelationshipRegression(unittest.TestCase):
    def base(self):
        L=blank();L['reviewers'].append(reviewer());addclaim(L,claim('a','T'));return L
    def test_pending_dispute_is_not_a_pending_attack(self):
        L=self.base();addclaim(L,claim('b','T'));addrelation(L,relation('dis','DISPUTES','b','a'),False)
        r=agreement(ATOM,L,5,5)
        self.assertEqual(r['value'],'T');self.assertEqual(r['pending'],['dis'])
        L['admissions'].append(admit('dis','DISPUTES'))
        r=agreement(ATOM,L,5,5);self.assertEqual(r['value'],'T');self.assertEqual(r['disputed'],['a'])
    def test_pending_context_is_not_a_pending_attack(self):
        L=self.base();addclaim(L,claim('context','F',kind='context',pred='note'))
        addrelation(L,relation('ctx','ADDS_CONTEXT','context','a'),False)
        r=agreement(ATOM,L,5,5)
        self.assertEqual(r['value'],'T');self.assertEqual(r['pending'],['ctx'])
        L['admissions'].append(admit('ctx','ADDS_CONTEXT'))
        r=agreement(ATOM,L,5,5);self.assertEqual(r['value'],'T');self.assertIn('context',r['qualifiers'])
    def test_pending_correction_remains_conservative(self):
        L=self.base();addclaim(L,claim('b','T'));addrelation(L,relation('cor','CORRECTS','b','a'),False)
        r=agreement(ATOM,L,5,5);self.assertEqual(r['value'],'U');self.assertEqual(r['pending'],['cor'])
    def test_unrelated_context_has_no_targeted_projection_effect(self):
        L=self.base();addclaim(L,claim('b','T',pred='other'));addclaim(L,claim('c','T',kind='context',pred='note'))
        before=agreement(ATOM,L,5,5);addrelation(L,relation('unrelated','ADDS_CONTEXT','c','b'))
        after=agreement(ATOM,L,5,5);self.assertEqual(before,after)
        other=dict(ATOM,predicate='other')
        o=agreement(other,L,5,5);self.assertIn('c',o['qualifiers'])
    def test_unrelated_correction_guard_evidence_does_not_leak(self):
        L=self.base();addclaim(L,claim('b','T',pred='other'));addclaim(L,claim('c','T',pred='other'))
        addcondition(L,condition('flag','unrelated_guard','T'))
        before=agreement(ATOM,L,5,5)
        addrelation(L,relation('other_correction','CORRECTS','c','b',guard=['FACT','unrelated_guard']))
        after=agreement(ATOM,L,5,5)
        self.assertEqual(before,after)
    def test_reassess_keeps_old_snapshot_and_scoped_differences(self):
        a=self.base();b=copy.deepcopy(a)
        addclaim(b,claim('context','T',kind='context',pred='note'))
        addrelation(b,relation('r','ADDS_CONTEXT','context','a'),False)
        result=reassess(a,b,ATOM,5,5,5)
        self.assertEqual((result['before']['value'],result['after']['value']),('T','T'))
        self.assertEqual(result['after']['pending'],['r'])
        self.assertIn('pending',result['changed_fields'])
    def test_reversed_link_and_cutoff_still_bound(self):
        L=self.base();addclaim(L,claim('b','F'))
        addrelation(L,relation('c','CORRECTS','b','a'),False)
        L['admissions'].append(admit('c','CORRECTS',when=3))
        self.assertEqual(agreement(ATOM,L,5,2)['value'],'U')
        self.assertEqual(agreement(ATOM,L,5,3)['value'],'F')
if __name__=='__main__':unittest.main()
