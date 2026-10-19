import unittest,random,copy,json
from dataclasses import asdict
from evidence import EvidenceLedger
from registry import FrozenDefinitions
from typed_audit import TypedAudit
from lazy_graph import select_witness
from persistent_ledger import AppendLedger,GENESIS,verify_transition,verify_full_replay
from selective_audit import SelectiveAudit,AuditHandle

DEF=FrozenDefinitions({'H1':{'version':1,'parameters':['a','b','c'],'expression':'C(R({a},{b}),R({b},{c}))'},'H2':{'version':2,'parameters':['a','b','c'],'expression':'J(P({b}),C(R({a},{b}),R({b},{c})))'}})
def row(i,atom,value='T',obs=0,valid_from=0,valid_until=30):
    return {'id':i,'atom':atom,'value':value,'observed_stage':obs,'valid_from':valid_from,
            'valid_until':valid_until,'source':'LC007-synthetic','persistence_policy':'bounded'}
def path(n):
    expr='';rows=[]
    for i in range(n):
        a,b=f'N{i}',f'N{i+1}';x,y=f'X{i}',f'Y{i}'
        part=f'CHOICE(C(R({a},{x}),R({x},{b})),C(R({a},{y}),R({y},{b})))'
        expr=part if not expr else f'C({expr},{part})'
        for j,(u,v) in enumerate(((a,x),(x,b),(a,y),(y,b))):
            rows.append(row(f'E{i}-{j}',f'R({u},{v})'))
    return expr,rows

class LC007Tests(unittest.TestCase):
    def test_chain_against_independent_replay(self):
        store=AppendLedger();prev=store.snapshot();trusted_ids=set()
        for i in range(160):
            new=store.append(row(f'id{i}',f'R(A,B)' if i%3==0 else 'R(B,C)',('T','F','U')[i%3],obs=i%5))
            proof=new.transition(prev)
            self.assertTrue(verify_transition(proof,prev.digest,prev.length,trusted_ids))
            trusted_ids.add(f'id{i}')
            prev=new
        self.assertTrue(verify_full_replay(prev.records_for_replay(),prev.digest))
        self.assertEqual(prev.length,160)

    def test_reject_forged_transition_and_tampered_rows(self):
        s=AppendLedger([row('a','R(A,B)')]);old=s.snapshot();now=s.append(row('b','R(A,B)','F'))
        cert=now.transition(old)
        for field,value in [('previous_tip','0'*64),('new_tip','0'*64),('new_length',100),('previous_length',100)]:
            fake=copy.deepcopy(cert);fake[field]=value
            self.assertFalse(verify_transition(fake,old.digest,old.length,{'a'}))
        fake=copy.deepcopy(cert);fake['new_records'][0]['value']='U'
        self.assertFalse(verify_transition(fake,old.digest,old.length,{'a'}))
        # A chain-consistent forged reuse of a historical ID still must fail.
        from persistent_ledger import step,DOMAIN
        forged=copy.deepcopy(cert);forged['new_records'][0]['id']='a'
        forged['new_tip']=step(old.digest,old.length,forged['new_records'][0])
        self.assertFalse(verify_transition(forged,old.digest,old.length,{'a'}))
        self.assertFalse(verify_transition(cert,old.digest,old.length,None))
        with self.assertRaisesRegex(ValueError,'duplicate'):
            s.append(row('a','R(A,B)'))
        with self.assertRaises(ValueError):s.append(row('bad','R(A,B)',obs=-1))
        self.assertEqual(s.snapshot().digest,now.digest)

    def test_old_snapshots_exclude_later_rows_and_backwards_rejected(self):
        store=AppendLedger([row('a','R(A,B)','T')]);first=store.snapshot()
        later=store.append(row('b','R(A,B)','F'))
        self.assertEqual(first.lookup('R(A,B)',0,0)['value'],'T')
        self.assertEqual(later.lookup('R(A,B)',0,0)['value'],'U')
        self.assertEqual(len(first.records_for_replay()),1)
        with self.assertRaisesRegex(ValueError,'non-append'):first.appended_since(later)
        with self.assertRaisesRegex(ValueError,'unrelated'):
            later.appended_since(AppendLedger(first.records_for_replay()).snapshot())
        with self.assertRaises(AttributeError):first.length=999

    def test_selection_parity_all_temporal_states(self):
        rng=random.Random(706)
        rows=[];store=AppendLedger();atoms=('R(A,B)','R(B,C)','S(A)','P(B)')
        for i in range(128):
            obs=rng.randrange(0,5);start=rng.randrange(0,5);end=start+rng.randrange(1,5)
            r=row(f'r{i}',rng.choice(atoms),rng.choice(('T','F','U')),obs,start,end)
            rows.append(r);snap=store.append(r)
            for _ in range(4):
                atom=rng.choice(atoms+('R(X,Z)',));q=rng.randrange(0,8);k=rng.randrange(0,6)
                self.assertEqual(snap.lookup(atom,q,k),EvidenceLedger(rows).lookup(atom,q,k))

    def test_full_graph_rebuild_parity_across_64_segment_append(self):
        expr,rows=path(64);store=AppendLedger(rows)
        a=SelectiveAudit(DEF,'A');b=SelectiveAudit(DEF,'B');oracle=TypedAudit(DEF)
        prior=None
        for i in range(5):
            if i:
                atom='R(Q,W)' if i==1 else 'R(N0,X0)' if i==2 else 'R(N63,X63)'
                s=store.append(row(f'UPDATE{i}',atom,'F'))
            else:s=store.snapshot()
            ra=a.evaluate(expr,s,0,0);rb=b.evaluate(expr,s,0,0)
            expected=oracle.evaluate(expr,EvidenceLedger(s.records_for_replay()),0,0)
            self.assertEqual(ra['root_id'],expected['root_id'])
            self.assertEqual(rb['root_id'],expected['root_id'])
            self.assertEqual(a.full_graph(ra['audit_handle'])['nodes'],expected['nodes'])
            self.assertEqual(b.full_graph(rb['audit_handle'])['nodes'],expected['nodes'])
            self.assertNotIn('nodes',ra)
            for x in (0,1,2**32,2**64-1):
                w=a.witness(ra['audit_handle'],x)
                ref=select_witness(expected,x)
                self.assertEqual({key:w[key] for key in ref},ref)
                self.assertEqual(b.witness(rb['audit_handle'],x)['evidence_ids'],ref['evidence_ids'])
            if prior:
                self.assertEqual(a.full_graph(prior['audit_handle'])['root_id'],prior['root_id'])
                self.assertEqual(a.witness(prior['audit_handle'],0)['root_id'],prior['root_id'])
                if i==1:self.assertEqual(a.last_receipt['nodes_recomputed'],0)
            prior=ra

    def test_truth_unchanged_evidence_identity_changes(self):
        expr='R(A,B)';s=AppendLedger([row('a','R(A,B)','T')]);e=SelectiveAudit(DEF)
        old=e.evaluate(expr,s.snapshot(),0)
        new=e.evaluate(expr,s.append(row('b','R(A,B)','T')),0)
        self.assertEqual(old['value'],new['value'])
        self.assertNotEqual(old['root_id'],new['root_id'])
        self.assertEqual(e.witness(old['audit_handle'],0)['evidence_ids'],['a'])
        self.assertEqual(e.witness(new['audit_handle'],0)['evidence_ids'],['a','b'])

    def test_no_stale_standing_future_observation(self):
        s=AppendLedger([row('a','R(A,B)','T',obs=0,valid_from=0,valid_until=1)]);e=SelectiveAudit(DEF)
        old=e.evaluate('R(A,B)',s.snapshot(),2,2)
        new=e.evaluate('R(A,B)',s.append(row('b','R(A,B)','T',obs=5,valid_from=2,valid_until=8)),2,2)
        self.assertEqual(old['value'],'U');self.assertEqual(new['value'],'U')
        self.assertEqual(e.last_receipt['nodes_recomputed'],0)
        with self.assertRaisesRegex(ValueError,'context'):
            e.evaluate('R(A,B)',s.snapshot(),2,5)

    def test_issued_handle_integrity_and_readonly_audit(self):
        s=AppendLedger([row('a','R(A,B)')]);e=SelectiveAudit(DEF)
        r=e.evaluate('R(A,B)',s.snapshot(),0)
        h=r['audit_handle']
        with self.assertRaises(ValueError):e.full_graph(AuditHandle('another',h.revision,h.root_id,h.ledger_digest,h.expression,h.query_stage,h.knowledge_stage,h.registry_digest))
        with self.assertRaises(ValueError):e.witness(h,-1)
        with self.assertRaises(ValueError):e.witness(h,1)
        g=e.full_graph(h);g['nodes'][h.root_id]['value']='F'
        self.assertEqual(e.full_graph(h)['nodes'][h.root_id]['value'],'T')
        w=e.witness(h,0);w['evidence_ids'].clear()
        self.assertEqual(e.witness(h,0)['evidence_ids'],['a'])

    def test_failed_append_remains_transactional(self):
        s=AppendLedger([row('a','R(A,B)')]);e=SelectiveAudit(DEF)
        good=e.evaluate('R(A,B)',s.snapshot(),0)
        other=AppendLedger([row('a','R(A,B)'),row('b','R(A,B)','F')])
        with self.assertRaisesRegex(ValueError,'unrelated'):
            e.evaluate('R(A,B)',other.snapshot(),0)
        self.assertEqual(e.evaluate('R(A,B)',s.snapshot(),0)['root_id'],good['root_id'])

    def test_random_append_stream_independent_full_graph(self):
        rng=random.Random(71177);expr,rows=path(5);s=AppendLedger(rows)
        e=SelectiveAudit(DEF);oracle=TypedAudit(DEF)
        e.evaluate(expr,s.snapshot(),0)
        atoms=[r['atom'] for r in rows]+['R(Q,W)']
        for i in range(128):
            s.append(row(f'rand{i}',rng.choice(atoms),rng.choice(('T','F','U'))))
            snap=s.snapshot();got=e.evaluate(expr,snap,0)
            expected=oracle.evaluate(expr,EvidenceLedger(snap.records_for_replay()),0)
            self.assertEqual(got['root_id'],expected['root_id'])
            if i%16==0:
                self.assertEqual(e.full_graph(got['audit_handle'])['nodes'],expected['nodes'])

if __name__=='__main__':unittest.main()
