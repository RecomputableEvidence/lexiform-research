import copy
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

from evidence import sha
from registry import FrozenDefinitions
from persistent_ledger import AppendLedger, GENESIS, DOMAIN
from selective_audit import SelectiveAudit
from portable_audit import export_packet,verify_packet

ROOT=Path(__file__).resolve().parents[1]
DEF=FrozenDefinitions({'H1':{'version':1,'parameters':['a','b','c'],
                             'expression':'C(R({a},{b}),R({b},{c}))'},
                       'H2':{'version':2,'parameters':['a','b','c'],
                             'expression':'J(P({b}),C(R({a},{b}),R({b},{c})))'}})


def row(i,atom,value='T',obs=0,valid_from=0,valid_until=10):
    return {'id':i,'atom':atom,'value':value,'observed_stage':obs,
            'valid_from':valid_from,'valid_until':valid_until,
            'source':'synthetic','persistence_policy':'bounded'}


def path(n):
    expression='';rows=[]
    for i in range(n):
        a,b=f'N{i}',f'N{i+1}';x,y=f'X{i}',f'Y{i}'
        part=f'CHOICE(C(R({a},{x}),R({x},{b})),C(R({a},{y}),R({y},{b})))'
        expression=part if not expression else f'C({expression},{part})'
        for j,(u,v) in enumerate(((a,x),(x,b),(a,y),(y,b))):
            rows.append(row(f'e{i}-{j}',f'R({u},{v})'))
    return expression,rows


def packet_for(rows=None,expr='R(A,B)'):
    s=AppendLedger(rows if rows is not None else [row('e1','R(A,B)')])
    snap=s.snapshot();engine=SelectiveAudit(DEF)
    evaluation=engine.evaluate(expr,snap,0,0)
    return export_packet(engine,evaluation['audit_handle'],snap,DEF,[0]),s,engine,evaluation


def resha(packet):
    packet['packet_sha256']=sha({k:v for k,v in packet.items() if k!='packet_sha256'})
    return packet


class PortabilityTests(unittest.TestCase):
    def test_single_revision_roundtrip_and_bound_anchor(self):
        p,_,_,_=packet_for()
        got=verify_packet(p,trusted_ledger_tip=p['ledger']['tip'])
        self.assertEqual(got['anchor_status'],'EXTERNALLY_ANCHORED')
        self.assertEqual(got['verified_witnesses'],1)
        self.assertEqual(verify_packet(p)['anchor_status'],'UNANCHORED')
        self.assertEqual(verify_packet(p,trusted_packet_hash=p['packet_sha256'])['anchor_status'],'EXTERNALLY_ANCHORED')

    def test_old_revision_remains_portable_after_append(self):
        s=AppendLedger([row('a','R(A,B)','T')]);old_snapshot=s.snapshot()
        e=SelectiveAudit(DEF);a=e.evaluate('R(A,B)',old_snapshot,0)
        new_snapshot=s.append(row('b','R(A,B)','F'))
        b=e.evaluate('R(A,B)',new_snapshot,0)
        old=export_packet(e,a['audit_handle'],old_snapshot,DEF,[0])
        new=export_packet(e,b['audit_handle'],new_snapshot,DEF,[0])
        self.assertNotEqual(old['ledger']['tip'],new['ledger']['tip'])
        self.assertEqual(old['expected']['value'],'T')
        self.assertEqual(new['expected']['value'],'U')
        self.assertNotEqual(old['expected']['root_id'],new['expected']['root_id'])
        self.assertTrue(verify_packet(old)['verified'])
        self.assertTrue(verify_packet(new)['verified'])

    def test_out_of_process_replay_without_live_handle(self):
        p,_,_,_=packet_for([row('a','R(A,B)','T'),row('b','R(A,B)','T')])
        with tempfile.TemporaryDirectory(prefix='lc008-offline-test-') as d:
            packet_file=Path(d)/'packet.json';packet_file.write_text(json.dumps(p))
            command=[sys.executable,str(ROOT/'verify_packet.py'),str(packet_file),'--trusted-tip',p['ledger']['tip']]
            r=subprocess.run(command,capture_output=True,text=True,timeout=60)
            self.assertEqual(r.returncode,0,r.stderr)
            self.assertEqual(json.loads(r.stdout)['root_id'],p['expected']['root_id'])

    def test_huge_symbolic_witness_count_four_sampled_paths(self):
        expr,rows=path(64);s=AppendLedger(rows);engine=SelectiveAudit(DEF)
        handle=engine.evaluate(expr,s.snapshot(),0)['audit_handle']
        indexes=[0,1,2**32,2**64-1]
        p=export_packet(engine,handle,s.snapshot(),DEF,indexes)
        self.assertEqual(p['expected']['witness_count_decimal'],str(2**64))
        self.assertEqual([w['index_decimal'] for w in p['witnesses']],[str(i) for i in indexes])
        result=verify_packet(p)
        self.assertGreaterEqual(result['graph_nodes'],500)
        self.assertEqual(result['verified_witnesses'],4)

    def test_guard_macro_and_temporal_context(self):
        expr='H2(A,B,C)'
        rows=[row('ab','R(A,B)'),row('bc','R(B,C)'),row('pb','P(B)')]
        s=AppendLedger(rows);e=SelectiveAudit(DEF);handle=e.evaluate(expr,s.snapshot(),0,0)['audit_handle']
        p=export_packet(e,handle,s.snapshot(),DEF,[0])
        self.assertTrue(verify_packet(p)['verified'])
        self.assertTrue(p['witnesses'][0]['witness']['lineage'])
        s2=AppendLedger([row('future','R(A,B)','T',obs=4,valid_from=0,valid_until=8)])
        e2=SelectiveAudit(DEF);h=e2.evaluate('R(A,B)',s2.snapshot(),0,0)['audit_handle']
        packet=export_packet(e2,h,s2.snapshot(),DEF,[0])
        self.assertEqual(packet['expected']['value'],'U')
        self.assertTrue(verify_packet(packet)['verified'])

    def test_reject_mutated_packet_contents(self):
        p,_,_,_=packet_for()
        bad=copy.deepcopy(p);bad['ledger']['records'][0]['value']='F'
        with self.assertRaisesRegex(ValueError,'content hash'):verify_packet(bad)
        bad=resha(bad)
        with self.assertRaisesRegex(ValueError,'chain replay'):verify_packet(bad)

    def test_reject_structurally_consistent_new_chain_with_stale_claim(self):
        p,_,_,_=packet_for()
        bad=copy.deepcopy(p)
        bad['ledger']['records'][0]['value']='F'
        from evidence import EvidenceRecord
        from dataclasses import asdict
        r=asdict(EvidenceRecord.build(bad['ledger']['records'][0]))
        bad['ledger']['tip']=sha({'domain':DOMAIN,'position':0,'previous':GENESIS,'record':r})
        bad['witnesses'][0]['witness']['ledger_commitment']=bad['ledger']['tip']
        resha(bad)
        with self.assertRaisesRegex(ValueError,'reconstructed audit differs'):verify_packet(bad)
        with self.assertRaisesRegex(ValueError,'external ledger tip mismatch'):
            verify_packet(bad,trusted_ledger_tip=p['ledger']['tip'])

    def test_reject_witness_forgery_even_after_hash_update(self):
        p,_,_,_=packet_for()
        bad=copy.deepcopy(p)
        bad['witnesses'][0]['witness']['evidence_ids']=['forged']
        resha(bad)
        with self.assertRaisesRegex(ValueError,'independent witness mismatch'):verify_packet(bad)

    def test_reject_duplicate_id_even_when_chain_recomputed(self):
        p,_,_,_=packet_for([row('a','R(A,B)'),row('b','R(A,B)')])
        bad=copy.deepcopy(p)
        bad['ledger']['records'][1]['id']='a'
        tip=GENESIS
        for i,r in enumerate(bad['ledger']['records']):
            tip=sha({'domain':DOMAIN,'position':i,'previous':tip,'record':r})
        bad['ledger']['tip']=tip
        resha(bad)
        with self.assertRaisesRegex(ValueError,'reused evidence identifier'):verify_packet(bad)

    def test_reject_invalid_claims_and_duplicate_indices(self):
        p,_,_,_=packet_for()
        bad=copy.deepcopy(p);bad['expected']['value']='F';resha(bad)
        with self.assertRaisesRegex(ValueError,'reconstructed audit differs'):verify_packet(bad)
        bad=copy.deepcopy(p);bad['witnesses'].append(copy.deepcopy(bad['witnesses'][0]));resha(bad)
        with self.assertRaisesRegex(ValueError,'duplicate witness index'):verify_packet(bad)
        bad=copy.deepcopy(p);bad['witnesses'][0]['index_decimal']='00';resha(bad)
        with self.assertRaisesRegex(ValueError,'noncanonical witness index'):verify_packet(bad)

    def test_snapshot_and_handle_misbinding_rejected(self):
        p,s,e,r=packet_for()
        h=r['audit_handle'];new=s.append(row('new','R(A,B)'))
        with self.assertRaisesRegex(ValueError,'historical ledger tip mismatch'):
            export_packet(e,h,new,DEF)
        with self.assertRaisesRegex(ValueError,'registry mismatch'):
            # Engine identity must match the originally supplied registry object.
            export_packet(e,h,s.snapshot(),FrozenDefinitions(DEF.get_definitions()))
        other=SelectiveAudit(DEF)
        with self.assertRaisesRegex(ValueError,'invalid or unknown audit handle'):
            export_packet(other,h,s.snapshot(),DEF)

    def test_unrelated_append_distinguishes_ledger_not_root(self):
        s=AppendLedger([row('a','R(A,B)')]);e=SelectiveAudit(DEF)
        snap0=s.snapshot();a=e.evaluate('R(A,B)',snap0,0)
        snap1=s.append(row('x','R(Z,Q)'))
        b=e.evaluate('R(A,B)',snap1,0)
        packet0=export_packet(e,a['audit_handle'],snap0,DEF)
        packet1=export_packet(e,b['audit_handle'],snap1,DEF)
        self.assertEqual(packet0['expected']['root_id'],packet1['expected']['root_id'])
        self.assertNotEqual(packet0['ledger']['tip'],packet1['ledger']['tip'])
        self.assertTrue(verify_packet(packet0)['verified'])
        self.assertTrue(verify_packet(packet1)['verified'])

    def test_verifier_independent_of_lc007_step_function(self):
        import persistent_ledger
        p,_,_,_=packet_for()
        old=persistent_ledger.step
        try:
            persistent_ledger.step=lambda *_: (_ for _ in ()).throw(RuntimeError('not independent'))
            self.assertTrue(verify_packet(p)['verified'])
        finally:persistent_ledger.step=old


    def test_consistent_fork_without_anchor_does_not_authenticate_history(self):
        original,_,_,_=packet_for([row('a','R(A,B)','T')])
        alternative,_,_,_=packet_for([row('a','R(A,B)','F')])
        # Both histories are internally reproducible, but they conflict. No packet alone
        # can establish which record was externally accepted or what happened physically.
        self.assertTrue(verify_packet(original)['verified'])
        self.assertTrue(verify_packet(alternative)['verified'])
        self.assertNotEqual(original['ledger']['tip'],alternative['ledger']['tip'])
        self.assertEqual(alternative['expected']['value'],'F')
        with self.assertRaisesRegex(ValueError,'external ledger tip mismatch'):
            verify_packet(alternative,trusted_ledger_tip=original['ledger']['tip'])

    def test_cross_process_duplicate_json_key_rejected(self):
        p,_,_,_=packet_for()
        with tempfile.TemporaryDirectory(prefix='lc008-json-test-') as d:
            target=Path(d)/'ambiguous.json'
            target.write_text(json.dumps(p)[:-1]+', "schema": "other"}')
            r=subprocess.run([sys.executable,str(ROOT/'verify_packet.py'),str(target)],
                             capture_output=True,text=True,timeout=60)
            self.assertNotEqual(r.returncode,0)
            self.assertIn('duplicate JSON key',r.stderr)

if __name__=='__main__':unittest.main()
