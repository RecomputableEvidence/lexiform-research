import copy
import json
import random
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

from evidence import sha
from registry import FrozenDefinitions
from persistent_ledger import AppendLedger
from selective_audit import SelectiveAudit
from portable_audit import export_packet
from relational_audit import make_reassessment
from chain_audit import SCHEMA,build_chain,verify_chain,witness_comparison,step_commitment,genesis

ROOT=Path(__file__).resolve().parents[1]
DEFINITIONS=FrozenDefinitions({
 'H1':{'version':1,'parameters':['a','b','c'],'expression':'C(R({a},{b}),R({b},{c}))'},
 'H2':{'version':2,'parameters':['a','b','c'],'expression':'J(P({b}),C(R({a},{b}),R({b},{c})))'}
})

def row(i, atom='R(A,B)', value='T', obs=0, until=10):
    return dict(id=i,atom=atom,value=value,observed_stage=obs,valid_from=0,
                valid_until=until,source='synthetic',persistence_policy='bounded')

def packet(rows,expr='R(A,B)',q=0,k=0,indices=(0,)):
    snap=AppendLedger(rows).snapshot()
    engine=SelectiveAudit(DEFINITIONS)
    handle=engine.evaluate(expr,snap,q,k)['audit_handle']
    return export_packet(engine,handle,snap,DEFINITIONS,indices)

def setup_chain():
    a=packet([row('e0')])
    b=packet([row('e0'),row('e1')])
    c=packet([row('e0'),row('e1'),row('e2','R(A,B)','F')])
    d=packet([row('e0'),row('e1'),row('e2','R(A,B)','F'),row('e3','R(Z,Q)')])
    return (a,b,c,d),build_chain([make_reassessment(a,b),make_reassessment(b,c),make_reassessment(c,d)])

class ChainTests(unittest.TestCase):
    def test_reproduce_chained_transition(self):
        _,chain=setup_chain();result=verify_chain(chain)
        self.assertEqual([x['after_value'] for x in result['summary']],['T','U','U'])
        self.assertEqual([x['scalar_truth_changed'] for x in result['summary']],[False,True,False])
        self.assertEqual([x['appended_records'] for x in result['summary']],[1,1,1])
        self.assertTrue(result['verified']);self.assertEqual(result['step_count'],3)

    def test_identical_sample_index_changed_support(self):
        (_,b,_,_),ch=setup_chain()
        result=verify_chain(ch)
        first=result['summary'][0]['witness_sample']
        self.assertFalse(first['sample_order_changed'])
        self.assertFalse(first['sample_index_set_changed'])
        self.assertTrue(first['shared_sample_payload_changed'])
        self.assertTrue(first['shared_sample_evidence_ids_changed'])
        self.assertEqual(first['shared_sample_indices'],['0'])

    def test_unrelated_append_no_support_change(self):
        result=verify_chain(setup_chain()[1])
        last=result['summary'][2]['witness_sample']
        self.assertTrue(last['shared_sample_payload_changed'])  # external ledger commitment changed
        self.assertTrue(last['shared_sample_ledger_binding_changed'])
        self.assertFalse(last['shared_sample_content_changed'])
        self.assertFalse(last['shared_sample_evidence_ids_changed'])

    def test_synthetic_fork_valid_endpoints_rejected_in_sequence(self):
        (a,b,c,d),ch=setup_chain()
        alternative=make_reassessment(a,c)
        ch['steps'][1]['receipt']=alternative
        ch['steps'][1]['step_sha256']=step_commitment(1,ch['steps'][1]['prior_tip'],alternative['receipt_sha256'])
        with self.assertRaisesRegex(ValueError,'adjacent historical packet mismatch'):
            verify_chain(ch)

    def test_skipped_intermediate_packet_rejected(self):
        (_,_,_,d),ch=setup_chain()
        # A->B, C->D is not a continuous chain, although both are valid pair receipts.
        ch['steps'].pop(1)
        last=ch['steps'][1]
        last['ordinal']=1
        last['prior_tip']=ch['steps'][0]['step_sha256']
        last['step_sha256']=step_commitment(1,last['prior_tip'],last['receipt']['receipt_sha256'])
        ch['chain_tip']=last['step_sha256']
        with self.assertRaisesRegex(ValueError,'adjacent historical packet mismatch'):
            verify_chain(ch)

    def test_commitment_substitution_rejected(self):
        _,ch=setup_chain()
        altered=copy.deepcopy(ch);altered['steps'][1]['receipt']['after']['expected']['value']='T'
        with self.assertRaises(ValueError):verify_chain(altered)
        altered=copy.deepcopy(ch);altered['steps'][0]['step_sha256']='0'*64
        with self.assertRaisesRegex(ValueError,'step commitment mismatch'):verify_chain(altered)
        altered=copy.deepcopy(ch);altered['steps'][1]['prior_tip']='0'*64
        with self.assertRaisesRegex(ValueError,'predecessor commitment'):verify_chain(altered)

    def test_external_tip_scope(self):
        _,ch=setup_chain()
        res=verify_chain(ch,trusted_start_packet_hash=ch['start_packet_sha256'],trusted_chain_tip=ch['chain_tip'])
        self.assertTrue(res['commitment_matches']['supplied_whole_chain_tip'])
        self.assertEqual(res['anchor_origin'],'CALLER_SUPPLIED_NOT_INDEPENDENTLY_CHECKED')
        self.assertEqual(res['external_event_completeness'],'NOT_ESTABLISHED')
        with self.assertRaisesRegex(ValueError,'trusted chain tip mismatch'):
            verify_chain(ch,trusted_chain_tip='0'*64)
        with self.assertRaisesRegex(ValueError,'trusted start mismatch'):
            verify_chain(ch,trusted_start_packet_hash='0'*64)

    def test_reorder_and_duplicate_order_rejected(self):
        _,ch=setup_chain()
        x=copy.deepcopy(ch);x['steps'][0],x['steps'][1]=x['steps'][1],x['steps'][0]
        with self.assertRaisesRegex(ValueError,'step order'):verify_chain(x)
        x=copy.deepcopy(ch);x['steps'][2]['ordinal']=True
        with self.assertRaisesRegex(ValueError,'step order'):verify_chain(x)

    def test_sample_order_and_index_distinctions(self):
        expr='CHOICE(R(A,B),R(A,B))'
        a=packet([row('a')],expr,indices=(0,1))
        b=packet([row('a')],expr,indices=(1,0))
        c=packet([row('a')],expr,indices=(1,))
        d=witness_comparison(a,b)
        # The predecessor's export canonicalizes requested sample order.
        self.assertFalse(d['sample_order_changed']);self.assertFalse(d['sample_index_set_changed'])
        self.assertFalse(d['shared_sample_payload_changed'])
        e=witness_comparison(a,c)
        self.assertTrue(e['sample_index_set_changed'])
        self.assertFalse(e['shared_sample_payload_changed'])
        pair=make_reassessment(a,b)
        self.assertEqual(verify_chain(build_chain([pair]))['step_count'],1)

    def test_historical_step_chain_knowledge_change(self):
        rows=[row('late',obs=3)]
        a=packet(rows,k=0);b=packet(rows,k=3)
        c=packet(rows+[row('new',obs=3,value='F')],k=3)
        got=verify_chain(build_chain([make_reassessment(a,b),make_reassessment(b,c)]))
        self.assertEqual([x['after_value'] for x in got['summary']],['T','U'])
        self.assertEqual([x['appended_records'] for x in got['summary']],[0,1])

    def test_multi_episode_boundaries(self):
        a=packet([row('e')])
        r=make_reassessment(a,a)
        with self.assertRaisesRegex(ValueError,'step count'):
            build_chain([])
        with self.assertRaisesRegex(ValueError,'step count'):
            build_chain([r]*33)
        c=build_chain([r])
        x=copy.deepcopy(c);x['extra']='unbound'
        with self.assertRaisesRegex(ValueError,'chain keys'):verify_chain(x)

    def test_cli_cross_process_and_parser(self):
        _,ch=setup_chain()
        with tempfile.TemporaryDirectory(prefix='lc010-test-') as d:
            path=Path(d)/'chain.json';path.write_text(json.dumps(ch),encoding='utf-8')
            cmd=[sys.executable,str(ROOT/'verify_chain.py'),str(path),'--trusted-chain-tip',ch['chain_tip']]
            r=subprocess.run(cmd,text=True,capture_output=True,timeout=90)
            self.assertEqual(r.returncode,0,r.stderr)
            self.assertEqual(json.loads(r.stdout)['step_count'],3)
            path.write_text(json.dumps(ch)[:-1]+',"schema":"duplicate"}',encoding='utf-8')
            r=subprocess.run(cmd,text=True,capture_output=True,timeout=90)
            self.assertNotEqual(r.returncode,0)
            self.assertIn('duplicate JSON key',r.stderr)

    def test_seeded_three_snapshot_chains(self):
        rng=random.Random(1010)
        for n in range(64):
            a=packet([row(f'base{n}',value=rng.choice(['T','F','U']))])
            new1=row(f'first{n}',atom=rng.choice(['R(A,B)','R(Z,Q)']),value=rng.choice(['T','F','U']))
            b=packet([row(f'base{n}',value=a['ledger']['records'][0]['value']),new1])
            new2=row(f'second{n}',atom=rng.choice(['R(A,B)','R(Z,Q)']),value=rng.choice(['T','F','U']))
            c=packet([row(f'base{n}',value=a['ledger']['records'][0]['value']),new1,new2])
            result=verify_chain(build_chain([make_reassessment(a,b),make_reassessment(b,c)]))
            self.assertEqual(result['step_count'],2)
            self.assertEqual(result['final_packet_sha256'],c['packet_sha256'])
            self.assertEqual(result['summary'][0]['before_value'],a['expected']['value'])
            self.assertEqual(result['summary'][1]['after_value'],c['expected']['value'])
            self.assertEqual([x['appended_records'] for x in result['summary']],[1,1])

    def test_internal_consistency_does_not_prove_absence_of_earlier_events(self):
        (_,b,c,d), original=setup_chain()
        alternative=build_chain([make_reassessment(b,c),make_reassessment(c,d)])
        self.assertTrue(verify_chain(alternative)['verified'])
        self.assertNotEqual(original['start_packet_sha256'],alternative['start_packet_sha256'])
        self.assertNotEqual(original['chain_tip'],alternative['chain_tip'])
        self.assertEqual(verify_chain(alternative)['external_event_completeness'],'NOT_ESTABLISHED')

    def test_rehashed_valid_alternative_cannot_match_trusted_tip(self):
        (_,b,c,d),ch=setup_chain()
        replacement=build_chain([make_reassessment(b,c),make_reassessment(c,d)])
        self.assertTrue(verify_chain(replacement)['verified'])
        with self.assertRaisesRegex(ValueError,'trusted chain tip mismatch'):
            verify_chain(replacement,trusted_chain_tip=ch['chain_tip'])

if __name__=='__main__':unittest.main()
